import subprocess
import shutil
import os
import re

from botocore.exceptions import ClientError

from src.core.s3 import s3, BUCKET_NAME
from src.utils.logging_utils import setup_logger
from src.notifiers.redis_notifier import publish_progress

logger = setup_logger(__name__)


def extract_video_id(filename: str) -> str:
    """
    주어진 파일 경로에서 video ID(파일명에서 확장자를 제외한 값)를 추출합니다.
    예: "original/1234-abc.mp4" -> "1234-abc"
    """
    return filename.rsplit("/", 1)[-1].split(".")[0]


def get_duration(input_path: str) -> float:
    """
    ffprobe를 사용하여 영상의 총 재생 시간을 초 단위로 반환합니다.
    실패 시 fallback 값으로 1.0을 반환합니다.
    """
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        logger.warning(f"[Logic] ⚠️  Failed to get duration from ffprobe: {result.stdout}")
        return 1.0  # fallback to avoid division by zero


def transcode_video(filename: str) -> dict:
    """
    주어진 S3 비디오 파일을 HLS로 트랜스코딩하고,
    진행률을 실시간으로 Redis와 RabbitMQ로 전송하며,
    결과를 다시 S3에 저장합니다.

    Args:
        filename (str): S3의 원본 영상 경로 (예: original/1234-abc.mp4)

    Returns:
        void
    """

    logger.info(f"[Logic] Starting transcoding: {filename}")

    video_id = extract_video_id(filename)
    tmp_dir = f"/tmp/{video_id}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_path = os.path.join(tmp_dir, filename.rsplit("/", 1)[-1])
    output_dir = os.path.join(tmp_dir, "hls")
    os.makedirs(os.path.join(output_dir, "480p"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "1080p"), exist_ok=True)

    publish_progress(video_id, "in_progress", 0)

    try:
        try:
            with open(input_path, "wb") as f:
                s3.download_fileobj(BUCKET_NAME, filename, f)
            logger.info(f"📥  Downloaded {filename} to {input_path}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.warning(f"[Logic] ❌  S3 object not found: {filename}")
                publish_progress(video_id, "failed", 0)
            raise e

        duration = get_duration(input_path)

        if duration <= 1.0:
            logger.warning(f"[Logic] ⚠️  Video duration fallback to 1.0. May cause inaccurate progress reporting.")

        # FFmpeg HLS 변환
        output_m3u8 = os.path.join(output_dir, "output.m3u8")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-filter_complex", "[0:v]split=2[v1][v2];[v1]scale=w=854:h=480[v1out];[v2]scale=w=1920:h=1080[v2out]",
            "-map", "[v1out]", "-c:v:0", "libx264", "-b:v:0", "1400k",
            "-map", "a:0", "-c:a:0", "aac",
            "-f", "hls", "-hls_time", "10", "-hls_playlist_type", "vod",
            "-hls_segment_filename", os.path.join(output_dir, "480p", "segment_%03d.ts"),
            os.path.join(output_dir, "480p", "output.m3u8"),
            "-map", "[v2out]", "-c:v:1", "libx264", "-b:v:1", "5000k",
            "-map", "a:0", "-c:a:1", "aac",
            "-f", "hls", "-hls_time", "10", "-hls_playlist_type", "vod",
            "-hls_segment_filename", os.path.join(output_dir, "1080p", "segment_%03d.ts"),
            os.path.join(output_dir, "1080p", "output.m3u8")
        ]

        # Popen 으로 진행률 트래킹
        process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, universal_newlines=True)

        last_progress = -1
        # FFmpeg는 진행률을 stderr에 time=HH:MM:SS.ss 형식으로 출력함
        for line in process.stderr:
            match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if match:
                h, m, s = map(float, match.groups())
                seconds = h * 3600 + m * 60 + s
                progress = int(min(seconds / duration * 100, 100))
                # 진행 상황에 변동이 있을 때만 전송
                if progress > last_progress:
                    publish_progress(video_id, "in_progress", progress)
                    last_progress = progress

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, ffmpeg_cmd)

        logger.info("🎞️ FFmpeg to HLS conversion complete")

        renditions = {
            "480p": {
                "bandwidth": 1400000,
                "resolution": "854x480"
            },
            "1080p": {
                "bandwidth": 5000000,
                "resolution": "1920x1080"
            },
        }

        lines = ["#EXTM3U"]
        for label, props in renditions.items():
            lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={props['bandwidth']},RESOLUTION={props['resolution']}")
            lines.append(f"{label}/output.m3u8")

        master_m3u8 = "\n".join(lines)

        with open(os.path.join(output_dir, "master.m3u8"), "w", encoding="utf-8", newline="\n") as f:
            f.write(master_m3u8)


        # S3에 청크들 업로드
        s3_prefix = f"hls/{video_id}/"
        for root, _, files in os.walk(output_dir):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, output_dir)
                s3_key = f"{s3_prefix}{rel_path}"
                with open(local_path, "rb") as f:
                    s3.upload_fileobj(f, BUCKET_NAME, s3_key)
                logger.debug(f"📤  Uploaded segment: {s3_key}")

        logger.info(f"[Logic] ✅  Transcoding complete: s3://{BUCKET_NAME}/{s3_prefix}master.m3u8")
        publish_progress(video_id, "success", 100)

        success = True

        return {
            "videoId": video_id,
            "m3u8": f"{s3_prefix}master.m3u8",
            "status": "success",
            "progress": 100
        }

    except Exception as e:
        if not locals().get("success"):
            logger.exception(f"[Logic] ❌  Transcoding failed: {e}")
            publish_progress(video_id, "failed", 0)
        raise e

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.info(f"[Logic] 🧹  Cleaned up: {tmp_dir}")
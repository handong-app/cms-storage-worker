import subprocess
import logging
import shutil
import os

from src.core.s3 import s3, BUCKET_NAME

logger = logging.getLogger(__name__)


def transcode_video(filename: str) -> str:
    logger.info(f"[Logic] Starting transcoding: {filename}")

    video_id = filename.rsplit("/", 1)[-1].split(".")[0]
    tmp_dir = f"/tmp/{video_id}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_path = os.path.join(tmp_dir, filename.rsplit("/", 1)[-1])
    output_dir = os.path.join(tmp_dir, "hls")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # S3에서 원본 다운로드
        with open(input_path, "wb") as f:
            s3.download_fileobj(BUCKET_NAME, filename, f)
        logger.info(f"📥 Downloaded {filename} to {input_path}")

        # FFmpeg HLS 변환
        output_m3u8 = os.path.join(output_dir, "output.m3u8")
        ffmpeg_cmd = [
            "ffmpeg", "-y",  # 덮어쓰기 허용
            "-i", input_path,
            "-profile:v", "baseline", "-level", "3.0",
            "-start_number", "0",
            "-hls_time", "10", "-hls_list_size", "0", "-f", "hls",
            output_m3u8
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        logger.info("🎞️ FFmpeg to HLS conversion complete")

        # S3에 청크들 업로드
        s3_prefix = f"hls/{video_id}/"
        for root, _, files in os.walk(output_dir):
            for file in files:
                local_path = os.path.join(root, file)
                s3_key = s3_prefix + file
                with open(local_path, "rb") as f:
                    s3.upload_fileobj(f, BUCKET_NAME, s3_key)
                logger.debug(f"📤 Uploaded segment: {s3_key}")

        logger.info(f"[Logic] ✅ Transcoding complete: s3://{BUCKET_NAME}/{s3_prefix}output.m3u8")
        return f"{s3_prefix}output.m3u8"

    except Exception as e:
        logger.error(f"[Logic] ❌ Transcoding failed: {e}")
        raise

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.info(f"[Logic] 🧹 Cleaned up: {tmp_dir}")
from app.core.s3 import s3, BUCKET_NAME
from app.schemas.presigned_dto import UploadPresignedRequestDTO, DownloadPresignedRequestDTO, DownloadPresignedResponseDTO, UploadPresignedResponseDTO
from app.util.date_utils import get_seoul_timestamp


def generate_upload_presigned_url(dto: UploadPresignedRequestDTO) -> UploadPresignedResponseDTO:
    key = f"original/{int(get_seoul_timestamp())}-{dto.filename}"
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": dto.content_type,
        },
        ExpiresIn=dto.expires_in,
    )
    return UploadPresignedResponseDTO(presigned_url=url, key=key)

def generate_download_presigned_url(dto: DownloadPresignedRequestDTO) -> DownloadPresignedResponseDTO:
    url = url=s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET_NAME, "Key": dto.filename},
            ExpiresIn=dto.expires_in,
        )
    return DownloadPresignedResponseDTO(presigned_url=url)
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.presigned_dto import UploadPresignedRequestDTO, UploadPresignedResponseDTO, \
    DownloadPresignedResponseDTO, DownloadPresignedRequestDTO
from app.services.presigned_service import generate_upload_presigned_url, generate_download_presigned_url

presigned_router = APIRouter()

@presigned_router.post("/upload", response_model=UploadPresignedResponseDTO)
def create_upload_url(dto: UploadPresignedRequestDTO):
    try:
        res = generate_upload_presigned_url(dto)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {e}")

@presigned_router.get("/download", response_model=DownloadPresignedResponseDTO)
def get_download_url(dto: DownloadPresignedRequestDTO = Depends()):
    try:
        res = generate_download_presigned_url(dto)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {e}")
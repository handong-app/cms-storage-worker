from typing import Optional

from pydantic import BaseModel


class UploadPresignedRequestDTO(BaseModel):
    filename: str
    content_type: str
    expires_in: Optional[int] = 300


class DownloadPresignedRequestDTO(BaseModel):
    filename: str
    expires_in: Optional[int] = 300


class UploadPresignedResponseDTO(BaseModel):
    presigned_url: str
    key: str


class DownloadPresignedResponseDTO(BaseModel):
    presigned_url: str

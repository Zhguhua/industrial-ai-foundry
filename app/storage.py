from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import settings


@dataclass
class StoredObject:
    bucket: str
    object_name: str
    checksum: str
    size: int
    content_type: str | None

    @property
    def uri(self) -> str:
        return f"minio://{self.bucket}/{self.object_name}"


class ObjectStorage:
    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_document_bucket

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put_bytes(
        self,
        content: bytes,
        file_name: str,
        content_type: str | None = None,
    ) -> StoredObject:
        self.ensure_bucket()
        checksum = hashlib.sha256(content).hexdigest()
        suffix = Path(file_name).suffix.lower()
        object_name = f"sha256/{checksum[:2]}/{checksum}{suffix}"
        size = len(content)

        try:
            self.client.stat_object(self.bucket, object_name)
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                raise
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(content),
                size,
                content_type=content_type or "application/octet-stream",
            )

        return StoredObject(
            bucket=self.bucket,
            object_name=object_name,
            checksum=checksum,
            size=size,
            content_type=content_type,
        )

    def get_stream(self, storage_uri: str) -> tuple[BinaryIO, int, str | None]:
        prefix = f"minio://{self.bucket}/"
        if not storage_uri.startswith(prefix):
            raise ValueError("Unsupported or invalid storage URI")

        object_name = storage_uri[len(prefix):]
        stat = self.client.stat_object(self.bucket, object_name)
        response = self.client.get_object(self.bucket, object_name)
        return response, stat.size, stat.content_type


object_storage = ObjectStorage()

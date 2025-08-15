from contextlib import asynccontextmanager
import uuid

from aiobotocore.session import get_session
from fastapi import UploadFile


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file: UploadFile) -> str:
        unique_suffix = str(uuid.uuid4())
        object_name = f"{unique_suffix}_{file.filename}"

        contents = await file.read()

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=contents
            )

        return f"{self.config['endpoint_url'].rstrip('/')}/{self.bucket_name}/{object_name}"

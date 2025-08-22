import uuid
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from fastapi import UploadFile


class S3Client:
    """
    Асинхронный клиент для работы с S3-подобным хранилищем.

    Args:
        access_key (str): AWS Access Key.
        secret_key (str): AWS Secret Key.
        endpoint_url (str): URL S3-совместимого сервера.
        bucket_name (str): Название бакета.
    """

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
        """
        Асинхронный контекстный менеджер для S3 клиента.

        Usage:
            async with s3_client.get_client() as client:
                # работа с client
        """
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file: UploadFile) -> str:
        """
        Загружает файл в S3 и возвращает публичный URL.

        Args:
            file (UploadFile): Загружаемый файл FastAPI.

        Returns:
            str: Публичный URL загруженного файла.
        """
        unique_suffix = str(uuid.uuid4())
        object_name = f"{unique_suffix}_{file.filename}"

        contents = await file.read()

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=contents
            )

        return (
            f"{self.config['endpoint_url'].rstrip('/')}/"
            f"{self.bucket_name}/"
            f"{object_name}"
        )

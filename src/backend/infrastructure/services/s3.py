import io
import secrets
from dataclasses import dataclass, field

import aioboto3

from backend.config.settings import Settings


@dataclass
class S3Service:
    aws_endpoint_url: str = Settings().AWS_ENDPOINT_URL
    aws_key_id: str = Settings().AWS_KEY_ID
    aws_access_key: str = Settings().AWS_ACCESS_KEY
    bucket_name: str = "files"
    base_url: str = Settings().FILES_BASE_URL
    session: aioboto3.Session = field(default_factory=aioboto3.Session)

    async def upload_file(self, file_content: bytes, file_extension: str) -> str:
        async with self.session.client(
            service_name="s3",
            endpoint_url=self.aws_endpoint_url,
            aws_access_key_id=self.aws_key_id,
            aws_secret_access_key=self.aws_access_key,
        ) as s3:
            file_key_name = f"{secrets.token_hex(7)}.{file_extension.lower()}"
            file_io = io.BytesIO(file_content)
            await s3.upload_fileobj(file_io, self.bucket_name, file_key_name)
            return f"{self.base_url}/{file_key_name}"

    async def delete_file_from_url(self, file_url: str) -> None:
        if not file_url or not file_url.startswith(self.aws_endpoint_url):
            return

        try:
            file_key = file_url.split("/")[-1]
            async with self.session.client(
                service_name="s3",
                endpoint_url=self.aws_endpoint_url,
                aws_access_key_id=self.aws_key_id,
                aws_secret_access_key=self.aws_access_key,
            ) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=file_key)
        except Exception:
            pass

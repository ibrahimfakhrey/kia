import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid
import os


class S3Service:
    def __init__(self):
        self.s3_client = None

    def _get_client(self):
        if self.s3_client is None:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_S3_REGION']
            )
        return self.s3_client

    def upload_file(self, file, subject_id):
        """Upload a file to S3 and return the URL."""
        try:
            client = self._get_client()
            bucket = current_app.config['AWS_S3_BUCKET']

            # Generate unique filename
            ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            key = f"materials/{subject_id}/{unique_filename}"

            # Upload file
            client.upload_fileobj(
                file,
                bucket,
                key,
                ExtraArgs={'ContentType': file.content_type}
            )

            # Generate URL
            region = current_app.config['AWS_S3_REGION']
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

            return url
        except ClientError as e:
            current_app.logger.error(f"S3 upload error: {e}")
            return None

    def delete_file(self, file_url):
        """Delete a file from S3."""
        try:
            client = self._get_client()
            bucket = current_app.config['AWS_S3_BUCKET']

            # Extract key from URL
            key = file_url.split(f"{bucket}.s3.")[1].split(".amazonaws.com/")[1]

            client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            current_app.logger.error(f"S3 delete error: {e}")
            return False


s3_service = S3Service()

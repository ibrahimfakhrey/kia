from flask import current_app, url_for
import uuid
import os
from werkzeug.utils import secure_filename


class S3Service:
    """File upload service using local filesystem instead of AWS S3"""

    def upload_file(self, file, subject_id):
        """Upload a file to local uploads folder and return the URL."""
        try:
            # Get upload folder from config
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

            # Create subject folder if it doesn't exist
            subject_folder = os.path.join(upload_folder, 'materials', str(subject_id))
            os.makedirs(subject_folder, exist_ok=True)

            # Generate unique filename
            original_filename = secure_filename(file.filename)
            ext = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"

            # Full file path
            file_path = os.path.join(subject_folder, unique_filename)

            # Save file
            file.save(file_path)

            # Generate URL (relative path for serving)
            relative_path = f"materials/{subject_id}/{unique_filename}"
            url = f"/uploads/{relative_path}"

            return url
        except Exception as e:
            current_app.logger.error(f"File upload error: {e}")
            return None

    def delete_file(self, file_url):
        """Delete a file from local uploads folder."""
        try:
            # Extract relative path from URL
            # URL format: /uploads/materials/1/filename.pdf
            if not file_url.startswith('/uploads/'):
                return False

            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            relative_path = file_url.replace('/uploads/', '')
            file_path = os.path.join(upload_folder, relative_path)

            # Delete file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"File delete error: {e}")
            return False


s3_service = S3Service()

from app import s3, Config
from utils import validate_image
import uuid


def s3_image_upload(file):
    # Faz o upload da iamgem para o S3
    uuid_code = str(uuid.uuid4())
    filename = f'{uuid_code}-{file.filename.strip()}'
    validate_image(file)
    s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
    url = f"{Config.AWS_SS3_CUSTOM_DOMAIN}/{filename}"
    return url, filename

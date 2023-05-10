from app import s3, Config
from utils import validate_image
import uuid

def s3_image_upload(file, image):
    # Faz o upload da imagem para o S3
    bucket_file = 'wallpapers' if image == 'wallpaper' else 'avatars'
    uuid_code = str(uuid.uuid4())
    filename = f'{bucket_file}/{uuid_code}-{file.filename.strip()}'
    validate_image(file)
    print(file)
    s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
    url = f"{Config.AWS_S3_CUSTOM_DOMAIN}/{filename}"
    return url, filename
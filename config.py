from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Config:
    ENVIRONMENT = getenv('ENVIRONMENT')
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    CLIENT_URL = getenv(
        'CLIENT_URL') if ENVIRONMENT == 'prod' else 'http://localhost:5173'
    AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = getenv('AWS_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = getenv('AWS_S3_CUSTOM_DOMAIN')
    AWS_DEFAULT_ACL = getenv('AWS_DEFAULT_ACL')
    SIGHTENGINE_API = getenv('SIGHTENGINE_API')
    SIGHTENGINE_API_USER = getenv('SIGHTENGINE_API_USER')
    SIGHTENGINE_API_SECRET = getenv('SIGHTENGINE_API_SECRET')

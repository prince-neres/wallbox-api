from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = getenv('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    SPOTIFY_CLIENT_ID = getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = getenv('SPOTIFY_CLIENT_SECRET')

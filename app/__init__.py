from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from boto3 import client
from os import getenv


db = SQLAlchemy()
s3 = client('s3', aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)

    CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app

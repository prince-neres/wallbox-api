from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(10), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_updated = db.Column(db.DateTime, default=datetime.utcnow())


class Wallpaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False, default='')
    filename = db.Column(db.String(500), nullable=False, default='')
    tags = db.Column(ARRAY(db.String(50)), nullable=False, default=[])
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False, default=b'')
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_updated = db.Column(db.DateTime, default=datetime.utcnow())

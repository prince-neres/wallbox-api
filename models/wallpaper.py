from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


class Wallpaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False, default='')
    filename = db.Column(db.String(500), nullable=False, default='')
    tags = db.Column(ARRAY(db.String(50)), nullable=False, default=[])
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=False, default='')
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now())

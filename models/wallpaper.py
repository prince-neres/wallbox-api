from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from app import db


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    wallpaper_id = db.Column(db.Integer, db.ForeignKey('wallpaper.id'))


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
    favorites = db.relationship(
        'Favorite', backref='wallpaper', lazy='dynamic')
    downloads = db.Column(db.Integer, nullable=False, default=0)

    @property
    def favorite_count(self):
        return self.favorites.count()

    def increment_download(self):
        self.downloads += 1
        db.session.commit()

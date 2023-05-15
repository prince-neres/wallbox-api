from app import db


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    wallpaper_id = db.Column(db.Integer, db.ForeignKey('wallpaper.id'))

    def add_favorite(self):
        db.session.add(self)
        db.session.commit()

    def remove_favorite(self):
        db.session.delete(self)
        db.session.commit()

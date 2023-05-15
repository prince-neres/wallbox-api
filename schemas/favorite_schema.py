from marshmallow import Schema, fields


class FavoriteSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    wallpaper_id = fields.Int()

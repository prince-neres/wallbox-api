from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    image = fields.Str()
    date_created = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    date_updated = fields.DateTime(format='%Y-%m-%d %H:%M:%S')


class WallpaperSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)
    image = fields.Str(required=True)
    date_created = fields.DateTime(dump_only=True)
    date_updated = fields.DateTime(dump_only=True)

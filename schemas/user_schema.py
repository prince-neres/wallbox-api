from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    image = fields.Str()
    date_created = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    date_updated = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

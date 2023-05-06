from marshmallow import Schema, fields


class WallpaperSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)
    image = fields.Str(required=True)
    date_created = fields.DateTime(dump_only=True)
    date_updated = fields.DateTime(dump_only=True)

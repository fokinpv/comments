from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()


class CommentSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    parent_id = fields.Int()
    created_at = fields.String()
    updated_at = fields.String()
    text = fields.String()


class SnapshotSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    created_at = fields.String()
    xml_filepath = fields.String()

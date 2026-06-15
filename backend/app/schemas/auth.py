from marshmallow import fields, validate
from app.schemas.base import BaseSchema, EmailField


class RegisterSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = EmailField(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True,
    )


class LoginSchema(BaseSchema):
    email = EmailField(required=True)
    password = fields.Str(required=True, load_only=True)

from marshmallow import fields, validates, ValidationError
from app.schemas.base import BaseSchema


class CreateWorklogSchema(BaseSchema):
    hours = fields.Float(required=True)
    date = fields.Date(load_default=None, allow_none=True)
    note = fields.Str(load_default=None, allow_none=True)

    @validates("hours")
    def validate_hours(self, value):
        if value <= 0 or value > 24:
            raise ValidationError("hours must be between 0 (exclusive) and 24")

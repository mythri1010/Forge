from marshmallow import fields, validate, validates_schema, ValidationError
from app.schemas.base import BaseSchema


class CreateProjectSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(load_default=None, allow_none=True)
    start_date = fields.Date(load_default=None, allow_none=True)
    end_date = fields.Date(load_default=None, allow_none=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        s, e = data.get("start_date"), data.get("end_date")
        if s and e and e < s:
            raise ValidationError("end_date must be on or after start_date", "end_date")


class UpdateProjectSchema(BaseSchema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        s, e = data.get("start_date"), data.get("end_date")
        if s and e and e < s:
            raise ValidationError("end_date must be on or after start_date", "end_date")

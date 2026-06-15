from marshmallow import fields, validate
from app.schemas.base import BaseSchema


class CreateFeedbackSchema(BaseSchema):
    category = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    message = fields.Str(required=True, validate=validate.Length(min=1))


class UpdateFeedbackStatusSchema(BaseSchema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["OPEN", "REVIEWED", "CLOSED"]),
    )

    def load(self, data, **kwargs):
        if isinstance(data, dict) and "status" in data:
            data = {**data, "status": (data["status"] or "").upper()}
        return super().load(data, **kwargs)

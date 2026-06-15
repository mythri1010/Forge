from marshmallow import fields
from app.schemas.base import BaseSchema


class CreateLearningLogSchema(BaseSchema):
    summary = fields.Str(required=True)
    date = fields.Date(load_default=None, allow_none=True)
    task_id = fields.Int(load_default=None, allow_none=True)

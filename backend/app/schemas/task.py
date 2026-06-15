from marshmallow import fields, validate
from app.schemas.base import BaseSchema
from app.models.task import VALID_STATUSES, VALID_PRIORITIES

_status_list = sorted(VALID_STATUSES)
_priority_list = sorted(VALID_PRIORITIES)


class CreateTaskSchema(BaseSchema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    description = fields.Str(load_default=None, allow_none=True)
    priority = fields.Str(
        load_default="MEDIUM",
        validate=validate.OneOf(_priority_list),
    )
    assignee_id = fields.Int(load_default=None, allow_none=True)
    due_date = fields.Date(load_default=None, allow_none=True)

    def load(self, data, **kwargs):
        if isinstance(data, dict) and "priority" in data:
            data = {**data, "priority": (data["priority"] or "").upper()}
        return super().load(data, **kwargs)


class UpdateTaskSchema(BaseSchema):
    title = fields.Str(validate=validate.Length(min=1, max=300))
    description = fields.Str(allow_none=True)
    priority = fields.Str(validate=validate.OneOf(_priority_list))
    assignee_id = fields.Int(allow_none=True)
    due_date = fields.Date(allow_none=True)

    def load(self, data, **kwargs):
        if isinstance(data, dict) and "priority" in data:
            data = {**data, "priority": (data["priority"] or "").upper()}
        return super().load(data, **kwargs)


class ChangeStatusSchema(BaseSchema):
    to_status = fields.Str(
        required=True,
        validate=validate.OneOf(_status_list),
    )

    def load(self, data, **kwargs):
        if isinstance(data, dict) and "to_status" in data:
            data = {**data, "to_status": (data["to_status"] or "").upper()}
        return super().load(data, **kwargs)

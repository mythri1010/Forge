from marshmallow import fields, validate
from app.schemas.base import BaseSchema


class CreateGoalSchema(BaseSchema):
    goal_text = fields.Str(required=True, validate=validate.Length(min=1))
    week_start_date = fields.Date(required=True)


class SubmitReflectionSchema(BaseSchema):
    met_goal = fields.Bool(required=True)
    blockers = fields.Str(load_default=None, allow_none=True)
    process_notes = fields.Str(load_default=None, allow_none=True)
    perceived_helpfulness = fields.Int(
        load_default=None,
        allow_none=True,
        validate=validate.Range(min=1, max=5, error="perceived_helpfulness must be 1-5"),
    )

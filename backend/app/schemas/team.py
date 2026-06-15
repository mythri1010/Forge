from marshmallow import fields, validate
from app.schemas.base import BaseSchema

TEAM_ROLES = ("USER", "TEAM_ADMIN")


class CreateTeamSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))


class JoinTeamSchema(BaseSchema):
    invite_code = fields.Str(required=True, validate=validate.Length(min=1, max=64))


class UpdateMemberRoleSchema(BaseSchema):
    role_in_team = fields.Str(
        required=True,
        validate=validate.OneOf(TEAM_ROLES, error="role_in_team must be USER or TEAM_ADMIN"),
    )

    def load(self, data, **kwargs):
        # Normalise to upper before OneOf validation
        if isinstance(data, dict) and "role_in_team" in data:
            data = {**data, "role_in_team": (data["role_in_team"] or "").upper()}
        return super().load(data, **kwargs)

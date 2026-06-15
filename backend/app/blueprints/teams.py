from flask import Blueprint, request
from app.extensions import db
from app.models.team import Team, TeamMember
from app.schemas import CreateTeamSchema, JoinTeamSchema, UpdateMemberRoleSchema
from app.utils.auth import require_auth, require_team_member, require_team_admin
from app.utils.validation import validate_or_400
from app.utils.errors import bad_request, not_found, forbidden, ok

teams_bp = Blueprint("teams", __name__)


@teams_bp.post("")
@require_auth
def create_team(current_user):
    if current_user.team_id:
        return bad_request("You are already in a team")

    data, err = validate_or_400(CreateTeamSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    team = Team(name=data["name"])
    db.session.add(team)
    db.session.flush()

    membership = TeamMember(team_id=team.id, user_id=current_user.id, role_in_team="TEAM_ADMIN")
    current_user.role = "TEAM_ADMIN"
    db.session.add(membership)
    db.session.commit()
    return ok(team.to_dict(), 201)


@teams_bp.post("/join")
@require_auth
def join_team(current_user):
    if current_user.team_id:
        return bad_request("You are already in a team")

    data, err = validate_or_400(JoinTeamSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    team = Team.query.filter_by(invite_code=data["invite_code"]).first()
    if not team:
        return not_found("Team")

    membership = TeamMember(team_id=team.id, user_id=current_user.id, role_in_team="USER")
    db.session.add(membership)
    db.session.commit()
    return ok(team.to_dict(), 201)


@teams_bp.get("/me")
@require_team_member
def get_my_team(current_user):
    team = Team.query.get(current_user.team_id)
    return ok(team.to_dict()) if team else not_found("Team")


@teams_bp.get("/me/members")
@require_team_member
def get_team_members(current_user):
    members = TeamMember.query.filter_by(team_id=current_user.team_id).all()
    return ok([m.to_dict() for m in members])


@teams_bp.patch("/me/members/<int:user_id>/role")
@require_team_admin
def update_member_role(current_user, user_id):
    data, err = validate_or_400(UpdateMemberRoleSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    membership = TeamMember.query.filter_by(
        team_id=current_user.team_id, user_id=user_id
    ).first()
    if not membership:
        return not_found("Team member")

    membership.role_in_team = data["role_in_team"]
    membership.user.role = data["role_in_team"]
    db.session.commit()
    return ok(membership.to_dict())

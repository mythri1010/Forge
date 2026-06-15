from flask import Blueprint, request
from app.extensions import db
from app.models.weekly import WeeklyGoal, WeeklyReflection
from app.models.project import Project
from app.schemas import CreateGoalSchema, SubmitReflectionSchema
from app.utils.auth import require_team_member, assert_team_owns
from app.utils.validation import validate_or_400
from app.utils.pagination import paginate
from app.utils.errors import not_found, forbidden, ok

weekly_bp = Blueprint("weekly", __name__)


def _get_project_for_user(project_id, current_user):
    project = Project.query.get(project_id)
    if not project:
        return None, not_found("Project")
    if not assert_team_owns(project, current_user):
        return None, forbidden()
    return project, None


@weekly_bp.get("/goals/project/<int:project_id>")
@require_team_member
def list_goals(current_user, project_id):
    _, error = _get_project_for_user(project_id, current_user)
    if error:
        return error
    query = (
        WeeklyGoal.query
        .filter_by(project_id=project_id, team_id=current_user.team_id)
        .order_by(WeeklyGoal.week_start_date.desc())
    )
    return ok(paginate(query, lambda g: g.to_dict()))


@weekly_bp.post("/goals/project/<int:project_id>")
@require_team_member
def create_goal(current_user, project_id):
    _, error = _get_project_for_user(project_id, current_user)
    if error:
        return error

    data, err = validate_or_400(CreateGoalSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    goal = WeeklyGoal(
        project_id=project_id,
        team_id=current_user.team_id,
        week_start_date=data["week_start_date"],
        goal_text=data["goal_text"],
    )
    db.session.add(goal)
    db.session.commit()
    return ok(goal.to_dict(), 201)


@weekly_bp.get("/goals/<int:goal_id>/reflections")
@require_team_member
def list_reflections(current_user, goal_id):
    goal = WeeklyGoal.query.get(goal_id)
    if not goal:
        return not_found("Weekly goal")
    if goal.team_id != current_user.team_id:
        return forbidden()
    return ok([r.to_dict() for r in goal.reflections.all()])


@weekly_bp.post("/goals/<int:goal_id>/reflections")
@require_team_member
def submit_reflection(current_user, goal_id):
    goal = WeeklyGoal.query.get(goal_id)
    if not goal:
        return not_found("Weekly goal")
    if goal.team_id != current_user.team_id:
        return forbidden()

    data, err = validate_or_400(SubmitReflectionSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    reflection = WeeklyReflection(
        weekly_goal_id=goal_id,
        met_goal=data["met_goal"],
        blockers=data.get("blockers"),
        process_notes=data.get("process_notes"),
        perceived_helpfulness=data.get("perceived_helpfulness"),
    )
    db.session.add(reflection)
    db.session.commit()
    return ok(reflection.to_dict(), 201)

from flask import Blueprint, request
from app.extensions import db
from app.models.project import Project
from app.schemas import CreateProjectSchema, UpdateProjectSchema
from app.utils.auth import require_team_member, require_team_admin, assert_team_owns
from app.utils.validation import validate_or_400
from app.utils.pagination import paginate
from app.utils.errors import not_found, forbidden, ok

projects_bp = Blueprint("projects", __name__)


@projects_bp.get("")
@require_team_member
def list_projects(current_user):
    query = Project.query.filter_by(team_id=current_user.team_id).order_by(Project.created_at.desc())
    return ok(paginate(query, lambda p: p.to_dict()))


@projects_bp.post("")
@require_team_member
def create_project(current_user):
    data, err = validate_or_400(CreateProjectSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    project = Project(
        team_id=current_user.team_id,
        name=data["name"],
        description=data.get("description"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        created_by=current_user.id,
    )
    db.session.add(project)
    db.session.commit()
    return ok(project.to_dict(), 201)


@projects_bp.get("/<int:project_id>")
@require_team_member
def get_project(current_user, project_id):
    project = Project.query.get(project_id)
    if not project:
        return not_found("Project")
    if not assert_team_owns(project, current_user):
        return forbidden()
    return ok(project.to_dict())


@projects_bp.patch("/<int:project_id>")
@require_team_admin
def update_project(current_user, project_id):
    project = Project.query.get(project_id)
    if not project:
        return not_found("Project")
    if not assert_team_owns(project, current_user):
        return forbidden()

    data, err = validate_or_400(UpdateProjectSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    for field in ("name", "description", "start_date", "end_date"):
        if field in data:
            setattr(project, field, data[field])

    db.session.commit()
    return ok(project.to_dict())

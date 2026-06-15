from datetime import datetime, timezone
from flask import Blueprint, request
from app.extensions import db
from app.models.task import Task, TaskStatusHistory, VALID_STATUSES
from app.models.project import Project
from app.schemas import CreateTaskSchema, UpdateTaskSchema, ChangeStatusSchema
from app.utils.auth import require_team_member, assert_team_owns
from app.utils.validation import validate_or_400
from app.utils.pagination import paginate
from app.utils.errors import bad_request, not_found, forbidden, ok

tasks_bp = Blueprint("tasks", __name__)


def _get_project_for_user(project_id, current_user):
    project = Project.query.get(project_id)
    if not project:
        return None, not_found("Project")
    if not assert_team_owns(project, current_user):
        return None, forbidden()
    return project, None


@tasks_bp.get("/project/<int:project_id>")
@require_team_member
def list_tasks(current_user, project_id):
    _, error = _get_project_for_user(project_id, current_user)
    if error:
        return error

    query = Task.query.filter_by(project_id=project_id, team_id=current_user.team_id)

    if status := request.args.get("status"):
        query = query.filter(Task.status == status.upper())
    if assignee := request.args.get("assignee_id"):
        query = query.filter(Task.assignee_id == int(assignee))
    if priority := request.args.get("priority"):
        query = query.filter(Task.priority == priority.upper())

    query = query.order_by(Task.created_at.desc())
    return ok(paginate(query, lambda t: t.to_dict()))


@tasks_bp.post("/project/<int:project_id>")
@require_team_member
def create_task(current_user, project_id):
    _, error = _get_project_for_user(project_id, current_user)
    if error:
        return error

    data, err = validate_or_400(CreateTaskSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    task = Task(
        project_id=project_id,
        team_id=current_user.team_id,
        title=data["title"],
        description=data.get("description"),
        status="TODO",
        priority=data["priority"],
        created_by=current_user.id,
        assignee_id=data.get("assignee_id"),
        due_date=data.get("due_date"),
    )
    db.session.add(task)
    db.session.flush()

    db.session.add(TaskStatusHistory(
        task_id=task.id,
        from_status=None,
        to_status="TODO",
        changed_by=current_user.id,
    ))
    db.session.commit()
    return ok(task.to_dict(), 201)


@tasks_bp.get("/<int:task_id>")
@require_team_member
def get_task(current_user, task_id):
    task = Task.query.get(task_id)
    if not task:
        return not_found("Task")
    if not assert_team_owns(task, current_user):
        return forbidden()
    return ok(task.to_dict())


@tasks_bp.patch("/<int:task_id>")
@require_team_member
def update_task(current_user, task_id):
    task = Task.query.get(task_id)
    if not task:
        return not_found("Task")
    if not assert_team_owns(task, current_user):
        return forbidden()

    data, err = validate_or_400(UpdateTaskSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    for field in ("title", "description", "priority", "assignee_id", "due_date"):
        if field in data:
            setattr(task, field, data[field])

    db.session.commit()
    return ok(task.to_dict())


@tasks_bp.post("/<int:task_id>/status")
@require_team_member
def change_status(current_user, task_id):
    task = Task.query.get(task_id)
    if not task:
        return not_found("Task")
    if not assert_team_owns(task, current_user):
        return forbidden()

    data, err = validate_or_400(ChangeStatusSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    to_status = data["to_status"]
    if task.status == to_status:
        return bad_request(f"Task is already in status {to_status}")

    db.session.add(TaskStatusHistory(
        task_id=task.id,
        from_status=task.status,
        to_status=to_status,
        changed_by=current_user.id,
    ))
    task.status = to_status

    if to_status == "DONE":
        task.completed_at = task.completed_at or datetime.now(timezone.utc)
    else:
        task.completed_at = None

    db.session.commit()
    return ok(task.to_dict())


@tasks_bp.get("/<int:task_id>/history")
@require_team_member
def get_status_history(current_user, task_id):
    task = Task.query.get(task_id)
    if not task:
        return not_found("Task")
    if not assert_team_owns(task, current_user):
        return forbidden()
    return ok([h.to_dict() for h in task.status_history.all()])

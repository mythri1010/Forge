from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.worklog import Worklog
from app.models.task import Task
from app.schemas import CreateWorklogSchema
from app.utils.auth import require_team_member, assert_team_owns
from app.utils.validation import validate_or_400
from app.utils.pagination import paginate
from app.utils.errors import not_found, forbidden, ok

worklogs_bp = Blueprint("worklogs", __name__)


def _get_task_for_user(task_id, current_user):
    task = Task.query.get(task_id)
    if not task:
        return None, not_found("Task")
    if not assert_team_owns(task, current_user):
        return None, forbidden()
    return task, None


@worklogs_bp.get("/task/<int:task_id>")
@require_team_member
def list_worklogs(current_user, task_id):
    _, error = _get_task_for_user(task_id, current_user)
    if error:
        return error
    query = Worklog.query.filter_by(task_id=task_id).order_by(Worklog.date.desc())
    return ok(paginate(query, lambda w: w.to_dict()))


@worklogs_bp.post("/task/<int:task_id>")
@require_team_member
def create_worklog(current_user, task_id):
    _, error = _get_task_for_user(task_id, current_user)
    if error:
        return error

    data, err = validate_or_400(CreateWorklogSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    worklog = Worklog(
        task_id=task_id,
        team_id=current_user.team_id,
        user_id=current_user.id,
        date=data.get("date") or date.today(),
        hours=data["hours"],
        note=data.get("note"),
    )
    db.session.add(worklog)
    db.session.commit()
    return ok(worklog.to_dict(), 201)


@worklogs_bp.delete("/<int:worklog_id>")
@require_team_member
def delete_worklog(current_user, worklog_id):
    worklog = Worklog.query.get(worklog_id)
    if not worklog:
        return not_found("Worklog")
    if worklog.team_id != current_user.team_id:
        return forbidden()
    if worklog.user_id != current_user.id and current_user.role not in ("TEAM_ADMIN", "PLATFORM_ADMIN"):
        return forbidden()
    db.session.delete(worklog)
    db.session.commit()
    return ok({"message": "Deleted"})

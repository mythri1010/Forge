from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.learning import LearningLog
from app.models.task import Task
from app.schemas import CreateLearningLogSchema
from app.utils.auth import require_team_member, assert_team_owns
from app.utils.validation import validate_or_400
from app.utils.pagination import paginate
from app.utils.errors import not_found, forbidden, ok

learning_bp = Blueprint("learning", __name__)


@learning_bp.get("")
@require_team_member
def list_entries(current_user):
    query = (
        LearningLog.query
        .filter_by(user_id=current_user.id)
        .order_by(LearningLog.date.desc())
    )
    return ok(paginate(query, lambda l: l.to_dict()))


@learning_bp.post("")
@require_team_member
def create_entry(current_user):
    data, err = validate_or_400(CreateLearningLogSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    task_id = data.get("task_id")
    if task_id:
        task = Task.query.get(task_id)
        if not task:
            return not_found("Task")
        if not assert_team_owns(task, current_user):
            return forbidden()

    entry = LearningLog(
        user_id=current_user.id,
        task_id=task_id,
        date=data.get("date") or date.today(),
        summary=data["summary"],
    )
    db.session.add(entry)
    db.session.commit()
    return ok(entry.to_dict(), 201)


@learning_bp.delete("/<int:entry_id>")
@require_team_member
def delete_entry(current_user, entry_id):
    entry = LearningLog.query.get(entry_id)
    if not entry:
        return not_found("Learning log")
    if entry.user_id != current_user.id:
        return forbidden()
    db.session.delete(entry)
    db.session.commit()
    return ok({"message": "Deleted"})

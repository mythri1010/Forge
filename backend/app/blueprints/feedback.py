from flask import Blueprint, request
from app.extensions import db
from app.models.feedback import Feedback
from app.schemas import CreateFeedbackSchema
from app.utils.auth import require_team_member
from app.utils.validation import validate_or_400
from app.utils.errors import ok

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.post("")
@require_team_member
def submit_feedback(current_user):
    data, err = validate_or_400(CreateFeedbackSchema(), request.get_json(silent=True) or {})
    if err:
        return err

    entry = Feedback(
        team_id=current_user.team_id,
        user_id=current_user.id,
        category=data["category"],
        message=data["message"],
    )
    db.session.add(entry)
    db.session.commit()
    return ok(entry.to_dict(), 201)


@feedback_bp.get("")
@require_team_member
def list_my_feedback(current_user):
    if current_user.role in ("TEAM_ADMIN", "PLATFORM_ADMIN"):
        entries = Feedback.query.filter_by(team_id=current_user.team_id).all()
    else:
        entries = Feedback.query.filter_by(
            team_id=current_user.team_id, user_id=current_user.id
        ).all()
    return ok([e.to_dict() for e in entries])

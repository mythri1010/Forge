from datetime import datetime, timezone, timedelta
from flask import Blueprint, request
from sqlalchemy import func, text

from app.extensions import db
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.task import Task
from app.models.worklog import Worklog
from app.models.weekly import WeeklyGoal, WeeklyReflection
from app.models.feedback import Feedback
from app.utils.auth import require_platform_admin
from app.utils.errors import ok

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/overview")
@require_platform_admin
def overview(current_user):
    teams = Team.query.all()
    results = []

    for team in teams:
        user_count = TeamMember.query.filter_by(team_id=team.id).count()
        project_count = Project.query.filter_by(team_id=team.id).count()
        task_count = Task.query.filter_by(team_id=team.id).count()

        hours_result = db.session.query(func.sum(Worklog.hours)).filter(
            Worklog.team_id == team.id
        ).scalar()
        total_hours = float(hours_result or 0)

        # Last active: most recent worklog date
        last_log = db.session.query(func.max(Worklog.created_at)).filter(
            Worklog.team_id == team.id
        ).scalar()
        last_active_at = last_log.isoformat() if last_log else None

        # Goal success rate
        total_r = db.session.query(func.count(WeeklyReflection.id)).join(
            WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
        ).filter(WeeklyGoal.team_id == team.id).scalar() or 0

        met_r = db.session.query(func.count(WeeklyReflection.id)).join(
            WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
        ).filter(
            WeeklyGoal.team_id == team.id,
            WeeklyReflection.met_goal == True,  # noqa: E712
        ).scalar() or 0

        goal_rate = round(met_r / total_r, 3) if total_r else None

        avg_help = db.session.query(
            func.avg(WeeklyReflection.perceived_helpfulness)
        ).join(
            WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
        ).filter(
            WeeklyGoal.team_id == team.id,
            WeeklyReflection.perceived_helpfulness.isnot(None),
        ).scalar()
        avg_help = round(float(avg_help), 2) if avg_help else None

        results.append({
            "team_id": team.id,
            "team_name": team.name,
            "user_count": user_count,
            "project_count": project_count,
            "task_count": task_count,
            "total_hours": total_hours,
            "last_active_at": last_active_at,
            "avg_weekly_goal_success_rate": goal_rate,
            "avg_perceived_helpfulness": avg_help,
        })

    return ok(results)


@admin_bp.get("/usage-timeseries")
@require_platform_admin
def usage_timeseries(current_user):
    """Returns per-week activity counts (worklogs, tasks completed) per team.

    Accepts optional query params: weeks (default 8), team_id.
    """
    weeks = min(int(request.args.get("weeks", 8)), 52)
    filter_team = request.args.get("team_id")

    results = []
    now = datetime.now(timezone.utc)

    for i in range(weeks - 1, -1, -1):
        week_end = now - timedelta(weeks=i)
        week_start = week_end - timedelta(weeks=1)
        label = week_start.strftime("%Y-W%W")

        wl_query = db.session.query(
            Worklog.team_id,
            func.count(Worklog.id).label("worklog_count"),
            func.sum(Worklog.hours).label("hours"),
        ).filter(
            Worklog.created_at >= week_start,
            Worklog.created_at < week_end,
        )
        task_query = db.session.query(
            Task.team_id,
            func.count(Task.id).label("tasks_completed"),
        ).filter(
            Task.status == "DONE",
            Task.completed_at >= week_start,
            Task.completed_at < week_end,
        )

        if filter_team:
            wl_query = wl_query.filter(Worklog.team_id == int(filter_team))
            task_query = task_query.filter(Task.team_id == int(filter_team))

        wl_rows = {r.team_id: r for r in wl_query.group_by(Worklog.team_id).all()}
        task_rows = {r.team_id: r for r in task_query.group_by(Task.team_id).all()}

        all_team_ids = set(wl_rows) | set(task_rows)
        for tid in all_team_ids:
            results.append({
                "week": label,
                "team_id": tid,
                "worklog_count": wl_rows[tid].worklog_count if tid in wl_rows else 0,
                "hours_logged": float(wl_rows[tid].hours or 0) if tid in wl_rows else 0.0,
                "tasks_completed": task_rows[tid].tasks_completed if tid in task_rows else 0,
            })

    return ok(results)


@admin_bp.get("/feedback")
@require_platform_admin
def list_feedback(current_user):
    """Returns all feedback with team name. No raw task or user content exposed."""
    entries = (
        db.session.query(Feedback, Team.name.label("team_name"))
        .join(Team, Team.id == Feedback.team_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    return ok([{
        "id": f.id,
        "team_id": f.team_id,
        "team_name": team_name,
        "category": f.category,
        "message": f.message,
        "status": f.status,
        "created_at": f.created_at.isoformat(),
    } for f, team_name in entries])


@admin_bp.patch("/feedback/<int:feedback_id>")
@require_platform_admin
def update_feedback_status(current_user, feedback_id):
    from app.utils.errors import ok
    from app.utils.validation import validate_or_400
    from app.schemas import UpdateFeedbackStatusSchema
    from app.models.feedback import VALID_FEEDBACK_STATUSES

    data = request.get_json(silent=True) or {}
    new_status = (data.get("status") or "").upper()
    if new_status not in VALID_FEEDBACK_STATUSES:
        return bad_request(f"status must be one of {VALID_FEEDBACK_STATUSES}")

    entry = Feedback.query.get(feedback_id)
    if not entry:
        return not_found("Feedback")

    entry.status = new_status
    db.session.commit()
    return ok({"id": entry.id, "status": entry.status})

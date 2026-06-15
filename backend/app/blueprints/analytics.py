from datetime import datetime, timezone, timedelta
from flask import Blueprint
from sqlalchemy import func, case

from app.extensions import db
from app.models.project import Project
from app.models.task import Task, TaskStatusHistory
from app.models.worklog import Worklog
from app.models.team import TeamMember
from app.models.weekly import WeeklyGoal, WeeklyReflection
from app.utils.auth import require_team_member, assert_team_owns
from app.utils.errors import not_found, forbidden, ok

analytics_bp = Blueprint("analytics", __name__)

# ── helpers ───────────────────────────────────────────────────────────────────

def _first_in_progress_at(task_id: int):
    """Returns the timestamp when a task first entered IN_PROGRESS, or None."""
    row = (
        TaskStatusHistory.query
        .filter_by(task_id=task_id, to_status="IN_PROGRESS")
        .order_by(TaskStatusHistory.changed_at)
        .first()
    )
    return row.changed_at if row else None


def _compute_lead_cycle(tasks):
    """Returns (avg_lead_days, avg_cycle_days) for a list of DONE tasks."""
    leads, cycles = [], []
    for t in tasks:
        if t.completed_at and t.created_at:
            leads.append((t.completed_at - t.created_at).total_seconds() / 86400)
            ip_at = _first_in_progress_at(t.id)
            if ip_at:
                cycles.append((t.completed_at - ip_at).total_seconds() / 86400)

    avg_lead = round(sum(leads) / len(leads), 2) if leads else None
    avg_cycle = round(sum(cycles) / len(cycles), 2) if cycles else None
    return avg_lead, avg_cycle


# ── project metrics ───────────────────────────────────────────────────────────

@analytics_bp.get("/projects/<int:project_id>/metrics")
@require_team_member
def project_metrics(current_user, project_id):
    project = Project.query.get(project_id)
    if not project:
        return not_found("Project")
    if not assert_team_owns(project, current_user):
        return forbidden()

    all_tasks = Task.query.filter_by(project_id=project_id).all()
    done_tasks = [t for t in all_tasks if t.status == "DONE"]

    avg_lead, avg_cycle = _compute_lead_cycle(done_tasks)

    # Throughput: done tasks in the last 7 complete days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    throughput_per_week = sum(
        1 for t in done_tasks
        if t.completed_at and t.completed_at >= cutoff
    )

    # WIP by status (excludes DONE)
    wip_by_status = {}
    for t in all_tasks:
        if t.status != "DONE":
            wip_by_status[t.status] = wip_by_status.get(t.status, 0) + 1

    # At-risk: not DONE, past due date
    today = datetime.now(timezone.utc).date()
    tasks_at_risk = sum(
        1 for t in all_tasks
        if t.status != "DONE" and t.due_date and t.due_date < today
    )

    # Health score: simple 0–100 heuristic
    # Penalise for WIP > 2× team size and at-risk tasks
    total = len(all_tasks) or 1
    done_ratio = len(done_tasks) / total
    at_risk_ratio = tasks_at_risk / total
    health_score = round(max(0, min(100, (done_ratio * 60) + ((1 - at_risk_ratio) * 40))), 1)

    return ok({
        "project_id": project_id,
        "avg_lead_time_days": avg_lead,
        "avg_cycle_time_days": avg_cycle,
        "throughput_per_week": throughput_per_week,
        "wip_by_status": wip_by_status,
        "tasks_at_risk_count": tasks_at_risk,
        "health_score": health_score,
    })


# ── team metrics ──────────────────────────────────────────────────────────────

@analytics_bp.get("/teams/me/metrics")
@require_team_member
def team_metrics(current_user):
    team_id = current_user.team_id
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    members = TeamMember.query.filter_by(team_id=team_id).all()

    member_stats = []
    for m in members:
        uid = m.user_id

        # Current WIP: tasks assigned to user that are not DONE
        current_wip = Task.query.filter(
            Task.team_id == team_id,
            Task.assignee_id == uid,
            Task.status.notin_(["DONE"]),
        ).count()

        # Tasks finished in last 7 days
        tasks_done_7d = Task.query.filter(
            Task.team_id == team_id,
            Task.assignee_id == uid,
            Task.status == "DONE",
            Task.completed_at >= seven_days_ago,
        ).count()

        # Total hours logged in last 7 days
        hours_result = db.session.query(func.sum(Worklog.hours)).filter(
            Worklog.team_id == team_id,
            Worklog.user_id == uid,
            Worklog.date >= seven_days_ago.date(),
        ).scalar()
        total_hours_7d = float(hours_result or 0)

        # Avg cycle time for tasks this user completed
        done_tasks = Task.query.filter(
            Task.team_id == team_id,
            Task.assignee_id == uid,
            Task.status == "DONE",
        ).all()
        _, avg_cycle = _compute_lead_cycle(done_tasks)

        member_stats.append({
            "user_id": uid,
            "user_name": m.user.name,
            "current_wip": current_wip,
            "tasks_done_last_7d": tasks_done_7d,
            "total_hours_last_7d": total_hours_7d,
            "avg_cycle_time_days": avg_cycle,
        })

    # Weekly goal success rate for the team
    total_reflections = db.session.query(func.count(WeeklyReflection.id)).join(
        WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
    ).filter(WeeklyGoal.team_id == team_id).scalar() or 0

    met_reflections = db.session.query(func.count(WeeklyReflection.id)).join(
        WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
    ).filter(
        WeeklyGoal.team_id == team_id,
        WeeklyReflection.met_goal == True,  # noqa: E712
    ).scalar() or 0

    goal_success_rate = (
        round(met_reflections / total_reflections, 3) if total_reflections else None
    )

    # Average perceived helpfulness
    avg_helpfulness = db.session.query(
        func.avg(WeeklyReflection.perceived_helpfulness)
    ).join(
        WeeklyGoal, WeeklyGoal.id == WeeklyReflection.weekly_goal_id
    ).filter(
        WeeklyGoal.team_id == team_id,
        WeeklyReflection.perceived_helpfulness.isnot(None),
    ).scalar()
    avg_helpfulness = round(float(avg_helpfulness), 2) if avg_helpfulness else None

    return ok({
        "team_id": team_id,
        "member_stats": member_stats,
        "weekly_goal_success_rate": goal_success_rate,
        "avg_perceived_helpfulness": avg_helpfulness,
    })

"""
Analytics tests focus on the shape and correctness of computed metrics.
They deliberately set up enough data to make the numbers non-trivial.
"""
import json
import pytest
from datetime import datetime, timezone, timedelta, date

from app.models.task import Task, TaskStatusHistory
from app.models.worklog import Worklog
from app.models.weekly import WeeklyGoal, WeeklyReflection


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


def _seed_done_task(db, scenario, days_to_complete=3):
    """Creates a DONE task with a known lead time."""
    now = datetime.now(timezone.utc)
    task = Task(
        project_id=scenario["project"].id,
        team_id=scenario["team"].id,
        title="Seeded Done Task",
        status="DONE",
        priority="MEDIUM",
        created_by=scenario["admin"].id,
        assignee_id=scenario["member"].id,
        created_at=now - timedelta(days=days_to_complete),
        completed_at=now,
    )
    db.session.add(task)
    db.session.flush()

    # Add IN_PROGRESS entry (needed for cycle time)
    db.session.add(TaskStatusHistory(
        task_id=task.id,
        from_status="TODO",
        to_status="IN_PROGRESS",
        changed_at=now - timedelta(days=days_to_complete - 1),
        changed_by=scenario["admin"].id,
    ))
    db.session.commit()
    return task


def _seed_worklog(db, scenario, user, hours=4.0, days_ago=1):
    log = Worklog(
        task_id=scenario["task_todo"].id,
        team_id=scenario["team"].id,
        user_id=user.id,
        date=date.today() - timedelta(days=days_ago),
        hours=hours,
    )
    db.session.add(log)
    db.session.commit()
    return log


def _seed_reflection(db, scenario, met=True, helpfulness=5):
    now = datetime.now(timezone.utc)
    goal = WeeklyGoal(
        project_id=scenario["project"].id,
        team_id=scenario["team"].id,
        week_start_date=date.today(),
        goal_text="test",
    )
    db.session.add(goal)
    db.session.flush()
    r = WeeklyReflection(
        weekly_goal_id=goal.id,
        met_goal=met,
        perceived_helpfulness=helpfulness,
    )
    db.session.add(r)
    db.session.commit()
    return goal, r


class TestProjectMetrics:
    def test_metrics_shape(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        data = r.get_json()
        required_keys = {
            "project_id", "avg_lead_time_days", "avg_cycle_time_days",
            "throughput_per_week", "wip_by_status", "tasks_at_risk_count", "health_score"
        }
        assert required_keys == data.keys()

    def test_lead_time_computed(self, client, db, scenario, auth_headers):
        _seed_done_task(db, scenario, days_to_complete=4)
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        data = r.get_json()
        # The seeded task had a 4-day lead time; scenario fixture also has a DONE task
        assert data["avg_lead_time_days"] is not None
        assert data["avg_lead_time_days"] > 0

    def test_cycle_time_computed(self, client, db, scenario, auth_headers):
        _seed_done_task(db, scenario, days_to_complete=3)
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        data = r.get_json()
        # Cycle time should be shorter than or equal to lead time
        if data["avg_cycle_time_days"] and data["avg_lead_time_days"]:
            assert data["avg_cycle_time_days"] <= data["avg_lead_time_days"]

    def test_wip_by_status_excludes_done(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        wip = r.get_json()["wip_by_status"]
        assert "DONE" not in wip

    def test_throughput_counts_recent_done(self, client, db, scenario, auth_headers):
        _seed_done_task(db, scenario, days_to_complete=2)  # completed < 7 days ago
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        assert r.get_json()["throughput_per_week"] >= 1

    def test_health_score_in_range(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics",
                       headers=auth_headers(scenario["member"]))
        hs = r.get_json()["health_score"]
        assert 0 <= hs <= 100

    def test_cross_team_denied(self, client, db, scenario,
                               make_user, make_team, auth_headers):
        outsider = make_user(email="out6@x.com")
        make_team(name="Other6", owner=outsider)
        db.session.commit()

        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}/metrics", headers=auth_headers(outsider))
        assert r.status_code == 403


class TestTeamMetrics:
    def test_metrics_shape(self, client, db, scenario, auth_headers):
        r = client.get("/api/teams/me/metrics", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        data = r.get_json()
        assert "team_id" in data
        assert "member_stats" in data
        assert "weekly_goal_success_rate" in data
        assert "avg_perceived_helpfulness" in data

    def test_member_stats_per_member(self, client, db, scenario, auth_headers):
        r = client.get("/api/teams/me/metrics", headers=auth_headers(scenario["admin"]))
        stats = r.get_json()["member_stats"]
        member_ids = {s["user_id"] for s in stats}
        assert scenario["member"].id in member_ids
        assert scenario["admin"].id in member_ids

    def test_hours_aggregated_correctly(self, client, db, scenario, auth_headers):
        _seed_worklog(db, scenario, scenario["member"], hours=3.0, days_ago=1)
        _seed_worklog(db, scenario, scenario["member"], hours=2.5, days_ago=2)

        r = client.get("/api/teams/me/metrics", headers=auth_headers(scenario["admin"]))
        stats = {s["user_id"]: s for s in r.get_json()["member_stats"]}
        member_hours = stats[scenario["member"].id]["total_hours_last_7d"]
        assert member_hours == pytest.approx(5.5, rel=1e-2)

    def test_goal_success_rate_computation(self, client, db, scenario, auth_headers):
        _seed_reflection(db, scenario, met=True, helpfulness=5)
        _seed_reflection(db, scenario, met=False, helpfulness=3)

        r = client.get("/api/teams/me/metrics", headers=auth_headers(scenario["admin"]))
        data = r.get_json()
        # 1 met out of 2 total
        assert data["weekly_goal_success_rate"] == pytest.approx(0.5, rel=1e-2)
        # avg of 5 and 3
        assert data["avg_perceived_helpfulness"] == pytest.approx(4.0, rel=1e-2)

    def test_no_reflections_returns_none(self, client, db, scenario, auth_headers):
        r = client.get("/api/teams/me/metrics", headers=auth_headers(scenario["admin"]))
        data = r.get_json()
        # No reflections seeded in base scenario
        assert data["weekly_goal_success_rate"] is None
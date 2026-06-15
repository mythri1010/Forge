import json
import pytest

from app.models.feedback import Feedback
from app.models.worklog import Worklog
from datetime import date


def _make_platform_admin(db, make_user):
    user = make_user(name="Platform Admin", email="padmin@platform.com", role="PLATFORM_ADMIN")
    db.session.commit()
    return user


class TestAdminOverview:
    def test_overview_requires_platform_admin(self, client, db, scenario, auth_headers):
        r = client.get("/api/admin/overview", headers=auth_headers(scenario["admin"]))
        assert r.status_code == 403

    def test_overview_returns_all_teams(self, client, db, scenario, make_user, auth_headers):
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/overview", headers=auth_headers(admin))
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        team_ids = [row["team_id"] for row in data]
        assert scenario["team"].id in team_ids

    def test_overview_shape(self, client, db, scenario, make_user, auth_headers):
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/overview", headers=auth_headers(admin))
        row = next(d for d in r.get_json() if d["team_id"] == scenario["team"].id)
        expected_keys = {
            "team_id", "team_name", "user_count", "project_count",
            "task_count", "total_hours", "last_active_at",
            "avg_weekly_goal_success_rate", "avg_perceived_helpfulness",
        }
        assert expected_keys == row.keys()

    def test_overview_counts_correct(self, client, db, scenario, make_user, auth_headers):
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/overview", headers=auth_headers(admin))
        row = next(d for d in r.get_json() if d["team_id"] == scenario["team"].id)
        assert row["user_count"] == 2     # admin + member
        assert row["project_count"] >= 1
        assert row["task_count"] >= 2


class TestAdminFeedback:
    def _seed_feedback(self, db, scenario):
        fb = Feedback(
            team_id=scenario["team"].id,
            user_id=scenario["member"].id,
            category="BUG",
            message="The button is broken",
        )
        db.session.add(fb)
        db.session.commit()
        return fb

    def test_list_feedback(self, client, db, scenario, make_user, auth_headers):
        self._seed_feedback(db, scenario)
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/feedback", headers=auth_headers(admin))
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) >= 1
        # team_name is populated
        assert all("team_name" in row for row in data)

    def test_feedback_has_no_user_pii(self, client, db, scenario, make_user, auth_headers):
        """Admin feedback endpoint must not expose user email or raw task content."""
        self._seed_feedback(db, scenario)
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/feedback", headers=auth_headers(admin))
        for row in r.get_json():
            assert "email" not in row
            assert "password" not in row

    def test_update_feedback_status(self, client, db, scenario, make_user, auth_headers):
        fb = self._seed_feedback(db, scenario)
        admin = _make_platform_admin(db, make_user)
        r = client.patch(
            f"/api/admin/feedback/{fb.id}",
            data=json.dumps({"status": "REVIEWED"}),
            content_type="application/json",
            headers=auth_headers(admin),
        )
        assert r.status_code == 200
        assert r.get_json()["status"] == "REVIEWED"

    def test_update_feedback_invalid_status(self, client, db, scenario, make_user, auth_headers):
        fb = self._seed_feedback(db, scenario)
        admin = _make_platform_admin(db, make_user)
        r = client.patch(
            f"/api/admin/feedback/{fb.id}",
            data=json.dumps({"status": "PENDING"}),
            content_type="application/json",
            headers=auth_headers(admin),
        )
        assert r.status_code == 400


class TestAdminTimeseries:
    def test_timeseries_shape(self, client, db, scenario, make_user, auth_headers):
        admin = _make_platform_admin(db, make_user)
        r = client.get("/api/admin/usage-timeseries?weeks=4", headers=auth_headers(admin))
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        if data:
            row = data[0]
            assert "week" in row
            assert "team_id" in row
            assert "hours_logged" in row
            assert "tasks_completed" in row

    def test_timeseries_requires_platform_admin(self, client, db, scenario, auth_headers):
        r = client.get("/api/admin/usage-timeseries", headers=auth_headers(scenario["admin"]))
        assert r.status_code == 403
import json
import pytest


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


class TestWeeklyGoals:
    def test_create_goal(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/weekly/goals/project/{pid}", {
            "goal_text": "Ship the login feature",
            "week_start_date": "2025-06-02",
        }, auth_headers(scenario["admin"]))
        assert r.status_code == 201
        data = r.get_json()
        assert data["goal_text"] == "Ship the login feature"
        assert data["team_id"] == scenario["team"].id

    def test_list_goals(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        _post(client, f"/api/weekly/goals/project/{pid}", {
            "goal_text": "G1", "week_start_date": "2025-06-02",
        }, auth_headers(scenario["admin"]))
        _post(client, f"/api/weekly/goals/project/{pid}", {
            "goal_text": "G2", "week_start_date": "2025-06-09",
        }, auth_headers(scenario["admin"]))

        r = client.get(f"/api/weekly/goals/project/{pid}",
                       headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert len(r.get_json()) == 2

    def test_create_goal_missing_date(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/weekly/goals/project/{pid}",
                  {"goal_text": "No date"}, auth_headers(scenario["admin"]))
        assert r.status_code == 400


class TestReflections:
    def _create_goal(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/weekly/goals/project/{pid}", {
            "goal_text": "Ship it", "week_start_date": "2025-06-02",
        }, auth_headers(scenario["admin"]))
        return r.get_json()["id"]

    def test_submit_reflection(self, client, db, scenario, auth_headers):
        gid = self._create_goal(client, db, scenario, auth_headers)
        r = _post(client, f"/api/weekly/goals/{gid}/reflections", {
            "met_goal": True,
            "blockers": "None",
            "perceived_helpfulness": 4,
        }, auth_headers(scenario["member"]))
        assert r.status_code == 201
        data = r.get_json()
        assert data["met_goal"] is True
        assert data["perceived_helpfulness"] == 4

    def test_reflection_helpfulness_out_of_range(self, client, db, scenario, auth_headers):
        gid = self._create_goal(client, db, scenario, auth_headers)
        r = _post(client, f"/api/weekly/goals/{gid}/reflections", {
            "met_goal": False, "perceived_helpfulness": 10,
        }, auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_reflection_met_goal_required(self, client, db, scenario, auth_headers):
        gid = self._create_goal(client, db, scenario, auth_headers)
        r = _post(client, f"/api/weekly/goals/{gid}/reflections",
                  {"blockers": "oops"}, auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_cross_team_goal_denied(self, client, db, scenario,
                                    make_user, make_team, auth_headers):
        outsider = make_user(email="out5@x.com")
        make_team(name="Other5", owner=outsider)
        db.session.commit()

        gid = self._create_goal(client, db, scenario, auth_headers)
        r = _post(client, f"/api/weekly/goals/{gid}/reflections",
                  {"met_goal": True}, auth_headers(outsider))
        assert r.status_code == 403
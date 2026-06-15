import json
import pytest


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


class TestWorklogs:
    def test_create_worklog(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {
            "hours": 2.5,
            "date": "2025-06-01",
            "note": "Fixed the bug",
        }, auth_headers(scenario["member"]))
        assert r.status_code == 201
        data = r.get_json()
        assert data["hours"] == 2.5
        assert data["user_id"] == scenario["member"].id
        assert data["team_id"] == scenario["team"].id

    def test_list_worklogs(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        _post(client, f"/api/worklogs/task/{tid}", {"hours": 1}, auth_headers(scenario["member"]))
        _post(client, f"/api/worklogs/task/{tid}", {"hours": 2}, auth_headers(scenario["admin"]))

        r = client.get(f"/api/worklogs/task/{tid}", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert len(r.get_json()) == 2

    def test_hours_validation_zero(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 0},
                  auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_hours_validation_over_24(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 25},
                  auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_cross_team_task_denied(self, client, db, scenario,
                                    make_user, make_team, auth_headers):
        outsider = make_user(email="out4@other.com")
        make_team(name="OtherTeam4", owner=outsider)
        db.session.commit()

        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 1},
                  auth_headers(outsider))
        assert r.status_code == 403

    def test_delete_own_worklog(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 1},
                  auth_headers(scenario["member"]))
        wid = r.get_json()["id"]

        r2 = client.delete(f"/api/worklogs/{wid}", headers=auth_headers(scenario["member"]))
        assert r2.status_code == 200

    def test_delete_others_worklog_denied(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 1},
                  auth_headers(scenario["admin"]))
        wid = r.get_json()["id"]

        r2 = client.delete(f"/api/worklogs/{wid}", headers=auth_headers(scenario["member"]))
        assert r2.status_code == 403

    def test_admin_can_delete_any_worklog(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/worklogs/task/{tid}", {"hours": 1},
                  auth_headers(scenario["member"]))
        wid = r.get_json()["id"]

        r2 = client.delete(f"/api/worklogs/{wid}", headers=auth_headers(scenario["admin"]))
        assert r2.status_code == 200
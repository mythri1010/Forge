import json
import pytest


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


class TestLearningLogs:
    def test_create_entry(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/learning", {
            "summary": "Learned about SQLAlchemy relationships",
            "date": "2025-06-01",
            "task_id": scenario["task_todo"].id,
        }, auth_headers(scenario["member"]))
        assert r.status_code == 201
        data = r.get_json()
        assert data["user_id"] == scenario["member"].id
        assert data["task_id"] == scenario["task_todo"].id

    def test_create_entry_no_task(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/learning",
                  {"summary": "General note", "date": "2025-06-01"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 201
        assert r.get_json()["task_id"] is None

    def test_create_entry_missing_summary(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/learning", {}, auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_list_entries_scoped_to_user(self, client, db, scenario, auth_headers):
        _post(client, "/api/learning", {"summary": "Member note"},
              auth_headers(scenario["member"]))
        _post(client, "/api/learning", {"summary": "Admin note"},
              auth_headers(scenario["admin"]))

        r = client.get("/api/learning", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        entries = r.get_json()
        # Member should only see their own entries
        assert all(e["user_id"] == scenario["member"].id for e in entries)

    def test_delete_own_entry(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/learning", {"summary": "Delete me"},
                  auth_headers(scenario["member"]))
        eid = r.get_json()["id"]

        r2 = client.delete(f"/api/learning/{eid}", headers=auth_headers(scenario["member"]))
        assert r2.status_code == 200

    def test_delete_others_entry_denied(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/learning", {"summary": "Admin note"},
                  auth_headers(scenario["admin"]))
        eid = r.get_json()["id"]

        r2 = client.delete(f"/api/learning/{eid}", headers=auth_headers(scenario["member"]))
        assert r2.status_code == 403

    def test_cross_team_task_denied(self, client, db, scenario,
                                    make_user, make_team, auth_headers):
        outsider = make_user(email="out7@x.com")
        make_team(name="Other7", owner=outsider)
        db.session.commit()

        r = _post(client, "/api/learning", {
            "summary": "Sneaky",
            "task_id": scenario["task_todo"].id,
        }, auth_headers(outsider))
        assert r.status_code == 403
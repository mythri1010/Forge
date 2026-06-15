import json
import pytest


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


class TestProjects:
    def test_list_projects(self, client, db, scenario, auth_headers):
        r = client.get("/api/projects", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        assert any(p["id"] == scenario["project"].id for p in data)

    def test_create_project(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/projects", {
            "name": "New Project",
            "description": "Some desc",
            "start_date": "2025-01-01",
        }, auth_headers(scenario["member"]))
        assert r.status_code == 201
        assert r.get_json()["team_id"] == scenario["team"].id

    def test_create_project_missing_name(self, client, db, scenario, auth_headers):
        r = _post(client, "/api/projects", {}, auth_headers(scenario["admin"]))
        assert r.status_code == 400

    def test_get_project(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert r.get_json()["id"] == pid

    def test_get_project_cross_team_denied(self, client, db, scenario,
                                           make_user, make_team, make_project, auth_headers):
        outsider = make_user(email="out@other.com")
        other_team = make_team(name="Other Team", owner=outsider)
        db.session.commit()

        pid = scenario["project"].id
        r = client.get(f"/api/projects/{pid}", headers=auth_headers(outsider))
        assert r.status_code == 403

    def test_update_project(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.patch(
            f"/api/projects/{pid}",
            data=json.dumps({"name": "Renamed"}),
            content_type="application/json",
            headers=auth_headers(scenario["admin"]),
        )
        assert r.status_code == 200
        assert r.get_json()["name"] == "Renamed"

    def test_update_project_requires_team_admin(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.patch(
            f"/api/projects/{pid}",
            data=json.dumps({"name": "Should Fail"}),
            content_type="application/json",
            headers=auth_headers(scenario["member"]),
        )
        assert r.status_code == 403
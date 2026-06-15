import json
import pytest


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


def _get(client, url, headers):
    return client.get(url, headers=headers)


class TestCreateTeam:
    def test_create_team(self, client, db, make_user, auth_headers):
        user = make_user(email="new@team.com")
        db.session.commit()
        h = auth_headers(user)

        r = _post(client, "/api/teams", {"name": "New Team"}, h)
        assert r.status_code == 201
        data = r.get_json()
        assert data["name"] == "New Team"
        assert "invite_code" in data

    def test_create_team_already_in_team(self, client, db, scenario, auth_headers):
        h = auth_headers(scenario["admin"])
        r = _post(client, "/api/teams", {"name": "Another"}, h)
        assert r.status_code == 400
        assert "already in a team" in r.get_json()["error"]

    def test_create_team_missing_name(self, client, db, make_user, auth_headers):
        user = make_user(email="lone@x.com")
        db.session.commit()
        r = _post(client, "/api/teams", {}, auth_headers(user))
        assert r.status_code == 400


class TestJoinTeam:
    def test_join_via_invite_code(self, client, db, scenario, make_user, auth_headers):
        new_user = make_user(email="joiner@x.com")
        db.session.commit()
        h = auth_headers(new_user)

        r = _post(client, "/api/teams/join",
                  {"invite_code": scenario["team"].invite_code}, h)
        assert r.status_code == 201
        assert r.get_json()["id"] == scenario["team"].id

    def test_join_bad_code(self, client, db, make_user, auth_headers):
        user = make_user(email="bad@x.com")
        db.session.commit()
        r = _post(client, "/api/teams/join", {"invite_code": "INVALID"}, auth_headers(user))
        assert r.status_code == 404


class TestGetTeam:
    def test_get_my_team(self, client, db, scenario, auth_headers):
        r = _get(client, "/api/teams/me", auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert r.get_json()["id"] == scenario["team"].id

    def test_get_members(self, client, db, scenario, auth_headers):
        r = _get(client, "/api/teams/me/members", auth_headers(scenario["admin"]))
        assert r.status_code == 200
        ids = {m["user_id"] for m in r.get_json()}
        assert scenario["admin"].id in ids
        assert scenario["member"].id in ids

    def test_no_team_returns_forbidden(self, client, db, make_user, auth_headers):
        lone = make_user(email="lone2@x.com")
        db.session.commit()
        r = _get(client, "/api/teams/me", auth_headers(lone))
        assert r.status_code == 403


class TestMemberRoles:
    def test_admin_can_promote_member(self, client, db, scenario, auth_headers):
        h = auth_headers(scenario["admin"])
        member_id = scenario["member"].id
        r = client.patch(
            f"/api/teams/me/members/{member_id}/role",
            data=json.dumps({"role_in_team": "TEAM_ADMIN"}),
            content_type="application/json",
            headers=h,
        )
        assert r.status_code == 200
        assert r.get_json()["role_in_team"] == "TEAM_ADMIN"

    def test_regular_user_cannot_change_roles(self, client, db, scenario, auth_headers):
        h = auth_headers(scenario["member"])
        r = client.patch(
            f"/api/teams/me/members/{scenario['admin'].id}/role",
            data=json.dumps({"role_in_team": "USER"}),
            content_type="application/json",
            headers=h,
        )
        assert r.status_code == 403
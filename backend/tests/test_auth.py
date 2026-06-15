import json
import pytest


def post(client, url, body, headers=None):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers or {})


class TestRegister:
    def test_register_success(self, client, db):
        r = post(client, "/api/auth/register", {
            "name": "Alice", "email": "alice@example.com", "password": "secure123"
        })
        assert r.status_code == 201
        assert "user_id" in r.get_json()

    def test_register_duplicate_email(self, client, db, make_user):
        make_user(email="dup@example.com")
        db.session.commit()

        r = post(client, "/api/auth/register", {
            "name": "Bob", "email": "dup@example.com", "password": "secure123"
        })
        assert r.status_code == 400
        assert "already registered" in r.get_json()["error"]

    def test_register_missing_fields(self, client, db):
        r = post(client, "/api/auth/register", {"email": "x@x.com"})
        assert r.status_code == 400

    def test_register_short_password(self, client, db):
        r = post(client, "/api/auth/register", {
            "name": "Eve", "email": "eve@x.com", "password": "short"
        })
        assert r.status_code == 400
        assert "8 characters" in r.get_json()["error"]


class TestLogin:
    def test_login_success(self, client, db, make_user, make_team):
        user = make_user(email="login@example.com", password="password123")
        db.session.commit()

        r = post(client, "/api/auth/login", {
            "email": "login@example.com", "password": "password123"
        })
        assert r.status_code == 200
        data = r.get_json()
        assert "access_token" in data
        assert data["role"] == "USER"

    def test_login_wrong_password(self, client, db, make_user):
        make_user(email="x@x.com", password="rightpass")
        db.session.commit()

        r = post(client, "/api/auth/login", {"email": "x@x.com", "password": "wrong"})
        assert r.status_code == 401

    def test_login_unknown_email(self, client, db):
        r = post(client, "/api/auth/login", {
            "email": "nobody@nowhere.com", "password": "whatever"
        })
        assert r.status_code == 401

    def test_login_returns_team_id(self, client, db, scenario, make_user):
        """After joining a team, team_id is returned in the login payload."""
        r = post(client, "/api/auth/login", {
            "email": "admin@team.com", "password": "password123"
        })
        assert r.status_code == 200
        assert r.get_json()["team_id"] == scenario["team"].id

    def test_protected_route_without_token(self, client):
        r = client.get("/api/teams/me")
        assert r.status_code == 401
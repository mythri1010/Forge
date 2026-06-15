import json
import pytest
from datetime import datetime, timezone

from app.models.task import Task, TaskStatusHistory
from app.extensions import db as _db


def _post(client, url, body, headers):
    return client.post(url, data=json.dumps(body),
                       content_type="application/json", headers=headers)


def _patch(client, url, body, headers):
    return client.patch(url, data=json.dumps(body),
                        content_type="application/json", headers=headers)


class TestListTasks:
    def test_list_all_tasks(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/tasks/project/{pid}", headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert len(r.get_json()) == 2

    def test_filter_by_status(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = client.get(f"/api/tasks/project/{pid}?status=DONE",
                       headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        tasks = r.get_json()
        assert all(t["status"] == "DONE" for t in tasks)

    def test_filter_by_assignee(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        mid = scenario["member"].id
        r = client.get(f"/api/tasks/project/{pid}?assignee_id={mid}",
                       headers=auth_headers(scenario["member"]))
        tasks = r.get_json()
        assert all(t["assignee_id"] == mid for t in tasks)

    def test_cross_team_project_denied(self, client, db, scenario,
                                       make_user, make_team, auth_headers):
        outsider = make_user(email="out2@other.com")
        make_team(name="OtherTeam2", owner=outsider)
        db.session.commit()

        pid = scenario["project"].id
        r = client.get(f"/api/tasks/project/{pid}", headers=auth_headers(outsider))
        assert r.status_code == 403


class TestCreateTask:
    def test_create_task(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/tasks/project/{pid}", {
            "title": "Brand new task",
            "priority": "HIGH",
            "due_date": "2025-12-31",
        }, auth_headers(scenario["admin"]))
        assert r.status_code == 201
        data = r.get_json()
        assert data["status"] == "TODO"
        assert data["priority"] == "HIGH"
        assert data["team_id"] == scenario["team"].id

    def test_create_task_writes_history(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/tasks/project/{pid}", {"title": "Hist Task"},
                  auth_headers(scenario["admin"]))
        task_id = r.get_json()["id"]

        history = TaskStatusHistory.query.filter_by(task_id=task_id).all()
        assert len(history) == 1
        assert history[0].from_status is None
        assert history[0].to_status == "TODO"

    def test_create_task_missing_title(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/tasks/project/{pid}", {}, auth_headers(scenario["admin"]))
        assert r.status_code == 400

    def test_create_task_bad_priority(self, client, db, scenario, auth_headers):
        pid = scenario["project"].id
        r = _post(client, f"/api/tasks/project/{pid}",
                  {"title": "T", "priority": "URGENT"},
                  auth_headers(scenario["admin"]))
        assert r.status_code == 400


class TestUpdateTask:
    def test_update_title_and_assignee(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _patch(client, f"/api/tasks/{tid}", {
            "title": "Updated Title",
            "assignee_id": scenario["admin"].id,
        }, auth_headers(scenario["admin"]))
        assert r.status_code == 200
        data = r.get_json()
        assert data["title"] == "Updated Title"
        assert data["assignee_id"] == scenario["admin"].id

    def test_update_task_cross_team_denied(self, client, db, scenario,
                                           make_user, make_team, auth_headers):
        outsider = make_user(email="out3@other.com")
        make_team(name="OtherTeam3", owner=outsider)
        db.session.commit()

        tid = scenario["task_todo"].id
        r = _patch(client, f"/api/tasks/{tid}", {"title": "Nope"}, auth_headers(outsider))
        assert r.status_code == 403


class TestStatusChange:
    def test_valid_status_transition(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/tasks/{tid}/status",
                  {"to_status": "IN_PROGRESS"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert r.get_json()["status"] == "IN_PROGRESS"

    def test_transition_to_done_sets_completed_at(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        _post(client, f"/api/tasks/{tid}/status", {"to_status": "IN_PROGRESS"},
              auth_headers(scenario["member"]))
        r = _post(client, f"/api/tasks/{tid}/status", {"to_status": "DONE"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert r.get_json()["completed_at"] is not None

    def test_reopen_clears_completed_at(self, client, db, scenario, auth_headers):
        tid = scenario["task_done"].id
        r = _post(client, f"/api/tasks/{tid}/status", {"to_status": "IN_PROGRESS"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 200
        assert r.get_json()["completed_at"] is None

    def test_same_status_rejected(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/tasks/{tid}/status", {"to_status": "TODO"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_invalid_status_rejected(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        r = _post(client, f"/api/tasks/{tid}/status", {"to_status": "DOING"},
                  auth_headers(scenario["member"]))
        assert r.status_code == 400

    def test_status_history_recorded(self, client, db, scenario, auth_headers):
        tid = scenario["task_todo"].id
        _post(client, f"/api/tasks/{tid}/status", {"to_status": "IN_PROGRESS"},
              auth_headers(scenario["member"]))

        r = client.get(f"/api/tasks/{tid}/history",
                       headers=auth_headers(scenario["member"]))
        assert r.status_code == 200
        history = r.get_json()
        # Initial TODO entry + the IN_PROGRESS transition
        statuses = [h["to_status"] for h in history]
        assert "TODO" in statuses
        assert "IN_PROGRESS" in statuses
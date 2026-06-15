"""
Shared pytest fixtures.

SQLAlchemy 2.x compatible: each test runs inside a savepoint (nested
transaction) that is always rolled back, giving full isolation without
rebuilding the schema between tests.

Requires: TEST_DATABASE_URL env var, or defaults to tracker_test_db.
"""
import os
import pytest
from flask_jwt_extended import create_access_token

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
os.environ.setdefault(
    "DATABASE_URL",
    os.getenv("TEST_DATABASE_URL", "postgresql://tracker:tracker@localhost:5432/tracker_test_db"),
)
os.environ.setdefault("FLASK_ENV", "development")

from app import create_app                          # noqa: E402
from app.extensions import db as _db               # noqa: E402
from app.models.user import User                   # noqa: E402
from app.models.team import Team, TeamMember       # noqa: E402
from app.models.project import Project             # noqa: E402
from app.models.task import Task, TaskStatusHistory  # noqa: E402


# ── App / DB fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    # Disable rate-limit storage errors during tests
    flask_app.config["RATELIMIT_ENABLED"] = False

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture
def db(app):
    """
    Wraps each test in a savepoint.  The outer transaction is never committed,
    so every test starts with a clean slate.
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        _db.session.configure(bind=connection)

        # Create a savepoint so individual tests can also call commit()
        # without actually flushing to the DB.
        nested = connection.begin_nested()

        # Re-open the savepoint after any commit inside a test
        from sqlalchemy import event

        @event.listens_for(_db.session, "after_transaction_end")
        def reopen_savepoint(session, t):
            nonlocal nested
            if not nested.is_active:
                nested = connection.begin_nested()

        yield _db

        _db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Entity factories ──────────────────────────────────────────────────────────

@pytest.fixture
def make_user(db):
    def _make(name="Test User", email="user@example.com",
               password="password123", role="USER"):
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        return user
    return _make


@pytest.fixture
def make_team(db):
    def _make(name="Alpha Team", owner: User = None):
        team = Team(name=name)
        db.session.add(team)
        db.session.flush()
        if owner:
            m = TeamMember(team_id=team.id, user_id=owner.id, role_in_team="TEAM_ADMIN")
            owner.role = "TEAM_ADMIN"
            db.session.add(m)
            db.session.flush()
        return team
    return _make


@pytest.fixture
def make_project(db):
    def _make(team: Team, creator: User, name="Test Project"):
        project = Project(team_id=team.id, name=name, created_by=creator.id)
        db.session.add(project)
        db.session.flush()
        return project
    return _make


@pytest.fixture
def make_task(db):
    def _make(project: Project, creator: User, title="Test Task",
               status="TODO", assignee: User = None):
        task = Task(
            project_id=project.id,
            team_id=project.team_id,
            title=title,
            status=status,
            priority="MEDIUM",
            created_by=creator.id,
            assignee_id=assignee.id if assignee else None,
        )
        db.session.add(task)
        db.session.flush()
        db.session.add(TaskStatusHistory(
            task_id=task.id,
            from_status=None,
            to_status=status,
            changed_by=creator.id,
        ))
        db.session.flush()
        return task
    return _make


# ── Auth helper ───────────────────────────────────────────────────────────────

@pytest.fixture
def auth_headers(app):
    def _headers(user: User):
        with app.app_context():
            token = create_access_token(identity=user.id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    return _headers


# ── Pre-built scenario ────────────────────────────────────────────────────────

@pytest.fixture
def scenario(db, make_user, make_team, make_project, make_task):
    admin  = make_user(name="Admin",  email="admin@team.com",  role="TEAM_ADMIN")
    member = make_user(name="Member", email="member@team.com")
    team   = make_team(name="Dev Team", owner=admin)

    db.session.add(TeamMember(team_id=team.id, user_id=member.id, role_in_team="USER"))
    db.session.flush()

    project   = make_project(team=team, creator=admin)
    task_todo = make_task(project=project, creator=admin,
                          title="Todo Task", assignee=member)
    task_done = make_task(project=project, creator=admin,
                          title="Done Task", status="DONE", assignee=member)

    db.session.commit()

    return {
        "admin":     admin,
        "member":    member,
        "team":      team,
        "project":   project,
        "task_todo": task_todo,
        "task_done": task_done,
    }

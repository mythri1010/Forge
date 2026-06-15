"""
Seed script — creates realistic demo data for development and demo purposes.

Usage:
    python seed.py                  # seed all three demo teams
    python seed.py --wipe           # drop all rows first, then seed
    FLASK_ENV=development python seed.py

WARNING: Never run against a production database.
"""
import sys
import random
import argparse
from datetime import date, datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.task import Task, TaskStatusHistory
from app.models.worklog import Worklog
from app.models.weekly import WeeklyGoal, WeeklyReflection
from app.models.learning import LearningLog
from app.models.feedback import Feedback

app = create_app()

# ── helpers ───────────────────────────────────────────────────────────────────

def _rand_dt(days_ago_max: int, days_ago_min: int = 0) -> datetime:
    offset = random.randint(days_ago_min, days_ago_max)
    return datetime.now(timezone.utc) - timedelta(days=offset)


def _rand_date(days_ago_max: int, days_ago_min: int = 0) -> date:
    return _rand_dt(days_ago_max, days_ago_min).date()


def _make_user(name: str, email: str, password: str = "password123", role: str = "USER") -> User:
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    return user


def _make_team(name: str, admin: User) -> Team:
    team = Team(name=name)
    db.session.add(team)
    db.session.flush()
    m = TeamMember(team_id=team.id, user_id=admin.id, role_in_team="TEAM_ADMIN")
    admin.role = "TEAM_ADMIN"
    db.session.add(m)
    return team


def _add_member(team: Team, user: User) -> None:
    db.session.add(TeamMember(team_id=team.id, user_id=user.id, role_in_team="USER"))


def _make_project(team: Team, creator: User, name: str, weeks_ago: int = 8) -> Project:
    start = _rand_date(weeks_ago * 7, weeks_ago * 7 - 3)
    p = Project(
        team_id=team.id,
        name=name,
        description=f"Project: {name}. Auto-generated seed data.",
        start_date=start,
        end_date=start + timedelta(weeks=12),
        created_by=creator.id,
    )
    db.session.add(p)
    return p


def _make_task(project: Project, creator: User, assignee: User,
               title: str, status: str, days_ago_created: int) -> Task:
    created_at = _rand_dt(days_ago_created + 2, days_ago_created)
    completed_at = None
    if status == "DONE":
        completed_at = created_at + timedelta(days=random.randint(1, 5))

    t = Task(
        project_id=project.id,
        team_id=project.team_id,
        title=title,
        description=f"Task: {title}",
        status=status,
        priority=random.choice(["LOW", "MEDIUM", "MEDIUM", "HIGH"]),
        created_by=creator.id,
        assignee_id=assignee.id,
        created_at=created_at,
        completed_at=completed_at,
        due_date=_rand_date(2, -5),     # due dates scattered around today
    )
    db.session.add(t)
    db.session.flush()

    # Status history
    db.session.add(TaskStatusHistory(
        task_id=t.id, from_status=None, to_status="TODO",
        changed_at=created_at, changed_by=creator.id,
    ))
    if status in ("IN_PROGRESS", "IN_REVIEW", "DONE", "BLOCKED"):
        db.session.add(TaskStatusHistory(
            task_id=t.id, from_status="TODO", to_status="IN_PROGRESS",
            changed_at=created_at + timedelta(days=1), changed_by=assignee.id,
        ))
    if status in ("IN_REVIEW", "DONE"):
        db.session.add(TaskStatusHistory(
            task_id=t.id, from_status="IN_PROGRESS", to_status="IN_REVIEW",
            changed_at=created_at + timedelta(days=3), changed_by=assignee.id,
        ))
    if status == "DONE":
        db.session.add(TaskStatusHistory(
            task_id=t.id, from_status="IN_REVIEW", to_status="DONE",
            changed_at=completed_at, changed_by=creator.id,
        ))
    return t


def _make_worklogs(task: Task, users: list[User], n: int = 3) -> None:
    for _ in range(n):
        user = random.choice(users)
        db.session.add(Worklog(
            task_id=task.id,
            team_id=task.team_id,
            user_id=user.id,
            date=_rand_date(14),
            hours=round(random.uniform(0.5, 6.0), 1),
            note=random.choice(["Fixed edge case", "Pair programming session",
                                "Code review", "Unit tests added", None]),
        ))


def _make_weekly_goal(project: Project, week_offset: int, goal_text: str,
                      met: bool, helpfulness: int) -> None:
    week_start = date.today() - timedelta(weeks=week_offset, days=date.today().weekday())
    goal = WeeklyGoal(
        project_id=project.id,
        team_id=project.team_id,
        week_start_date=week_start,
        goal_text=goal_text,
    )
    db.session.add(goal)
    db.session.flush()
    db.session.add(WeeklyReflection(
        weekly_goal_id=goal.id,
        met_goal=met,
        blockers=None if met else "Unexpected dependency issue delayed completion.",
        process_notes="Stand-ups were effective. Better async communication needed.",
        perceived_helpfulness=helpfulness,
    ))


# ── teams ─────────────────────────────────────────────────────────────────────

TEAMS = [
    {
        "name": "Team Phoenix",
        "members": [
            ("Alice Chen", "alice@phoenix.dev"),
            ("Bob Rajan", "bob@phoenix.dev"),
            ("Cara Müller", "cara@phoenix.dev"),
            ("Dan Park", "dan@phoenix.dev"),
        ],
        "projects": ["Inventory Management System", "Mobile Onboarding Flow"],
    },
    {
        "name": "Team Orion",
        "members": [
            ("Eve Santos", "eve@orion.dev"),
            ("Frank Liu", "frank@orion.dev"),
            ("Grace Obi", "grace@orion.dev"),
            ("Hiro Tanaka", "hiro@orion.dev"),
            ("Isla Mack", "isla@orion.dev"),
        ],
        "projects": ["Analytics Dashboard", "API Gateway Refactor"],
    },
    {
        "name": "Team Nova",
        "members": [
            ("Jay Kim", "jay@nova.dev"),
            ("Kai Patel", "kai@nova.dev"),
            ("Lena Gomez", "lena@nova.dev"),
            ("Milo Reyes", "milo@nova.dev"),
        ],
        "projects": ["DevOps Pipeline Automation"],
    },
]

TASK_TITLES = [
    "Set up CI/CD pipeline",
    "Design database schema",
    "Implement auth middleware",
    "Write API integration tests",
    "Add pagination to list endpoints",
    "Fix N+1 query in dashboard",
    "Set up feature flags",
    "Migrate legacy data",
    "Document REST API",
    "Add error monitoring",
    "Performance profiling",
    "Implement caching layer",
    "Code review and cleanup",
    "Deploy to staging",
    "Security audit",
    "Add OpenAPI spec",
    "Refactor service layer",
    "Fix timezone handling bug",
    "Add rate limiting",
    "Update dependencies",
]

STATUSES = ["TODO", "TODO", "IN_PROGRESS", "IN_PROGRESS", "IN_REVIEW", "DONE", "DONE", "DONE"]

GOALS = [
    ("Complete authentication module", True, 4),
    ("Ship v1 of the dashboard", True, 5),
    ("Resolve all P1 bugs", False, 3),
    ("Integration testing pass", True, 4),
    ("Performance improvements merged", True, 5),
    ("Documentation up to date", False, 3),
    ("Staging deployment green", True, 5),
]

FEEDBACK_DATA = [
    ("FEATURE", "Would love a Slack integration for task updates."),
    ("BUG", "The weekly reflection form sometimes clears on submission."),
    ("GENERAL", "The dashboard metrics have been really helpful for our retrospectives."),
    ("FEATURE", "Can we get CSV export of worklogs?"),
    ("BUG", "Pagination breaks when filtering by status and changing pages."),
]


# ── main seeder ───────────────────────────────────────────────────────────────

def seed(wipe: bool = False) -> None:
    with app.app_context():
        if wipe:
            print("Wiping existing data...")
            # Order matters — FK constraints
            for model in [
                Feedback, LearningLog, WeeklyReflection, WeeklyGoal,
                Worklog, TaskStatusHistory, Task, Project,
                TeamMember, Team, User,
            ]:
                model.query.delete()
            db.session.commit()
            print("Done.")

        # Platform admin (no team)
        padmin = _make_user("Platform Admin", "admin@platform.dev",
                            password="admin1234", role="PLATFORM_ADMIN")
        db.session.flush()

        for team_spec in TEAMS:
            print(f"Seeding {team_spec['name']}...")

            # Create users — first member becomes team admin
            users = []
            for i, (name, email) in enumerate(team_spec["members"]):
                u = _make_user(name, email)
                db.session.flush()
                users.append(u)

            # Build team with first user as admin
            team = _make_team(team_spec["name"], users[0])
            for u in users[1:]:
                _add_member(team, u)
            db.session.flush()

            # Projects
            for proj_name in team_spec["projects"]:
                project = _make_project(team, users[0], proj_name)
                db.session.flush()

                # Tasks — 15-20 per project
                n_tasks = random.randint(15, 20)
                titles = random.sample(TASK_TITLES, min(n_tasks, len(TASK_TITLES)))
                tasks = []
                for title in titles:
                    status = random.choice(STATUSES)
                    assignee = random.choice(users)
                    task = _make_task(project, users[0], assignee, title, status,
                                      days_ago_created=random.randint(5, 40))
                    tasks.append(task)
                db.session.flush()

                # Worklogs
                for task in tasks:
                    _make_worklogs(task, users, n=random.randint(1, 4))

                # Learning logs
                for user in users:
                    if random.random() > 0.4:
                        db.session.add(LearningLog(
                            user_id=user.id,
                            task_id=random.choice(tasks).id,
                            date=_rand_date(14),
                            summary=random.choice([
                                "Learned about SQLAlchemy relationship loading strategies.",
                                "Deep-dived into JWT expiry handling.",
                                "Explored Postgres EXPLAIN ANALYZE output.",
                                "Read up on marshmallow schema inheritance.",
                                "Pair-programmed pagination logic — good refresher.",
                            ]),
                        ))

                # Weekly goals (last 4 weeks)
                for week_offset, (goal_text, met, helpfulness) in enumerate(
                    random.sample(GOALS, min(4, len(GOALS)))
                ):
                    _make_weekly_goal(project, week_offset, goal_text, met, helpfulness)

            # Feedback (2-3 per team)
            for category, message in random.sample(FEEDBACK_DATA, random.randint(2, 3)):
                db.session.add(Feedback(
                    team_id=team.id,
                    user_id=random.choice(users).id,
                    category=category,
                    message=message,
                ))

        db.session.commit()
        print("\nSeed complete.")
        print(f"  Platform admin: admin@platform.dev / admin1234")
        for spec in TEAMS:
            admin_email = spec["members"][0][1]
            print(f"  {spec['name']} admin: {admin_email} / password123")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the tracker database.")
    parser.add_argument("--wipe", action="store_true",
                        help="Delete all existing rows before seeding")
    args = parser.parse_args()
    seed(wipe=args.wipe)

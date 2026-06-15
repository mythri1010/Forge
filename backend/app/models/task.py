from datetime import datetime, timezone
from app.extensions import db

# Valid statuses — enforced at the application layer
VALID_STATUSES = {"TODO", "IN_PROGRESS", "IN_REVIEW", "DONE", "BLOCKED"}
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="TODO")
    priority = db.Column(db.String(32), nullable=False, default="MEDIUM")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    project = db.relationship("Project", back_populates="tasks")
    status_history = db.relationship("TaskStatusHistory", back_populates="task",
                                     order_by="TaskStatusHistory.changed_at", lazy="dynamic")
    worklogs = db.relationship("Worklog", back_populates="task", lazy="dynamic")
    learning_logs = db.relationship("LearningLog", back_populates="task", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "team_id": self.team_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_by": self.created_by,
            "assignee_id": self.assignee_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskStatusHistory(db.Model):
    __tablename__ = "task_status_history"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = db.Column(db.String(32), nullable=True)   # NULL for the initial status set
    to_status = db.Column(db.String(32), nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    task = db.relationship("Task", back_populates="status_history")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "changed_at": self.changed_at.isoformat(),
            "changed_by": self.changed_by,
        }

from datetime import datetime, timezone
from app.extensions import db


class Worklog(db.Model):
    __tablename__ = "worklogs"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Numeric(5, 2), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    task = db.relationship("Task", back_populates="worklogs")
    user = db.relationship("User", back_populates="worklogs")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "hours": float(self.hours),
            "note": self.note,
            "created_at": self.created_at.isoformat(),
        }

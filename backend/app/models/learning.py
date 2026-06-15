from datetime import datetime, timezone
from app.extensions import db


class LearningLog(db.Model):
    __tablename__ = "learning_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    date = db.Column(db.Date, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="learning_logs")
    task = db.relationship("Task", back_populates="learning_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "date": self.date.isoformat(),
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }

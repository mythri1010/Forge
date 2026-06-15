from datetime import datetime, timezone
from app.extensions import db


class WeeklyGoal(db.Model):
    __tablename__ = "weekly_goals"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start_date = db.Column(db.Date, nullable=False)
    goal_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = db.relationship("Project", back_populates="weekly_goals")
    reflections = db.relationship("WeeklyReflection", back_populates="weekly_goal", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "team_id": self.team_id,
            "week_start_date": self.week_start_date.isoformat(),
            "goal_text": self.goal_text,
            "created_at": self.created_at.isoformat(),
        }


class WeeklyReflection(db.Model):
    __tablename__ = "weekly_reflections"

    id = db.Column(db.Integer, primary_key=True)
    weekly_goal_id = db.Column(db.Integer, db.ForeignKey("weekly_goals.id", ondelete="CASCADE"),
                               nullable=False, index=True)
    met_goal = db.Column(db.Boolean, nullable=False)
    blockers = db.Column(db.Text, nullable=True)
    process_notes = db.Column(db.Text, nullable=True)
    # 1–5 subjective score; NULL if not provided
    perceived_helpfulness = db.Column(db.SmallInteger, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    weekly_goal = db.relationship("WeeklyGoal", back_populates="reflections")

    def to_dict(self):
        return {
            "id": self.id,
            "weekly_goal_id": self.weekly_goal_id,
            "met_goal": self.met_goal,
            "blockers": self.blockers,
            "process_notes": self.process_notes,
            "perceived_helpfulness": self.perceived_helpfulness,
            "created_at": self.created_at.isoformat(),
        }

import secrets
from datetime import datetime, timezone
from app.extensions import db


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    invite_code = db.Column(db.String(32), unique=True, nullable=False, index=True,
                            default=lambda: secrets.token_urlsafe(16))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    members = db.relationship("TeamMember", back_populates="team", lazy="dynamic")
    projects = db.relationship("Project", back_populates="team", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "invite_code": self.invite_code,
            "created_at": self.created_at.isoformat(),
        }


class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    # Role within the team context (mirrors global role but scoped to team)
    role_in_team = db.Column(db.String(32), nullable=False, default="USER")
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    team = db.relationship("Team", back_populates="members")
    user = db.relationship("User", back_populates="memberships")

    def to_dict(self):
        return {
            "id": self.id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_email": self.user.email,
            "role_in_team": self.role_in_team,
            "joined_at": self.joined_at.isoformat(),
        }

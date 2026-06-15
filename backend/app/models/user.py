import bcrypt
from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # Global role: USER | TEAM_ADMIN | PLATFORM_ADMIN
    role = db.Column(db.String(32), nullable=False, default="USER")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    memberships = db.relationship("TeamMember", back_populates="user", lazy="dynamic")
    worklogs = db.relationship("Worklog", back_populates="user", lazy="dynamic")
    learning_logs = db.relationship("LearningLog", back_populates="user", lazy="dynamic")

    def set_password(self, plaintext: str) -> None:
        self.password_hash = bcrypt.hashpw(
            plaintext.encode(), bcrypt.gensalt()
        ).decode()

    def check_password(self, plaintext: str) -> bool:
        return bcrypt.checkpw(plaintext.encode(), self.password_hash.encode())

    @property
    def team_membership(self):
        """Returns the single active TeamMember row for this user (users belong to one team)."""
        return self.memberships.first()

    @property
    def team_id(self):
        m = self.team_membership
        return m.team_id if m else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "team_id": self.team_id,
            "created_at": self.created_at.isoformat(),
        }

from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from app.extensions import db, limiter
from app.models.user import User
from app.schemas import RegisterSchema, LoginSchema
from app.utils.validation import validate_or_400
from app.utils.errors import ok, err

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@limiter.limit("10 per hour")          # prevent account-farming
def register():
    data, error = validate_or_400(RegisterSchema(), request.get_json(silent=True) or {})
    if error:
        return error

    if User.query.filter_by(email=data["email"]).first():
        return err("Email already registered", 400)

    user = User(name=data["name"], email=data["email"], role="USER")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return ok({"message": "Registered successfully", "user_id": user.id}, 201)


@auth_bp.post("/login")
@limiter.limit("20 per minute")        # block credential-stuffing
def login():
    data, error = validate_or_400(LoginSchema(), request.get_json(silent=True) or {})
    if error:
        return error

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return err("Invalid credentials", 401)

    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return ok({
        "access_token": token,
        "user_id": user.id,
        "role": user.role,
        "team_id": user.team_id,
    })

from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.utils.errors import forbidden, err


def _load_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def require_auth(f):
    """Verifies JWT and injects `current_user` into kwargs."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _load_user()
        if not user:
            return err("User not found", 401)
        return f(*args, current_user=user, **kwargs)
    return wrapper


def require_team_member(f):
    """Like require_auth but also asserts the user belongs to a team."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _load_user()
        if not user:
            return err("User not found", 401)
        if user.role != "PLATFORM_ADMIN" and not user.team_id:
            return forbidden()
        return f(*args, current_user=user, **kwargs)
    return wrapper


def require_team_admin(f):
    """Requires TEAM_ADMIN or PLATFORM_ADMIN role."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _load_user()
        if not user:
            return err("User not found", 401)
        if user.role not in ("TEAM_ADMIN", "PLATFORM_ADMIN"):
            return forbidden()
        return f(*args, current_user=user, **kwargs)
    return wrapper


def require_platform_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _load_user()
        if not user:
            return err("User not found", 401)
        if user.role != "PLATFORM_ADMIN":
            return forbidden()
        return f(*args, current_user=user, **kwargs)
    return wrapper


def assert_team_owns(resource, current_user):
    """Returns True if the resource.team_id matches the user's team_id.
    PLATFORM_ADMIN bypasses this check."""
    if current_user.role == "PLATFORM_ADMIN":
        return True
    return resource.team_id == current_user.team_id

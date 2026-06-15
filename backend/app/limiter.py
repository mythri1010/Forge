from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Key function falls back to IP; once JWT is decoded the real user identity
# could be used instead, but IP is correct for the auth endpoints where
# we want to block credential-stuffing before any token is issued.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # no global limit — only explicit decorators
    storage_uri="memory://",    # swap for "redis://..." in production
)

from flask import Blueprint

bp = Blueprint("api", __name__)

# These imports are placed here to avoid circular dependencies
from app.api import errors  # noqa: F401
from app.api import routes  # noqa: F401

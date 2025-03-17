from app.main import bp
from flask import current_app


@bp.route("/")
def index():
    return current_app.send_static_file("index.html")
from flask import current_app, render_template, request
# from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response


def wants_json_response():
    return (
        request.accept_mimetypes["application/json"]
        >= request.accept_mimetypes["text/html"]
    )


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return current_app.send_static_file("index.html")


@bp.app_errorhandler(500)
def internal_error(error):
    # db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return (
        "An unexpected error has occurred. The administrator has been "
        "notified. Sorry for the inconvenience!",
        500,
    )

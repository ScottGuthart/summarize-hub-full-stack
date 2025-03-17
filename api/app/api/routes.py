from app import db
from app.api import bp
from flask import jsonify, current_app, send_file
from app.schemas import DataFileSchema, TaskSchema
from app.save_file import save_file
from apifairy import body, response
from app.models import Task
import os

@bp.route("/upload", methods=["POST"])
@body(DataFileSchema, location="form")
@response(TaskSchema)
def upload_data(data):
    """Upload a file for summarization"""
    file = data.get("file")

    filename = file.filename
    root, ext = os.path.splitext(filename)
    fn = save_file(file, root, ext, save=True, make_unique=True)
    ext = ext.lower()

    base_filename = os.path.basename(fn)
    t = Task.launch_task('summarize', f'Summarizing {base_filename}', fn)
    db.session.add(t)
    db.session.commit()

    return t
    
@bp.route("/task/<task_id>/download", methods=["GET"])
def download_task_data(task_id):
    """Download the data for a task"""
    task = Task.query.get_or_404(task_id)

    _, ext = os.path.splitext(task.filename)
    mimetype = "text/csv" if ext == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return send_file(
        task.filename,
        mimetype=mimetype,
        as_attachment=True,
    )
    

@bp.route(
    "/task/<task_id>"
)
@response(TaskSchema)
def get_task(task_id):
    """
    Get the status of a task
    """

    task = Task.query.get_or_404(task_id)
    return task


@bp.errorhandler(404)
def not_found_error(error):
    current_app.logger.error(f"404 error: {error}")
    return jsonify({'error': 'Not Found'}), 404
from app import db
from datetime import datetime
import redis
import rq
from flask import current_app


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    complete = db.Column(db.Boolean, default=False)
    succeeded = db.Column(db.Boolean)
    started_at = db.Column(db.DateTime)
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    filename = db.Column(db.String(128))

    @staticmethod
    def launch_task(name, description, filename, *args, **kwargs):
        current_app.logger.info(f"Launching task: {name} - {description}")
        rq_job = current_app.task_queue.enqueue(
            "app.tasks." + name,
            *args,
            **kwargs,
            job_timeout=current_app.config['RQ_JOB_TIMEOUT']
        )
        task = Task(
            id=rq_job.id,
            name=name,
            description=description[:128] if description else None,
            filename=filename,
        )
        db.session.add(task)
        db.session.commit()
        return task

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100

    def get_progress_message(self):
        job = self.get_rq_job()
        return job.meta.get("progress_message", "") if job is not None else ""

    def __repr__(self):
        if self.complete:
            if self.succeeded:
                status = "SUCCEEDED"
            else:
                status = "FAILED"
        else:
            status = f"{self.get_progress()}%"
        return f"<Task {self.name} {status}>"
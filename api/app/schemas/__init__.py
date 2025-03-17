from apifairy.fields import FileField
from marshmallow import validates, ValidationError, post_dump
from app import ma
import os
from app.models import Task
from flask import current_app
import pandas as pd
import tempfile


class DataFileSchema(ma.Schema):
    file = FileField(
        required=True,
        metadata={"description": "Data file in excel or csv format."},
    )

    @validates("file")
    def validate_file(self, value):
        _, ext = os.path.splitext(value.filename)
        if ext not in [".xlsx", ".csv", ".xls"]:
            raise ValidationError("Unsupported file format: " + ext)
        
        # Validate file size
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if value.content_length > max_size:
            max_mb = max_size / (1024 * 1024)
            msg = f"File too large. Maximum size is {max_mb:.0f}MB"
            raise ValidationError(msg)
            
        # Validate required columns
        try:
            # Save to temporary file first
            with tempfile.NamedTemporaryFile(suffix=ext) as temp_file:
                value.stream.seek(0)
                value.save(temp_file.name)
                
                if ext == '.csv':
                    df = pd.read_csv(temp_file.name)
                else:
                    df = pd.read_excel(temp_file.name)
                    
                if 'Article Content' not in df.columns:
                    msg = ("File must contain a column named "
                           "'Article Content'")
                    raise ValidationError(msg)
                    
        except Exception as e:
            raise ValidationError(f"Error reading file: {str(e)}")
        
        # Reset file pointer to beginning after validation
        value.stream.seek(0)


class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Task
        ordered = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(dump_only=True)
    description = ma.auto_field(dump_only=True)
    complete = ma.auto_field(dump_only=True)
    succeeded = ma.auto_field(dump_only=True)
    last_updated = ma.auto_field(dump_only=True)
    started_at = ma.auto_field(dump_only=True)
    progress = ma.Method("get_progress", dump_only=True)
    progress_message = ma.Method("get_progress_message", dump_only=True)

    def get_progress(self, obj):
        return obj.get_progress()

    def get_progress_message(self, obj):
        return obj.get_progress_message()

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if data.get("last_updated") is not None:
            data["last_updated"] += "Z"
        if data.get("started_at") is not None:
            data["started_at"] += "Z"
        return data

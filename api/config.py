"""Sets up important project configuration variables"""
import os

from dotenv import load_dotenv
import simplejson as json

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

def json_int_float_key_deserializer(obj):
    """
    If obj is a dictionary with keys that are all integers or floats,
    returns the keys as integers or floats instead of strings
    """
    d = json.loads(obj)
    if not isinstance(d, dict):
        return d
    if all(key.isdigit() for key in d):
        return {int(key): value for key, value in d.items()}
    if all(
        key.replace(".", "", 1).isdigit() and key.count(".") < 2 for key in d
    ):
        return {float(key): value for key, value in d.items()}
    return d


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(basedir, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Max Upload Size
    
    # Database
    database_uri = os.environ.get("DATABASE_URL")
    if database_uri is not None and database_uri.startswith("postgres://"):
        database_uri = database_uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = database_uri or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "json_serializer": lambda obj: json.dumps(obj, sort_keys=True),
        "json_deserializer": json_int_float_key_deserializer,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
    RQ_JOB_TIMEOUT = int(os.environ.get("RQ_JOB_TIMEOUT") or 900)

    # LLM
    LLM_MODEL = os.environ.get("LLM_MODEL") or "llama3-chatqa:8b"
# from flask_login import current_user
import os
import tempfile

from flask import current_app


def save_file(data, root=None, ext=None, save=True, user=None, make_unique=False):
    """
    Used to generate and/or save files to the flask instance.
    user: provide to store in a subdirectory with the username
    """
    if not os.path.exists(current_app.instance_path):
        os.mkdir(current_app.instance_path)
    if not os.path.exists(os.path.join(current_app.instance_path, "files")):
        os.mkdir(os.path.join(current_app.instance_path, "files"))

    if user is not None:
        if not os.path.exists(
            os.path.join(current_app.instance_path, "files", user)
        ):
            os.mkdir(os.path.join(current_app.instance_path, "files", user))
        if ext is not None and root is not None:
            filename = os.path.join(
                current_app.instance_path, "files", user, f"{root}.{ext}"
            )
        else:
            filename = os.path.join(current_app.instance_path, "files", user)

    else:
        if ext is not None and root is not None:
            filename = os.path.join(
                current_app.instance_path, "files", f"{root}.{ext}"
            )
        else:
            filename = os.path.join(current_app.instance_path, "files")
    if make_unique:
        filename = get_unique_filename(filename)
    if data and save:
        data.save(filename)
    return filename


def get_unique_filename(original_fn):
    """https://stackoverflow.com/a/183582/11312371"""
    dirname, filename = os.path.split(original_fn)
    prefix, suffix = os.path.splitext(filename)

    fd, unique_fn = tempfile.mkstemp(suffix, prefix + "_", dirname, text=False)
    # return os.fdopen(fd), filename
    os.remove(unique_fn)
    return unique_fn

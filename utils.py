
import os, functools
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
ALLOWED_EXTENSIONS = {"pdf","png","jpg","jpeg","gif"}
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def save_file(file_storage, subfolder:str) -> str | None:
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash("Arquivo não permitido. Envie PDF/Imagem até 20 MB.", "warning")
        return None
    from uuid import uuid4
    name, ext = os.path.splitext(file_storage.filename)
    filename = f"{uuid4().hex}{ext.lower()}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    file_storage.save(path)
    return os.path.relpath(path, start=current_app.root_path)
def admin_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Acesso restrito a administradores.", "warning")
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)
    return wrapped

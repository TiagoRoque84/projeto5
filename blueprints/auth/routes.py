
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm, UserForm
from utils import admin_required

auth_bp = Blueprint("auth", __name__, template_folder='../../templates/auth')

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user, remember=False)
            flash("Bem-vindo!", "success")
            next_page = request.args.get("next") or url_for("main.index")
            return redirect(next_page)
        flash("Credenciais inválidas ou usuário inativo.", "danger")
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/usuarios")
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.username).all()
    return render_template("auth/users_list.html", users=users)

@auth_bp.route("/usuarios/novo", methods=["GET","POST"])
@login_required
@admin_required
def users_new():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("Usuário já existe.", "warning")
        else:
            u = User(username=form.username.data.strip(), role=form.role.data, active=True)
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash("Usuário criado.", "success")
            return redirect(url_for("auth.users_list"))
    return render_template("auth/users_form.html", form=form)

@auth_bp.route("/usuarios/<int:user_id>/reset", methods=["POST"])
@login_required
@admin_required
def users_reset(user_id):
    u = User.query.get_or_404(user_id)
    u.set_password("senha123")
    db.session.commit()
    flash("Senha redefinida para 'senha123'.", "info")
    return redirect(url_for("auth.users_list"))

@auth_bp.route("/usuarios/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def users_toggle(user_id):
    u = User.query.get_or_404(user_id)
    u.active = not u.active
    db.session.commit()
    flash("Status atualizado.", "success")
    return redirect(url_for("auth.users_list"))

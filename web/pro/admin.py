from flask import Blueprint, render_template, request, redirect,flash,url_for
from flask_login import login_user,logout_user,current_user
from werkzeug.security import check_password_hash
from .model import User
from functools import wraps

admin = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required", "error")
            return redirect(url_for("auth.login"))  # or "admin.admin_login"
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/admin-login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.is_admin and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in', category='success')
            return render_template('backend/adminDash.html')
        else:
            flash('Invalid Admin Credentials', category='error')
    return render_template('backend/base.html')

@admin.route("/admin/dashboard")
@admin_required
def Adashboard():
    return render_template('backend/adminDash.html')
from flask import Blueprint, render_template, redirect,flash,url_for
from flask_login import login_user,logout_user,current_user
from werkzeug.security import check_password_hash
from .model import User
from functools import wraps
from .form import LoginForm
from . import db
from datetime import datetime

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

        form = LoginForm()

        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            admin = User.query.filter_by(email=email).first()


            if admin:
                if check_password_hash(admin.password, password):
                    login_user(admin, remember=False)
                    User.previous_login = User.last_login
                    User.last_login = datetime.utcnow()
                    db.session.commit()
                    flash("Welcome admin", category="success")
                    return redirect(url_for('admin_view.Adashboard'))
                else:
                     flash("Incorrect password", category="error")
            else:
                return redirect(url_for('views.home'))
        return render_template('backend/adminAuth.html', form=form)

@admin.route("/admin-logout")
@admin_required
def Alogout():
    logout_user()
    flash("logged out", category="success")
    return redirect(url_for('admin.login'))

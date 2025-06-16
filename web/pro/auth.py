from flask import Blueprint, render_template, request, flash, redirect, url_for,session
from .model import User
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_wtf.csrf import generate_csrf
from functools import wraps

auth=Blueprint('auth', __name__)

def user_required(f):
	@wraps(f)
	def decorated_function(*arg, **kwargs):
		if not current_user.is_authenticated or current_user.is_admin:
			flash("Member users only!", category="error")
			return redirect(url_for('auth.signup'))
		return f(*arg, **kwargs)
	return decorated_function

@auth.route("/signup", methods=['GET' ,'POST'])
def signup():
     csrf_token = generate_csrf()
     if request.method == 'POST':
               email=request.form.get('email')
               fName=request.form.get('fName')
               lName=request.form.get('lName')
               password=request.form.get('password')
               cPassword=request.form.get('confirm-password')

               user = User.query.filter_by(email=email).first()

               if user:
                    flash('user already exists', category='error') 
               elif is_admin_email(email):
                    flash("No", category="error")
               elif not email or len(email) < 4:
                    flash("Email is not valid", category="error")
               elif request.form.get('is_admin'):
                    flash("nah not today", category="error")
               elif not fName or len(fName) < 2:
                    flash("Invalid Name", category="error")
               elif password != cPassword:
                    flash("Passwords don\'t match",category="error")
               elif not password or len(password) < 8:
                    flash("Password must be greate than 8 characters", category="error")
               else:
                    new_user = User(email=email, f_name=fName, l_name=lName, password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16))
                    User.last_login = datetime.utcnow()
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=False)
                    flash('Account created', category='success')
                    return redirect(url_for('user_view.user_dashboard'))
                    

     return render_template('frontend/signup.html', csrf_token=csrf_token)

@auth.route("/login", methods=['GET', 'POST'])
def login():
     csrf_token = generate_csrf()

     if request.method == 'POST':
          email=request.form.get('email')
          password=request.form.get('password')

          user = User.query.filter_by(email=email).first()

          if user:
               if user and user.is_admin:
                     flash("no", category="error")
                     return redirect(url_for('views.home'))
               if check_password_hash(user.password, password):
                    login_user(user, remember=False)
                    User.previous_login = User.last_login
                    User.last_login = datetime.utcnow()
                    db.session.commit()
                    flash('logged in', category='success')
                    return redirect(url_for('user_view.user_dashboard'))
               else:
                    flash('Incorrect Password', category='error')
          else:
               flash('user doesnot exists', category='error')
     return render_template('frontend/auth.html', csrf_token=csrf_token)

@auth.route("/logout")
@login_required
@user_required

def logout():
     logout_user()
     flash('Logged out', category='success')
     return redirect(url_for('auth.login'))



def is_admin_email(email):
    return User.query.filter_by(email=email, is_admin=True).first() is not None


from flask import Blueprint, render_template, request, flash, redirect, url_for
from .model import User
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user

auth=Blueprint('auth', __name__)

@auth.route("/signup", methods=['GET' ,'POST'])
def signup():
    if request.method == 'POST':
          email=request.form.get('email')
          fName=request.form.get('fName')
          lName=request.form.get('lName')
          password=request.form.get('password')
          cPassword=request.form.get('confirm-password')

          user = User.query.filter_by(email=email).first()

          if user:
               flash('user already exists', category='error')
          elif len(email) < 4:
               flash("Email is not valid", category="error")
          elif fName and len(fName) < 2:
               flash("Invalid Name", category="error")
          elif password != cPassword:
               flash("Passwords don\'t match",category="error")
          elif not password and len(password) < 8:
               flash("Password must be greate than 8 characters", category="error")
          else:
               new_user = User(email=email, f_name=fName, L_name=lName, password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16))
               db.session.add(new_user)
               db.session.commit()
               login_user(new_user, remember=True)
               flash('Account created', category='success')
               return redirect(url_for('views.user_dashboard'))
               

    return render_template('frontend/signup.html')

@auth.route("/login", methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
          email=request.form.get('email')
          password=request.form.get('password')
          
          user = User.query.filter_by(email=email).first()

          if user:
               if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    flash('logged in', category='success')
                    return redirect(url_for('views.user_dashboard'))
               else:
                    flash('Incorrect Password', category='error')
          else:
               flash('user doesnot exists', category='error')
     return render_template('frontend/auth.html')

@auth.route("/logout")
@login_required
def logout():
     logout_user()
     flash('Logged out', category='success')
     return redirect(url_for('auth.login'))

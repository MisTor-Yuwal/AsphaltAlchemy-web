from flask import Flask
import os 
from os import path
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db=SQLAlchemy()
migrate=Migrate()
DB_NAME = "AsphaltDatabase.db"
csrf=CSRFProtect()


def create_app():
	app = Flask(__name__)
	app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
	# app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

	app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
	app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
	app.config['REMEMBER_COOKIE_HTTPONLY'] = True
	app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)
	app.config['SESSION_PROTECTION'] = 'strong'

	
	app.config['SERVER_NAME'] = 'localhost:1111'
	app.config['APPLICATION_ROOT'] = '/'
	app.config['PREFERRED_URL_SCHEMA'] = 'http'

	app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
	app.config['GALLERY_FOLDER'] = os.path.join(app.root_path, 'static/gallery')
	app.config['USER_PROFILE'] = os.path.join(app.root_path, 'static/users')

	os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
	os.makedirs(app.config['GALLERY_FOLDER'], exist_ok=True)
	os.makedirs(app.config['USER_PROFILE'], exist_ok=True)

	db.init_app(app)
	csrf.init_app(app)
	migrate.init_app(app, db)

	from .views import views
	from .auth import auth
	from .admin import admin
	from .admin_view import admin_view as aview
	from .user_view import user_view as uview
	app.register_blueprint(views, url_prefix="/")
	app.register_blueprint(auth, url_prefix="/")	
	app.register_blueprint(admin, url_prefix="/")
	app.register_blueprint(aview, url_prefix="/admin")
	app.register_blueprint(uview, url_prefix="/")

	from .model import User, Product
	create_database(app)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(Uid):
		return User.query.get(int(Uid))
	
	
	return app	

def create_database(app):
	if not path.exists('pro/' + DB_NAME):
		with app.app_context():
			db.create_all()
			print('Database created!')
			print(app.config['SQLALCHEMY_DATABASE_URI'])
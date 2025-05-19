from flask import Flask
import os 
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db=SQLAlchemy()
DB_NAME = "AsphaltDatabase.db"


def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
	app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
	db.init_app(app)

	from .views import views
	from .auth import auth
	from .admin import admin
	app.register_blueprint(views, url_prefix="/")
	app.register_blueprint(auth, url_prefix="/")	
	app.register_blueprint(admin, url_prefix="/")

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
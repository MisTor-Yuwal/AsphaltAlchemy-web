from flask import Blueprint, render_template


views = Blueprint("views", __name__)

@views.route("/")
def home():
	return render_template("frontend/home.html")

@views.route("/product")
def products():
	return render_template("frontend/product.html")

@views.route("/gallery")
def gallery():
	return render_template("frontend/gallery.html")

@views.app_errorhandler(404)
def page_not_found(e):
	return render_template("frontend/pagenotfound.html")
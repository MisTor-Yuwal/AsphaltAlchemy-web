from flask import Blueprint, render_template
from flask_login import login_required


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

@views.route("/dashboard")
@login_required
def user_dashboard():
	return render_template("frontend/user_dash/dash.html")

@views.route("/user_order")
@login_required
def users_order():
	return render_template("frontend/user_dash/order.html")

@views.route("/user_info")
@login_required
def user_info():
	return render_template("frontend/user_dash/info.html")

@views.route("/user_cart")
@login_required
def user_cart():
	return render_template("frontend/user_dash/cart.html")

@views.app_errorhandler(404)
def page_not_found(e):
	return render_template("frontend/pagenotfound.html")
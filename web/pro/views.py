from flask import Blueprint, render_template, current_app
from .model import Product, Gallery
import os

views = Blueprint("views", __name__)

@views.route("/")
def home():
	return render_template("frontend/home.html")

@views.route("/product")
def products():
	lproducts = Product.query.all()

	for product in lproducts:
		if product.offers:
			product.recent_offer = max(product.offers, key=lambda o: o.created_at)
		else:
			product.recent_offer = None
	return render_template("frontend/product.html", products=lproducts)

@views.route("/product/<int:productID>")
def product_detail(productID):
	product = Product.query.filter_by(productID=productID).first_or_404()
	lproducts = Product.query.all()

	for p in lproducts:
		if p.offers:
			p.recent_offer = max(p.offers, key=lambda o: o.created_at)
		else:
			p.recent_offer = None

	return render_template('frontend/product_detail.html', product=product, products=lproducts)

@views.route("/gallery")
def gallery():
	photos=Gallery.query.all()
	photo_folder = current_app.config['GALLERY_FOLDER']

	for photo in photos:
		photo_path = os.path.join(photo_folder, photo.picture_file)
		photo.exists = os.path.exists(photo_path)

	return render_template("frontend/gallery.html", photos=photos)

@views.app_errorhandler(404)
def page_not_found(e):
	return render_template("frontend/pagenotfound.html")
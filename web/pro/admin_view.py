from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required,current_user
from functools import wraps
from . import db
import os
from .model import User, Product, Gallery, ProductImage,Offer, Size
from .productForm import ProductForm, GalleryForm, Offerform, SelectProductForm
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from builtins import zip
from datetime import datetime

admin_view=Blueprint("admin_view", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You must be an admin to access this page.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function



@admin_view.route("/dashboard")
@admin_required
@login_required
def Adashboard():
    return render_template('backend/adminDash.html', previous_login=current_user.previous_login)

@admin_view.route("/addProduct", methods=['GET', 'POST'])
@admin_required
@login_required
def addProduct():

    form = ProductForm()
    form.sizes.data = []
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        quantity = form.quantity.data
        price = form.price.data
        color = form.color.data
        material = form.material.data
        weight = form.weight.data
        percentage = form.percentage.data

        new_product = Product(productName=name, productDetail=description, productQuantity=quantity, productPrice=price, productWeight=weight, productColor=color, productMaterial=material, productPercentage=percentage)
        db.session.add(new_product)
        db.session.flush()

        for size_label in form.sizes.data:
            size = Size(label= size_label, product_id = new_product)
            db.session.add(size)

        db.session.commit()

        files = form.image.data

        for file in files:
            if file: 
                filename= secure_filename(file.filename)
                upload_path = current_app.config['UPLOAD_FOLDER']
                file.save(os.path.join(upload_path, filename))

                image = ProductImage(file_name=filename, product_id=new_product.productID)
                db.session.add(image)

        db.session.commit()
        flash("Product added", category="success")
        return redirect(url_for('admin_view.addProduct'))
    return render_template('backend/addProduct.html', form=form)

@admin_view.route("/addPhoto", methods=['GET','POST'])
@admin_required
@login_required
def addPhoto():

    form = GalleryForm()

    if form.validate_on_submit():
        title=form.title.data
        detail=form.description.data
        photo=form.photo.data
        
        filename=secure_filename(photo.filename)
        upload_path = current_app.config['GALLERY_FOLDER']
        photo.save(os.path.join(upload_path, filename))

        new_image = Gallery(title=title, description=detail, picture_file=filename)
        db.session.add(new_image)
        db.session.commit()

        flash("Image added to the Gallery", category="success")
        return redirect(url_for('admin_view.addPhoto'))
    return render_template('backend/addPhoto.html', form=form)

@admin_view.route("/offer", methods=['GET', 'POST'])
@admin_required
@login_required

def issueOffer():
    form = Offerform()

    if form.validate_on_submit():
        if form.choose.data == 'all':
            products =Product.query.all()

            for product in products:
                offer = Offer(
                    start_date = form.start_date.data,
                    end_date = form.end_date.data,
                    discount_percentage = form.discount.data,
                    product_id = product.productID
                )
                db.session.add(offer)
        else:
            return redirect(url_for('admin_view.select_product', start_date =form.start_date.data, end_date = form.end_date.data, discount_percentage=form.discount.data))

        db.session.commit()
        flash('Success', category='success')
        return redirect(url_for('admin_view.issueOffer'))
    return render_template('backend/offer.html', form=form)

@admin_view.route("/select_product_for_offer", methods=['POST', 'GET'])
@admin_required
@login_required
def select_product():
    form = SelectProductForm()
    products = Product.query.all()
    form.product.choices = [(p.productID, p.productName)for p in products]

    if form.validate_on_submit():
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        discount_percentage = int(request.form.get('discount_percentage'))

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        for pid in form.product.data:
            offer = Offer(
                start_date = start_date,
                end_date = end_date,
                discount_percentage = discount_percentage,
                product_id = pid
            )
            db.session.add(offer)
        db.session.commit()
        flash('Success' , category='success')
        return redirect(url_for('admin_view.issueOffer'))
    else:
        print(form.errors)
    return render_template('backend/chooseProductOffer.html', form=form, products=products,zip=zip)



@admin_view.route("/report")
@admin_required
@login_required
def report():
    return render_template('backend/report.html')

@admin_view.route("/order")
@admin_required
@login_required
def order():
    products = Product.query.all()

    return render_template('backend/incommingOrder.html', products=products)

@admin_view.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    flash("File is too large, max size is 16 MB", "error")
    return redirect(url_for('admin_view.addProduct'))

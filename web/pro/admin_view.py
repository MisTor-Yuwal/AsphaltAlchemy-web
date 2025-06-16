from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, jsonify, abort
from flask_login import login_required,current_user
from sqlalchemy import func
from functools import wraps
from . import db,socketio
from flask_socketio import emit
import os
from .model import User, Product, Gallery, ProductImage,Offer, Size, Order,OrderItem
from .productForm import ProductForm, GalleryForm, Offerform, SelectProductForm
from .DiscardForm import EditProductForm, SelectOfferForm
from .statusForm import StatusForm
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from builtins import zip
from datetime import datetime
from sqlalchemy.orm import joinedload

admin_view=Blueprint("admin_view", __name__)

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated or not current_user.is_admin:
#             flash('You must be an admin to access this page.', 'error')
#             return redirect(url_for('admin.login'))
#         return f(*args, **kwargs)
#     return decorated_function
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Admin access required"}), 403
            else:
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_view.route("/dashboard")
@login_required
@admin_required

def Adashboard():
    return render_template('backend/adminDash.html', previous_login=current_user.previous_login)

@admin_view.route("/addProduct", methods=['GET', 'POST'])
@login_required
@admin_required

def addProduct():

    form = ProductForm()
    form.sizes.data = form.sizes.data or []
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

        if form.sizes.data:
            for size_label in form.sizes.data:
                size = Size(label= size_label, product_id = new_product.productID)
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
        data = {
            'id ' : new_product.productID,
            'name ': new_product.productName,
            'quantity' : new_product.productQuantity,
            'price' : new_product.productPrice,
            'color' : new_product.productColor,
            'material' : new_product.productMaterial,
            'weight'  : new_product.productWeight,
            'percentage' : new_product.productPercentage,
            'detail' : new_product.productDetail,
            'image' : new_product.image[0].file_name if new_product.image else 'static/images/non.jpeg'
        }
        socketio.emit('new_product', data, namespace='/')
        flash("Product added", category="success")
        return redirect(url_for('admin_view.addProduct'))
    return render_template('backend/addProduct.html', form=form)

@admin_view.route("/edit_or_delete_product" ,methods=['GET','POST'])
@login_required
@admin_required

def edit_delete_product():
    form = EditProductForm()
    products = Product.query.all()
    productform = ProductForm()

    form.select_to_edit_delete.choices = [(p.productID, p.productName) for p in products]

    if form.validate_on_submit():
        selected_id = form.select_to_edit_delete.data
        
        if form.delete.data:
            product = Product.query.get_or_404(selected_id)

            for image in product.image:
                file_path = os.path.join(current_app.root_path, 'static/uploads/' ,image.file_name)
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    flash({e}, category="error")
            db.session.delete(product)

        db.session.commit()
        flash("Product Deleted", category="success")
        return redirect(url_for('admin_view.edit_delete_product'))
    
    return render_template('backend/editOrDeleteProduct.html', form=form, products=products,zip=zip, productform=productform)


@admin_view.route("/edit_product/<int:productID>", methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(productID):
    product = Product.query.get_or_404(productID)
    productform = ProductForm()

    if productform.validate_on_submit():
        if productform.update.data:
            product = Product.query.get_or_404(productID)

            print("Submitted:", request.method == 'POST')
            print("Form valid:", productform.validate_on_submit())
            print("Errors:", productform.errors)


            product.productName = productform.name.data
            product.productQuantity = productform.quantity.data
            product.productPrice = productform.price.data
            product.productColor = productform.color.data
            product.productWeight = productform.weight.data
            product.productMaterial = productform.material.data
            product.productPercentage = productform.percentage.data
            product.productDetail = productform.description.data

            product.productSizes = productform.sizes.data
            db.session.commit()
        flash("Product updated", category="success")
        return redirect(url_for('admin_view.edit_delete_product'))
    return redirect(url_for('admin_view.edit_delete_product'))


@admin_view.route("/get_product_images/<int:productID>/images")
@login_required
@admin_required
def get_images_of_product(productID):
    product = Product.query.get_or_404(productID)
    images = [img.file_name for img in product.image]
    return jsonify(images)


@admin_view.route("/get_product/<int:productID>")
@login_required
@admin_required
def get_product(productID):
    product = Product.query.get(productID)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    images = [img.file_name for img in product.image or []] 
    sizes = [clothing.label for clothing in product.productSizes or []]

    return jsonify({
        "productName": product.productName,
        "productPrice": product.productPrice,
        "productDetail": product.productDetail,
        "productColor" : product.productColor,
        "productQuantity" : product.productQuantity,
        "productWeight": product.productWeight,
        "productMaterial" : product.productMaterial,
        "productPercentage" : product.productPercentage,
        "productSizes" : sizes,
        "productImages" : images
    })

@admin_view.route("/addPhoto", methods=['GET','POST'])
@login_required
@admin_required

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
@login_required
@admin_required

def issueOffer():
    form = Offerform()

    if form.validate_on_submit():
        if form.choose.data == 'all':
            products =Product.query.all()

            offer = Offer(
                start_date = form.start_date.data,
                end_date = form.end_date.data,
                discount_percentage = form.discount.data,
                products = products
            )
            db.session.add(offer)
        else:
            return redirect(url_for('admin_view.select_product', start_date =form.start_date.data, end_date = form.end_date.data, discount_percentage=form.discount.data))

        db.session.commit()
        flash('Success', category='success')
        return redirect(url_for('admin_view.issueOffer'))
    return render_template('backend/offer.html', form=form)


@admin_view.route("/discard_offer", methods=['GET', 'POST'])
@login_required
@admin_required

def remove_offer():
    offers = Offer.query.options(joinedload(Offer.products)).all()

    seen_offer_ids = set()
    offers_list = []

    for o in offers:
        if o.id not in seen_offer_ids:
            offers_list.append({'offer': o, 'products': o.products})
            seen_offer_ids.add(o.id)
    form = SelectOfferForm()
    form.offer.choices = [(str(item['offer'].id), "") for item in offers_list]


    if form.validate_on_submit():
        selected_id = form.offer.data
        for id in selected_id:
            offer = Offer.query.get_or_404(id)
            db.session.delete(offer)
        db.session.commit()
        flash('Offer removed',category='success')
        return redirect(url_for('admin_view.remove_offer'))

    return render_template('backend/discardOffer.html', offers =offers_list, form=form, zip=zip)


@admin_view.route("/select_product_for_offer", methods=['POST', 'GET'])
@login_required
@admin_required

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

        selected_products = Product.query.filter(Product.productID.in_(form.product.data)).all()
        offer = Offer(
            start_date = start_date,
            end_date = end_date,
            discount_percentage = discount_percentage,
            products = selected_products
        )
        db.session.add(offer)
        db.session.commit()
        flash('Success' , category='success')
        return redirect(url_for('admin_view.issueOffer'))
    else:
        print(form.errors)
    return render_template('backend/chooseProductOffer.html', form=form, products=products,zip=zip)



@admin_view.route("/report")
@login_required
@admin_required

def report():

    return render_template('backend/report.html')

@admin_view.route("/order", methods=['GET', 'POST'])
@login_required
@admin_required

def order():
    products = Product.query.all()
    form = StatusForm()

    orders = Order.query.order_by(Order.created_at.desc()).all()
    order_forms = {order.order_id: StatusForm(orderID=order.order_id, status=order.status) for order in orders}


    for order_id, form in order_forms.items():
        if form.validate_on_submit() and int(form.orderID.data) == order_id:
            order_to_update = Order.query.get(order_id)
            if order_to_update:
                order_to_update.status = form.status.data
                db.session.commit()
                flash(f"Order {order_id} status updated.", "success")
            else:
                flash("Order not found", "error")
            return redirect(url_for('admin_view.order'))

    return render_template('backend/incommingOrder.html', products=products, orders=orders, order_forms=order_forms)


@admin_view.route("/order/<int:order_id>/details")
@login_required
@admin_required
def get_order_details(order_id):

    if not current_user.is_admin:
        abort(403)
    
    else:
        order = Order.query.get_or_404(order_id)
        user = order.user
        delivery_location = order.user.delivery_location
        items = OrderItem.query.filter_by(order_id=order_id).all()

        return jsonify({
            'order_id' : order.order_id,
            'created_at' : order.created_at,
            'total_price' : order.total_price,
            'user' : {
                'f_name' : user.f_name,
                'l_name' : user.l_name,
                'phone' : user.phone,
                'email' : user.email,
                'delivery_location' :{
                    'state' : delivery_location.state,
                    'district' : delivery_location.district,
                    'city' : delivery_location.city,
                    'ward' : delivery_location.ward,
                    'street' : delivery_location.street
                }
            },
            'items' : [{
                'product_name' : item.product.productName,
                'product_price' : item.product.productPrice,
                'product_color' : item.product.productColor,
                'product_quantity' : item.quantity,
                'product_image' : item.product.image[0].file_name,
                'product_size' : item.size
            }for item in items  
            ]
        })

# @admin_view.route("/profit-loss")
# @login_required
# @admin_required

# def profit_loss_data():
#     data = (
#         db.session.query(
#             func.date(Order.created_at).label('date'),
#             func.sum(OrderItem.price * OrderItem.quantity).label('revenue'),
#             func.sum(Product.productPrice * OrderItem.quantity).label('cost')
#         )
#         .join(OrderItem, OrderItem.order_id == Order.order_id)
#         .join(Product, Product.productID ==  OrderItem.product_id)
#         .group_by(func.date(Order.created_at))
#         .order_by(func.date(Order.created_at))
#         .all()
#     )
#     result = []
#     for row in data:
#         profit = (row.revenue or 0) - (row.cost or 0)
#         result.append({
#             'date': row.date,
#             'profit': round(profit, 2)
#         })

#     return jsonify(result)



@admin_view.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    flash("File is too large, max size is 16 MB", "error")
    return redirect(url_for('admin_view.addProduct'))

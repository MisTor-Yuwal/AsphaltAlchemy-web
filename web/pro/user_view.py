from flask import Blueprint, render_template, flash, redirect,url_for, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from .productForm import EditProfileForm, UserLocationForm, DeliveryLocationForm
from .DiscardForm import AddToCartForm
from .data.location_data import STATE_AND_DISTRICTS
from . import db
from .model import User, UserImage, UserLocation, DeliveryLocation, Product, Cart, Order, OrderItem
import os
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date

user_view=Blueprint("user_view", __name__)

csrf = CSRFProtect()


def user_required(f):
	@wraps(f)
	def decorated_function(*arg, **kwargs):
		if not current_user.is_authenticated:
			flash("Member users only!", category="error")
			return redirect(url_for('auth.signup'))
		elif current_user.is_admin:
			flash("This is not for you", category="error")
			return redirect(url_for('admin.login'))
		return f(*arg, **kwargs)
	return decorated_function

@user_view.route("/dashboard")
@login_required
@user_required

def user_dashboard():
	user_id = current_user.id

	orders = Order.query.filter_by(user_id = user_id).all()

	orderMade = len(orders)
	cart_items = Cart.query.filter_by(user_id = user_id).all()

	itemInCart = len(cart_items)

	return render_template('frontend/user_dash/dash.html',orderMade=orderMade,itemInCart=itemInCart)

@user_view.route("/user_order")
@login_required
@user_required

def users_order():
	userid = current_user.id
	orders = Order.query.filter_by(user_id=userid).order_by(Order.created_at.desc()).all()

	return render_template('frontend/user_dash/order.html', orders=orders)


@user_view.route("/<int:order_id>/details", methods=['GET'])
@login_required
@user_required
def get_myorder_items(order_id):
	if not current_user.is_authenticated:
		abort(403)
	else :
		order = Order.query.get_or_404(order_id)
		items = OrderItem.query.filter_by(order_id=order_id).all()

		milapTotal = 0
		for item in items:
			milapTotal += item.price

		return jsonify({
			'order_id' : order.order_id,
			'created_at' : order.created_at,
			'total_price' : order.total_price,
			'milapTotal' : milapTotal,
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

@user_view.route("/user_info")
@login_required
@user_required

def user_info():
	form = UserLocationForm()
	dform = DeliveryLocationForm()

	image_path = os.path.join(current_app.root_path, 'static', 'users', current_user.image.file_name) if current_user.image else None
	has_image = os.path.isfile(image_path) if image_path else False
	
	return render_template('frontend/user_dash/info.html', has_image=has_image, form=form , dform=dform)

@user_view.route("/update-info",methods=['GET','POST'])
@login_required
@user_required

def update_info():
	lform = UserLocationForm()
	form = EditProfileForm()

	if form.validate_on_submit():
		current_user.f_name = form.first_name.data
		current_user.l_name = form.last_name.data
		current_user.email = form.email.data
		current_user.phone = form.phone.data
		img = form.image.data

		if img and hasattr(img, 'filename') and img.filename:
			filename=secure_filename(img.filename)
			upload_path = current_app.config['USER_PROFILE']

			old_img=UserImage.query.filter_by(user_id = current_user.id).first()
			if old_img:
				old_file_path = os.path.join(upload_path, old_img.file_name)

				if os.path.exists(old_file_path):
					os.remove(old_file_path)
				old_img.file_name = filename

			else: 
				user_img = UserImage(file_name = filename, user_id = current_user.id)
				db.session.add(user_img)
			img.save(os.path.join(upload_path, filename))
		db.session.commit()
		flash("Profile Updated", category="success")
		return redirect(url_for('user_view.user_info'))
	
	if request.method == 'GET':
		form.first_name.data = current_user.f_name
		form.last_name.data = current_user.l_name
		form.email.data = current_user.email
		form.phone.data = current_user.phone

	return render_template("frontend/user_dash/updateInfo.html", form=form, lform=lform)

@user_view.route("/update-location", methods=['GET', 'POST'])
@login_required
@user_required

def update_location():
	form = UserLocationForm()

	if form.state.data :
		form.district.choices = get_district_choices(form.state.data)
	else :
		form.district.data = []

	if form.validate_on_submit():
		if not current_user.location:
			state = form.state.data
			district = form.district.data
			city = form.city.data
			ward = form.ward.data
			street = form.streetAddress.data

			new_location = UserLocation(state=state, district=district, city=city, ward=ward, street=street, user_id = current_user.id)
			db.session.add(new_location)
			db.session.commit()
			flash("location added", category="success")
			return redirect(url_for('user_view.user_info'))
		else :
			current_user.location.state = form.state.data
			current_user.location.district = form.district.data
			current_user.location.city = form.city.data
			current_user.location.ward = form.ward.data
			current_user.location.street = form.streetAddress.data

			db.session.commit()
			flash("location Updated", category="success")
			return redirect(url_for('user_view.user_info'))
			

	if request.method == 'GET':
		if current_user.location:
			form.state.data = current_user.location.state
			form.district.data = current_user.location.district
			form.city.data = current_user.location.city
			form.ward.data = current_user.location.ward
			form.streetAddress.data = current_user.location.street
		else :
			form.state.data = 'Not Set'
			form.district.data  = 'Not Set'
			form.city.data = 'Not Set'
			form.ward.data = '0'
			form.streetAddress.data = 'Not Set'
	
	return render_template('frontend/user_dash/updateLocation.html', form=form)

@user_view.route("/update_delivery_location", methods=['GET', 'POST'])
@login_required
@user_required

def update_delivery_location():
	form = UserLocationForm()
	dform = DeliveryLocationForm()

	if dform.delivery_state.data :
		dform.delivery_district.choices = get_district_choices(dform.delivery_state.data)
	else :
		dform.delivery_district.data = []

	if dform.validate_on_submit():
		if not current_user.delivery_location:
			state = dform.delivery_state.data
			district = dform.delivery_district.data
			city = dform.delivery_city.data
			ward = dform.delivery_ward.data
			street = dform.delivery_street.data

			new_delivery_location = DeliveryLocation(
				state = state, district = district, city = city, ward = ward,
				street = street, user_id = current_user.id
			)

			db.session.add(new_delivery_location)
			db.session.commit()
			flash("Delivery location Added" , category="success")
			return redirect(url_for('user_view.user_info'))
		
		else :
			current_user.delivery_location.state = dform.delivery_state.data
			current_user.delivery_location.district = dform.delivery_district.data
			current_user.delivery_location.city = dform.delivery_city.data
			current_user.delivery_location.ward = dform.delivery_ward.data
			current_user.delivery_location.street = dform.delivery_street.data

			db.session.commit()
			flash("Delivery Location updated", category="success")
			return redirect(url_for('user_view.user_info'))

	if request.method == 'GET':
		if current_user.delivery_location:
			dform.delivery_state.data = current_user.delivery_location.state
			dform.delivery_district.data = current_user.delivery_location.district
			dform.delivery_city.data = current_user.delivery_location.city
			dform.delivery_ward.data = current_user.delivery_location.ward
			dform.delivery_street.data = current_user.delivery_location.street
		
		else :
			dform.delivery_state.data = 'none'
			dform.delivery_district.data = 'none'
			dform.delivery_city.data = 'none'
			dform.delivery_ward.data = '0'
			dform.delivery_street.data = 'none'

	return render_template('frontend/user_dash/updateDeliveryLocation.html', form=form, dform = dform)


@user_view.route('/add-to-cart', methods=['POST'])
@login_required
@user_required
def add_to_cart():
	
	try:
		data = request.get_json()

	except Exception as e:
		return jsonify({'success': False, 'message': f'JSON decode failed: {str(e)}'}), 400

	product_id = data.get('product_id')
	size = data.get('size')

	if not product_id or not size:
		return jsonify({'success': False, 'message': 'Missing product_id or size'}), 400

	product = Product.query.get(product_id)
	if not product:
		return jsonify({'success': False, 'message': 'Product not found'}), 404

	cart_product = Cart(product_id = product_id, user_id = current_user.id, size = size )
	db.session.add(cart_product)
	db.session.commit()
		
	return jsonify({
        'success': True,
        'product': {
            'id': product.productID,
            'name': product.productName,
            'price': product.productPrice,
			'image' : [{'file_name': img.file_name} for img in product.image]
        },
        'size': size,
    })


@user_view.route("/get_cart_items", methods=['GET'])
@login_required
@user_required
def get_cart_items():
	cart_items = Cart.query.filter_by(user_id = current_user.id).all()

	items_json = [
		{
			'product_id' : item.product_id,
			'product_name' : item.product.productName,
			'product_price' : item.product.pricePrice,
			'product_size' : item.size,
			'product_quantity' : item.quantity,
			'product_color' : item.product.productColor,
			'image_file' : item.product.image[0].file_name
		} for item in cart_items
	]
	return jsonify({'items' : items_json})




@user_view.route("/get_district", methods=['POST'])
@login_required
@user_required

def get_district():
	state = request.json.get('state')
	districts = STATE_AND_DISTRICTS.get(state, [])
	return jsonify({'districts' : districts})


@user_view.route("/user_cart/")
@login_required
@user_required

def user_cart():
	milap = AddToCartForm()

	user_id = current_user.id
	cart_items = Cart.query.filter_by(user_id=user_id).all()
	today = date.today()

	cart_data= []
	total = 0
	total_original = 0
	total_discount = 0


	totalitem=len(cart_items)
	totalPrice=0
	for item in cart_items:
		product = item.product
		quantity = item.quantity
		price = product.productPrice
		id = item.product_id
		size = item.size

		discount = 0
		discounted_price = price

		valid_offers = [offer for offer in product.offers if offer.start_date <= today <=offer.end_date ]
		if valid_offers:
			latest_offer = sorted(valid_offers, key=lambda o: o.created_at, reverse=True)[0]
			discount = latest_offer.discount_percentage
			discounted_price = round(price * (1 - discount/100), 2)
			
		item_total = discounted_price * quantity
		total += item_total
		total_original += (price * quantity)
		total_discount += (price - discounted_price) * quantity

		cart_data.append({
			'product': product,
			'quantity': quantity,
			'original_price': price,
			'discounted_price': discounted_price,
			'discount': discount,
			'item_total': item_total,
			'id' : id,
			'size' : size
		})
		totalPrice += item.product.productPrice
	return render_template('frontend/user_dash/cart.html', cart_items=cart_data, milap = milap, totalitem=totalitem, totalPrice = totalPrice,total=round(total, 2), total_discount=round(total_discount, 2))

@user_view.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
@login_required
@user_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()

    db.session.delete(cart_item)
    db.session.commit()

    flash('Item removed from cart', 'success')
    return redirect(url_for('user_view.user_cart'))


@user_view.route("/checkout", methods=['POST'])
@login_required
@user_required
def checkout():
	user_id =current_user.id
	deliveryLocation = DeliveryLocation.query.filter_by(user_id=user_id).first()

	if not deliveryLocation:
		flash("Please set your delivery location before checking out.", category="success")
		return redirect(url_for('user_view.update_delivery_location'))



	cart_items = Cart.query.filter_by(user_id = user_id).all()

	if not cart_items:
		flash("Cart is empty", category="error")
		return redirect(url_for('user_view.user_cart'))
	
	total_price = 0
	order = Order(user_id=user_id, total_price=0)  
	db.session.add(order)
	db.session.flush()  
 
	for item in cart_items:
		product = item.product

		latest_offer = (
			product.offers and
			sorted(product.offers, key=lambda x: x.created_at, reverse=True)[0]
		)
		discount = latest_offer.discount_percentage if latest_offer else 0
		final_price = product.productPrice * (1 - discount / 100)

		order_item = OrderItem(
			order_id=order.order_id,
			product_id=product.productID,
			quantity=item.quantity,
			price=final_price,
			size = item.size
		)

		total_price += final_price * item.quantity
		db.session.add(order_item)

		order.total_price = total_price
		db.session.commit()
	Cart.query.filter_by(user_id=user_id).delete()
	db.session.commit()
	flash("Order placed successfully!", "success")
	return redirect(url_for('user_view.users_order'))



def get_district_choices(state):
	return [(d, d) for d in STATE_AND_DISTRICTS.get(state, [])]
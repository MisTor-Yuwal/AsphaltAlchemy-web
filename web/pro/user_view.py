from flask import Blueprint, render_template, flash, redirect,url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from .productForm import EditProfileForm, UserLocationForm, DeliveryLocationForm
from .data.location_data import STATE_AND_DISTRICTS
from . import db
from .model import User, UserImage, UserLocation, DeliveryLocation
import os
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

user_view=Blueprint("user_view", __name__)

csrf = CSRFProtect()

@user_view.route("/dashboard")
@login_required
def user_dashboard():
	return render_template('frontend/user_dash/dash.html')

@user_view.route("/user_order")
@login_required
def users_order():
	return render_template('frontend/user_dash/order.html')

@user_view.route("/user_info")
@login_required
def user_info():
	form = UserLocationForm()
	dform = DeliveryLocationForm()

	image_path = os.path.join(current_app.root_path, 'static', 'users', current_user.image.file_name) if current_user.image else None
	has_image = os.path.isfile(image_path) if image_path else False
	
	return render_template('frontend/user_dash/info.html', has_image=has_image, form=form , dform=dform)

@user_view.route("/update-info",methods=['GET','POST'])
@login_required
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

@user_view.route("/get_district", methods=['POST'])
@login_required
def get_district():
	state = request.json.get('state')
	districts = STATE_AND_DISTRICTS.get(state, [])
	return jsonify({'districts' : districts})

@user_view.route("/user_cart")
@login_required
def user_cart():
	return render_template('frontend/user_dash/cart.html')


def get_district_choices(state):
	return [(d, d) for d in STATE_AND_DISTRICTS.get(state, [])]
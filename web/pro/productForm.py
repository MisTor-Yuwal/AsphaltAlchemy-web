from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, IntegerField, FloatField, MultipleFileField, DateField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Length, Email, Optional, Regexp
from flask_wtf.file import FileAllowed, FileRequired
from .data.location_data import STATE_AND_DISTRICTS



def min_files_required(min_file=1):
    def _min_files(form, field):
        if not field.data or len([f for f in field.data if f.filename]) < min_file:
            raise ValidationError(f"Please select atleast {min_file} files.")
    return _min_files



class ProductForm(FlaskForm):
    name = StringField(
        "Product name",
        validators=[DataRequired()],
        render_kw={"placeholder" : "product name", "class" : "form-control", "id" : "pname"}
    )
    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired(), NumberRange(min=1, max=100)],
        render_kw={"placeholder" : "quantity", "class" : "form-control", "id" : "pquantity"}

    )
    price = FloatField(
        "Price",
        validators=[DataRequired(), NumberRange(min=500, max=10000)],
        render_kw={"placeholder" : "price", "class" : "form-control", "id" : "pprice"}

    )
    description = StringField(
        "Description",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Description", "class" : "form-control", "id" : "pdescription"}
    )
    color = StringField(
        "Color",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Color", "class" : "form-control", "id" : "pname"}
    )
    weight = FloatField(
        "Weight",
        validators=[DataRequired(), NumberRange(min=100, max=1000)],
        render_kw={"placeholder" : "weight", "class" : "form-control", "id" : "pprice"}

    )
    material = StringField(
        "Material",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Material" , "class" : "form-control", "id" : "pname"}
    )
    percentage = FloatField(
        "%",
        validators=[DataRequired(), NumberRange(min=0, max=100)],
        render_kw={"placeholder" : "percentage", "class" : "form-control", "id" : "pprice"}

    )

    image = MultipleFileField(
         "Image",
         validators=[min_files_required(4), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')],
        render_kw={"placeholder" : "image", "class" : "form-control", "id" : "pimage"}

    )

    sizes = SelectMultipleField(
        "Size",
        choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL' , 'XL'), ('XXL', 'XXL')],
        coerce=str,
        render_kw={"placeholder" : "Size", "class" : "form-control", "id" : "psize"}
    )

    submit = SubmitField('upload', render_kw={"class" : "btn upload-btn btn-primary"})



class GalleryForm(FlaskForm):
    title = StringField(
        "title",
        validators=[DataRequired()],
        render_kw={"placeholder" : "title", "class" : "form-control" , "id" : "pname"}
    )

    description = StringField(
        "description",
        validators=[DataRequired()],
        render_kw={"placeholder" : "description", "class" : "form-control", "id" : "pdescription"}
    )
    photo = FileField(
        "photo",
        validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')],
        render_kw={"placeholder" : "photo", "class" : "form-control" , "id" : "pimage"}
    )
    submit = SubmitField('upload', render_kw={"class" : "btn upload-btn btn-primary"})



class Offerform(FlaskForm):
    start_date = DateField(
        "Start date",
        validators=[DataRequired()],
        format='%Y-%m-%d',
        render_kw={"placeholder" : "start date", "class" : "form-control", "id" : "offer-start-date"} 
    )
    end_date = DateField(
        "End date",
        validators=[DataRequired()],
        format='%Y-%m-%d',
        render_kw={"placeholder" : "end date", "class" : "form-control", "id" : "offer-end-date"}
    )
    discount = IntegerField(
        "Discount %",
        validators=[DataRequired(), NumberRange(min=1, max=100, message="Discount must be between 0 and 100")],
        render_kw={"placeholder" : "discount (1-100) %", "class" : "form-control", "id" : "offer-discount"}
    )

    choose = SelectField(
        "choose product",
        choices=[('Multiple/single', 'Multiple/single Product'), ('all', 'All Product')],
        validators=[DataRequired()],
        render_kw={"placeholder" : "choice" , "class" : "form-control", "id" : "choice-field"}
    )

    submit = SubmitField('Add Offer', render_kw={"class" : "btn btn-primary upload-btn"})

    def validate_end_date(form, field):
        if form.start_date.data and field.data:
            if field.data < form.start_date.data:
                raise ValidationError('End date must be after start date.')
            



class SelectProductForm(FlaskForm):
    product = SelectMultipleField(
        "Select product",
        coerce=int,
        choices=[],
        validators=[DataRequired()],
        render_kw={"class" : "form-control dropdown-for-offer-product"}
    )
    submit =SubmitField('Add offer', render_kw={"class" : "btn primary-btn  upload-btn"})




class EditProfileForm(FlaskForm):
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={"placeholder": "first name" , "class": "form-control", "id" : "Edit-form-fname"}
    )
    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={"placeholder": "last name" , "class": "form-control", "id" : "Edit-form-lname"}
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "email" , "class": "form-control", "id" : "Edit-form-email"}
    )
    phone = StringField(
        "Phone",
        validators=[DataRequired(), Regexp(r'^\d{10}$', message="Phone must be 10 digits.")],
        render_kw={"placeholder": "phone" , "class": "form-control", "id" : "Edit-form-phone"}
    )
    image = FileField(
        "Profile Picture",
        validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')],
        render_kw={"placeholder": "profile picture", "class" : "form-control", "id" : "Edit-from-image"}
    )

    submit = SubmitField('Update', render_kw={"class" : "btn btn-primary upload-btn", "id" : "Edit-form-button"})






class UserLocationForm(FlaskForm):
    state = SelectField(
        "State",
        choices=[(s,s) for s in STATE_AND_DISTRICTS.keys()],
        validators=[DataRequired()],
        render_kw={"placeholder" : "Province", "class" : "form-control", "id" : "state"}
    )

    district = SelectField(
        "District",
        choices=[],
        validators=[DataRequired()],
        render_kw={"placeholder" : "District", "class" : "form-control", "id" : "district"}
    )

    city = StringField(
        "City",
        validators=[DataRequired()],
        render_kw={"placeholder" : "City", "class" : "form-control", "id" : "Location-city"}
    )

    ward = IntegerField(
        "Ward",
        validators={DataRequired(), NumberRange(min=1, max=200)},
        render_kw={"placeholder" : "Ward", "class" : "form-control", "id": "Location-ward"}
    )

    streetAddress = StringField(
        "Street Address",
        validators=[DataRequired()],
        render_kw={"palceholder" : "Street Address", "class" : "form-control" , "id" : "Location-street"}
    )

    submit = SubmitField('Submit', render_kw={"id" : "Location-button"})



class DeliveryLocationForm(FlaskForm):
    delivery_state = SelectField(
        "State",
        choices=[(s,s) for s in STATE_AND_DISTRICTS.keys()],
        validators=[DataRequired()],
        render_kw={"placeholder" : "Delivery State", "class" : "form-control", "id" : "deliveryState" }
    )

    delivery_district = SelectField(
        "District",
        choices= [],
        validators=[DataRequired()],
        render_kw={"placeholder": "Delivery district", "class" : "form-control" , "id" : "deliveryDistrict"}
    )

    delivery_city = StringField(
        "City",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Delivery City" , "class":"form-control", "id" : "deliveryCity"}
    )

    delivery_ward = IntegerField(
        "Ward",
        validators=[DataRequired(), NumberRange(min=1, max=200)],
        render_kw={"placeholder" : "Delivery ward", "class" : "form-control", "id" : "deliveryWard"}
    )

    delivery_street = StringField(
        "Street",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Delivery street" , "class" : "form-control","id" : "deliveryStreet"}
    )

    submit = SubmitField('Submit', render_kw={"id": "deliveryLocationButton"})
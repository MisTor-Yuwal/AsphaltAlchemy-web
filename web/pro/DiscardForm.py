from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SelectField,SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired

class SelectOfferForm(FlaskForm):
    offer = SelectMultipleField(
        "Select Offer",
        coerce=int,
        choices=[],
        validators=[DataRequired()],
        render_kw={"placeholder":"select offer", "class" :"form-control", "id": "selectOffer"}
    )
    discard = SubmitField('Discard', render_kw={"id" : "discardButton"})

class EditProductForm(FlaskForm):
    select_to_edit_delete = SelectField(
        "Select",
        coerce=int,
        validators=[InputRequired()],
        render_kw={"placeholder" : "Select", "class" : "form-control", "id" : "EDproduct"}

    )
    edit = SubmitField('Edit', render_kw={"id" : "EDButton", "class" : "btn btn-primary upload-btn"})
    delete = SubmitField('Delete', render_kw={"id" : "DButton", "class" : "btn btn-danger upload-btn"})

class AddToCartForm(FlaskForm):
    size = SelectField(
        "Size",
        coerce=str,
        choices=[],
        validators=[InputRequired()],
        render_kw={"class" : "form-control" , "id" : "cartSize"}
    )
    product_id = HiddenField('product_ID', validators=[DataRequired()])
    addCart = SubmitField('Add to Cart', render_kw={"id" : "AddtoCartButton" , "class": "form-control"})
    remove = SubmitField('remove', render_kw={"id" : "xbutton", "class" : "form-control removeButton wdxl-lubrifont-tc-regular"})

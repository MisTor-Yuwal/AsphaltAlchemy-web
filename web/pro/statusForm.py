from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class StatusForm(FlaskForm):
    orderID = HiddenField('Order ID')
    status = SelectField(
        "status",
        choices=[('Payment', 'Payment Pending'), ('Payment received', 'Payment Received'), ('Order placed', 'Order placed'), ('Handed to logistic', 'Handed to logistic'), ('Refund issued', 'Refund issued'), ('Waiting for return', 'Waiting for return'), ('Return received', 'Return received'), ('Refund disbursed', 'Refund disbursed')],
        validators=[DataRequired()],
        render_kw={"placeholder": "status field", "class" : "form-control formStatusSelectField", "id" : "adminStatusField"}
    )
    update = SubmitField(
        'Update',
        render_kw={"class" : "adminUpdateStatusBtn btn form-control " , "id" : "adminUpdateStatusBtn"}
    )
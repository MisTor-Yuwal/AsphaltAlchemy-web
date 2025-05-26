from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email,Optional

class LoginForm(FlaskForm):
    email = StringField(
        "email",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Enter your email", "class" : "form-control", "id" : "email-input"}
    )
    
    password = PasswordField(
        "password",
        validators=[DataRequired()],
        render_kw={"placeholder" : "Enter your password", "class" : "form-control", "id" : "password-input"}
    )
    submit = SubmitField("login", render_kw={"class" : "btn btn-primary"})
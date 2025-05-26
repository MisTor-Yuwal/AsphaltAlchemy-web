from . import db
from sqlalchemy import CheckConstraint
from datetime import datetime
from flask_login import UserMixin


class Product(db.Model):
    productID = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(150))
    productQuantity = db.Column(db.Integer)
    productDetail = db.Column(db.String(10000))
    productPrice = db.Column(db.Float)
    productColor = db.Column(db.String(250))
    productWeight = db.Column(db.Float, nullable=True)
    productMaterial = db.Column(db.String(150))
    productPercentage = db.Column(db.Float)
    productSizes = db.relationship('Size', backref='product', lazy=True)
    offers = db.relationship('Offer', backref='product', lazy=True)
    image = db.relationship('ProductImage',backref='product', lazy=True)

class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(15))
    product_id = db.Column(db.Integer, db.ForeignKey('product.productID'))


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    discount_percentage = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.productID'))

    __table_args__ = (
        CheckConstraint ('discount_percentage >= 0 AND discount_percentage <= 100', name='check_discount_range'),
    )

    
class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.productID'), nullable=False)


class Order(db.Model):
    order_id=db.Column(db.Integer, primary_key=True)
    product_id=db.Column(db.Integer, db.ForeignKey('product.productID'))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity=db.Column(db.Integer)
    purchase_date=db.Column(db.DateTime, default=datetime.utcnow)
    state = db.Column(db.String(150))
    district = db.Column(db.String(150))
    city = db.Column(db.String(150))
    ward = db.Column(db.String(150))
    street = db.Column(db.String(150))

class Cart(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.productID'))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))



class Gallery(db.Model):
    pictureID=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(150))
    description=db.Column(db.String(10000))
    picture_file = db.Column(db.String(255), nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id= db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(150))
    l_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    phone = db.Column(db.Integer)
    is_admin = db.Column(db.Boolean, default=False)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime ,default=datetime.utcnow)
    previous_login = db.Column(db.DateTime)
    uorder = db.relationship('Order', backref='user', lazy=True)
    image = db.relationship('UserImage', backref='user', lazy=True ,uselist=False)
    location = db.relationship('UserLocation', backref='user', lazy=True, uselist=False)
    delivery_location = db.relationship('DeliveryLocation', backref='user', lazy=True, uselist=False)

class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)


class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(150))
    district = db.Column(db.String(150))
    city = db.Column(db.String(150))
    ward = db.Column(db.String(150))
    street = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True,nullable=False)

    __table_args__ = (
        CheckConstraint(
            "state IN ('Koshi', 'Madesh', 'Bagmati','Gandaki','Lumbini','Karnali','Sudur pachim')",
            name='valid_state_constraint'
        ),
    )



class DeliveryLocation(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(150))
    district = db.Column(db.String(150))
    city = db.Column(db.String(150))
    ward = db.Column(db.String(150))
    street = db.Column(db.String(150))
    is_default = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "state IN ('Koshi', 'Madesh', 'Bagmati','Gandaki','Lumbini','Karnali','Sudur pachim')",
            name='valid_state_constraint_for_delivery'
        ),
    )

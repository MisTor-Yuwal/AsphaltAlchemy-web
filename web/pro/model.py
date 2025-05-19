from . import db
from flask_login import UserMixin

class Product(db.Model):
    productID = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(150))
    productQuantity = db.Column(db.Integer)
    productDetail = db.Column(db.String(10000))
    productPrice = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id= db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(150))
    L_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=True)
    uproduct = db.relationship('Product', backref='user', lazy=True, cascade='all, delete')

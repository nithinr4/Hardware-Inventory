from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    privilege_level = db.Column(db.String(50), nullable=False, default='user')
    approval_status = db.Column(db.String(50), nullable=False, default='pending')

class Hardware(db.Model):
    __tablename__ = 'hardware'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    hw_owner = db.relationship('User', backref=db.backref('users', lazy=True))
    checkouts = db.relationship('Checkout', back_populates='hardware')

class Checkout(db.Model):   
    __tablename__ = 'checkout'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    return_date = db.Column(db.DateTime, nullable=True)
    state = db.Column(db.String(150), nullable=False)

    hardware = db.relationship('Hardware', back_populates='checkouts')

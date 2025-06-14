from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    privilege_level = db.Column(db.String(50), nullable=False, default='user')
    approval_status = db.Column(db.String(50), nullable=False, default='pending')

    def __str__(self):
        return self.username

class Hardware(db.Model):
    __tablename__ = 'hardware'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    hw_owner = db.relationship('User', backref=db.backref('hw_owner_name', lazy=True))
    checkouts = db.relationship('Checkout', back_populates='hardware')

    def __str__(self):
        return self.name

class Checkout(db.Model):   
    __tablename__ = 'checkout'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.id'), nullable=False)
    pending_checkout_date = db.Column(db.DateTime, nullable=True)
    pending_return_date = db.Column(db.DateTime, nullable=True)
    checkout_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    state = db.Column(db.String(150), nullable=False)

    hw_leaser = db.relationship('User', backref=db.backref('hw_leaser_name', lazy=True))
    hardware = db.relationship('Hardware', back_populates='checkouts')
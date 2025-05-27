from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, SignupForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

from views import UserAdmin, HardwareAdmin, CheckoutAdmin
from models import User, Hardware, Checkout

admin = Admin(app, name="Admin Panel", template_mode='bootstrap4')
admin.add_view(UserAdmin(User, db.session))
admin.add_view(HardwareAdmin(Hardware, db.session))
admin.add_view(CheckoutAdmin(Checkout, db.session))

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    formError = 0
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        formError = 1
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form, formError=formError)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_password, privilege_level='user')
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/hardware_list', methods=['GET'])
def hardware_list():
    active_checkouts = Checkout.query.filter(
        Checkout.state == 'taken'
    ).all()
    unleased_hardware = Hardware.query.filter(
        Hardware.count > 0).all()
    return render_template('hardware_list.html', active_checkouts=active_checkouts, unleased_hardware=unleased_hardware)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        if current_user.approval_status == 'approved':
            hardware_ids = request.form.getlist('hardware_ids')
            for hardware_id in hardware_ids:
                hardware = Hardware.query.get(hardware_id)
                if hardware and hardware.count > 0:
                    checkout_entry = Checkout(user_id=current_user.id, hardware_id=hardware.id, state='taken')
                    db.session.add(checkout_entry)
                    hardware.count -= 1
                    db.session.commit()
            flash('Hardware checked out successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Checkout failed because user has not been approved yet. Contact the administrator.', 'danger')
            return redirect(url_for('index'))

    hardware = Hardware.query.filter(
        Hardware.count > 0).all()
    return render_template('checkout.html', hardware=hardware)

@app.route('/return', methods=['GET', 'POST'])
@login_required
def return_hardware():
    if request.method == 'POST':
        checkout_ids = request.form.getlist('checkout_ids')
        for checkout_id in checkout_ids:
            checkout = Checkout.query.get(checkout_id)

            if checkout and checkout.user_id == current_user.id and not checkout.return_date:
                hardware = Hardware.query.get(checkout.hardware_id)
                hardware.count += 1
                checkout.return_date = db.func.current_timestamp()
                checkout.state = 'returned'
                db.session.commit()
        flash('Hardware returned successfully!', 'success')
        return redirect(url_for('index'))

    checkouts = Checkout.query.filter(
        Checkout.user_id == current_user.id,
        Checkout.state == 'taken').all()
    return render_template('return.html', checkouts=checkouts)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 10000)
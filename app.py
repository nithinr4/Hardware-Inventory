from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, Blueprint, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, SignupForm, ModifyAccountForm
from config import config_by_name
from pytz import timezone, utc
import os

def to_ist_filter(value):
    if value is None:
        return ''
    ist = timezone('Asia/Kolkata')
    return utc.localize(value).astimezone(ist).strftime('%Y-%m-%d %H:%M')

db = SQLAlchemy()
env = os.environ.get("FLASK_ENV", "development")
app = Flask(__name__)
app.jinja_env.filters['to_ist'] = to_ist_filter
app.config.from_object(config_by_name[env])
db.init_app(app)

admin_utils = Blueprint("admin_utils", __name__)

@admin_utils.route("/admin/download-db")
def download_db():
    if not current_user.is_authenticated or not (current_user.privilege_level == "admin" and current_user.approval_status == 'approved'):
        flash("Unauthorized access", "danger")
        return redirect(url_for("admin.index"))

    db_path = os.path.join('instance', app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", ""))
    if os.path.exists(db_path):
        return send_file(db_path, as_attachment=True)
    else:
        flash("Database file not found", "danger")
        return redirect(url_for("admin.index"))
app.register_blueprint(admin_utils)

from views import UserAdmin, HardwareAdmin, CheckoutAdmin
from models import User, Hardware, Checkout

admin = Admin(app, name="Admin Panel", template_mode='bootstrap4')
admin.add_view(UserAdmin(User, db.session))
admin.add_view(HardwareAdmin(Hardware, db.session))
admin.add_view(CheckoutAdmin(Checkout, db.session))
admin.add_link(MenuLink(name="Download DB", url="/admin/download-db", category="Tools"))

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_active_page():
    is_hw_owner = False
    if current_user.is_authenticated:
        is_hw_owner = Hardware.query.filter_by(owner_id=current_user.id).first() is not None
    return dict(active_page=request.endpoint, is_hw_owner=is_hw_owner)

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

@app.route('/update_account', methods=['GET', 'POST'])
def update_account():
    form = ModifyAccountForm()

    if form.validate_on_submit():
        # Check if current password matches
        user = User.query.filter_by(username = form.username.data).first()
        if not check_password_hash(user.password_hash, form.current_password.data):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('update_account'))

        # Update fields
        user.password_hash = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('index'))  # or wherever you want

    return render_template('update_account.html', form=form)

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
                    # checkout_entry = Checkout(user_id=current_user.id, hardware_id=hardware.id, state='taken')
                    checkout_entry = Checkout(user_id=current_user.id, hardware_id=hardware.id, state='pending_checkout', pending_checkout_date = db.func.current_timestamp())
                    db.session.add(checkout_entry)
                    hardware.count -= 1
                    db.session.commit()
            flash('Request to checkout hardware sent. Please wait for approval.', 'success')
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
                # hardware = Hardware.query.get(checkout.hardware_id)
                # hardware.count += 1
                checkout.pending_return_date = db.func.current_timestamp()
                # checkout.state = 'returned'
                checkout.state = 'pending_return'
                db.session.commit()
        flash('Request to return hardware sent. Contact the hardware owner and return the hardware.', 'success')
        return redirect(url_for('index'))

    checkouts = Checkout.query.filter(
        Checkout.user_id == current_user.id,
        Checkout.state == 'taken').all()
    return render_template('return.html', checkouts=checkouts)

@app.route('/pending', methods=['GET'])
@login_required
def pending():
    pending_checkouts = Checkout.query.filter(
        Checkout.user_id == current_user.id,
        Checkout.state == 'pending_checkout').all()
    pending_returns = Checkout.query.filter(
        Checkout.user_id == current_user.id,
        Checkout.state == 'pending_return').all()
    return render_template('pending.html', pending_checkouts=pending_checkouts, pending_returns=pending_returns)

@app.route('/owner_actions', methods=['GET'])
@login_required
def owner_actions():
    if Hardware.query.filter_by(owner_id=current_user.id).first() is not None:
        pending_checkouts = Checkout.query.join(Checkout.hardware).join(Hardware.hw_owner).filter(
            User.id == current_user.id,
            Checkout.state == 'pending_checkout').all()
        
        pending_returns = Checkout.query.join(Checkout.hardware).join(Hardware.hw_owner).filter(
            User.id == current_user.id,
            Checkout.state == 'pending_return').all()
        return render_template('owner_actions.html', pending_checkouts=pending_checkouts, pending_returns=pending_returns)
    else:
        flash('Forbidden access!', 'danger')
        return render_template('index.html')
    
@app.route('/approve-checkout', methods=['POST'])
@login_required
def approve_checkout():
    checkout_id = request.json.get("id")
    # handle approval logic here
    checkout = Checkout.query.get_or_404(checkout_id)
    print(checkout.hardware.name)
    if checkout.hardware.owner_id != current_user.id:
        abort(403)
    checkout.state = 'taken'
    checkout.pending_checkout_date = None
    checkout.checkout_date = db.func.current_timestamp()
    db.session.commit()
    return jsonify({"status": "success", "action": "approved", "id": checkout_id})    

@app.route('/reject-checkout', methods=['POST'])
@login_required
def reject_checkout():
    checkout_id = request.json.get("id")
    # handle rejection logic here
    checkout = Checkout.query.get_or_404(checkout_id)
    if checkout.hardware.owner_id != current_user.id:
        abort(403)
    hardware = Hardware.query.get(checkout.hardware_id)
    hardware.count += 1
    checkout.state = 'rejected'
    checkout.pending_checkout_date = None
    db.session.commit()
    return jsonify({"status": "success", "action": "rejected", "id": checkout_id})

@app.route('/confirm-return', methods=['POST'])
@login_required
def confirm_return():
    checkout_id = request.json.get("id")
    # handle confirmation logic here
    checkout = Checkout.query.get_or_404(checkout_id)
    if checkout.hardware.owner_id != current_user.id:
        abort(403)
    hardware = Hardware.query.get(checkout.hardware_id)
    hardware.count += 1
    checkout.pending_return_date = None
    checkout.return_date = db.func.current_timestamp()
    checkout.state = 'returned'
    db.session.commit()
    return jsonify({"status": "success", "action": "confirmed", "id": checkout_id})

@app.route('/revert-checkout-request', methods=['POST'])
@login_required
def revert_checkout_request():
    checkout_id = request.json.get("id")
    # handle confirmation logic here
    checkout = Checkout.query.get_or_404(checkout_id)
    if checkout.hw_leaser != current_user:
        abort(403)
    hardware = Hardware.query.get(checkout.hardware_id)
    hardware.count += 1
    checkout.pending_checkout_date = None
    checkout.state = 'reverted'
    db.session.commit()
    return jsonify({"status": "success", "action": "confirmed", "id": checkout_id})

@app.route('/revert-return-request', methods=['POST'])
@login_required
def revert_return_request():
    checkout_id = request.json.get("id")
    # handle confirmation logic here
    checkout = Checkout.query.get_or_404(checkout_id)
    if checkout.hw_leaser != current_user:
        abort(403)
    checkout.state = 'taken'
    checkout.pending_return_date = None
    db.session.commit()
    return jsonify({"status": "success", "action": "confirmed", "id": checkout_id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 10000)
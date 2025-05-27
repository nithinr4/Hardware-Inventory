from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import SelectField 

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.privilege_level == 'admin'

class UserAdmin(AdminModelView):
    form_overrides = {
        'privilege_level': SelectField,
        'approval_status': SelectField
    }
    form_args = {
        'privilege_level': {
            'choices': [('admin', 'Admin'), ('user', 'User')]
        },
        'approval_status': {
            'choices': [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
        }
    }
    form_excluded_columns = ['password_hash']
    column_list = ('username', 'privilege_level', 'approval_status')
    column_labels = {'username': 'Username', 'privilege_level': 'Access Level', 'approval_status': 'Approval Status'}
    column_filters = ('username', 'privilege_level', 'approval_status')

class HardwareAdmin(AdminModelView):
    column_list = ('hw_owner.username', 'name', 'count')
    column_labels = {'hw_owner.username': 'Hardware Owner', 'name': 'Board Name', 'count': 'Count'}
    column_filters = ('hw_owner.username', 'name', 'count')

class CheckoutAdmin(AdminModelView):
    form_overrides = {
        'state': SelectField
    }
    
    form_args = {
        'state': {
            'choices': [('taken', 'Taken'), ('returned', 'Returned')]
        }
    }
    column_list = ('hw_leaser.username', 'hardware.name', 'checkout_date', 'return_date', 'state')
    column_labels = {'hw_leaser.username': 'Hardware Leaser', 'hardware.name': 'Board Name', 'checkout_date': 'Checkout Date', 'return_date': 'Return Date', 'state': 'State'}
    column_filters = ('hw_leaser.username', 'hardware.name', 'checkout_date', 'return_date', 'state')
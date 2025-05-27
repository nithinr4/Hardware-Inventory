from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.privilege_level == 'admin'

class UserAdmin(AdminModelView):
    column_list = ('username', 'privilege_level', 'approval_status')
    column_labels = {'username': 'Username', 'privilege_level': 'Access Level', 'approval_status': 'Approval Status'}
    column_filters = ('username', 'privilege_level', 'approval_status')

class HardwareAdmin(AdminModelView):
    column_list = ('hw_owner.username', 'name', 'count')
    column_labels = {'hw_owner.username': 'Hardware Owner', 'name': 'Board Name', 'count': 'Count'}
    column_filters = ('hw_owner.username', 'name', 'count')

class CheckoutAdmin(AdminModelView):
    column_list = ('hw_leaser.username', 'name', 'count')
    column_labels = {'hw_leaser.username': 'Hardware Leaser', 'name': 'Board Name', 'count': 'Count'}
    column_filters = ('hw_leaser.username', 'name', 'count')
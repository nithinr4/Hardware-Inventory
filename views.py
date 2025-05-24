from flask_admin.contrib.sqla import ModelView

class UserAdmin(ModelView):
    column_list = ('username', 'privilege_level', 'approval_status')
    column_labels = {'username': 'Username', 'privilege_level': 'Access Level', 'approval_status': 'Approval Status'}
    column_filters = ('username', 'privilege_level', 'approval_status')

class HardwareAdmin(ModelView):
    column_list = ('hw_owner.username', 'name', 'count')
    column_labels = {'hw_owner.username': 'Hardware Owner', 'name': 'Board Name', 'count': 'Count'}
    column_filters = ('hw_owner.username', 'name', 'count')
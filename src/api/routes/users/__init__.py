
from flask import Blueprint
from . import user_routes

users_bp = Blueprint('users', __name__)

# Auth Routes
users_bp.add_url_rule('/api/auth/register', view_func=user_routes.register, endpoint='register', methods=['POST'])
users_bp.add_url_rule('/api/auth/login', view_func=user_routes.login, endpoint='login', methods=['POST'])
users_bp.add_url_rule('/api/auth/logout', view_func=user_routes.logout, endpoint='logout', methods=['POST'])

# User Info Routes
users_bp.add_url_rule('/api/auth/user-info', view_func=user_routes.get_user_info, endpoint='get_user_info', methods=['GET'])
users_bp.add_url_rule('/api/auth/user', view_func=user_routes.update_user, endpoint='update_user', methods=['PATCH'])

# Account Management Routes
users_bp.add_url_rule('/api/auth/change-password', view_func=user_routes.change_password, endpoint='change_password', methods=['POST'])
users_bp.add_url_rule('/api/auth/delete-account', view_func=user_routes.delete_account, endpoint='delete_account', methods=['POST'])

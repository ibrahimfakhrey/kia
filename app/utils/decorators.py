from functools import wraps
from flask import redirect, url_for, flash, jsonify
from flask_login import current_user
from flask_jwt_extended import get_jwt_identity
from app.models import User


def admin_required(f):
    """Decorator to require admin role for a route (Flask-Login)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin.login'))
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


def jwt_admin_required(f):
    """Decorator to require admin role for JWT API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)
    return decorated_function

from functools import wraps
from flask import redirect, url_for, flash, jsonify, request
from flask_login import current_user, logout_user
from flask_jwt_extended import get_jwt_identity
from app.models import User, ADMIN_SECTIONS


def _endpoint_section(endpoint):
    """Map an admin endpoint (e.g. 'admin.materials_create') to its section key."""
    name = (endpoint or '').rsplit('.', 1)[-1]
    for key in list(ADMIN_SECTIONS) + ['admins', 'dashboard']:
        if name == key or name.startswith(key + '_'):
            return key
    return None


def admin_landing_url(user):
    """First page this admin is allowed to open, or None if they have no sections."""
    if user.has_full_access():
        return url_for('admin.dashboard')
    sections = user.permission_list
    return url_for(ADMIN_SECTIONS[sections[0]][1]) if sections else None


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

        if not current_user.has_full_access():
            section = _endpoint_section(request.endpoint)
            landing = admin_landing_url(current_user)
            if landing is None:
                logout_user()
                flash('لا توجد صلاحيات مفعّلة لحسابك. تواصل مع المدير.', 'danger')
                return redirect(url_for('admin.login'))
            if section == 'dashboard':
                return redirect(landing)
            # Anything outside the granted sections (including managing admins
            # and unknown endpoints) is reserved for full-access admins.
            if section not in current_user.permission_list:
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة.', 'danger')
                return redirect(landing)
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

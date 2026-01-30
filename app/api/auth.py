from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app.models import User
from . import api_bp


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Parent login endpoint."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401

    if user.role != 'parent':
        return jsonify({'error': 'Access denied. Parents only.'}), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(current_user_id))

    return jsonify({'access_token': access_token}), 200


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict()), 200


@api_bp.route('/auth/fcm-token', methods=['POST'])
@jwt_required()
def update_fcm_token():
    """Update user's FCM token for push notifications."""
    from app.extensions import db

    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    fcm_token = data.get('fcm_token')

    if not fcm_token:
        return jsonify({'error': 'FCM token is required'}), 400

    user.fcm_token = fcm_token
    db.session.commit()

    return jsonify({'message': 'FCM token updated successfully'}), 200

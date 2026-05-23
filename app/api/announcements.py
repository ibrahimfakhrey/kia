from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.models import User, Announcement
from app.models.announcement import announcement_targets
from . import api_bp


@api_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    """Return active announcements relevant to the current user."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    targeted_ids_subq = (
        Announcement.query
        .with_entities(Announcement.id)
        .join(announcement_targets, announcement_targets.c.announcement_id == Announcement.id)
        .filter(announcement_targets.c.user_id == user.id)
        .subquery()
    )

    announcements = (
        Announcement.query
        .filter(Announcement.is_active.is_(True))
        .filter(or_(
            Announcement.target_type == 'all',
            (Announcement.target_type == 'role') & (Announcement.target_role == user.role),
            Announcement.id.in_(targeted_ids_subq),
        ))
        .order_by(Announcement.created_at.desc())
        .all()
    )

    return jsonify([a.to_dict() for a in announcements]), 200

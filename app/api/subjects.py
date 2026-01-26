from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Subject, Material, Student
from . import api_bp


@api_bp.route('/subjects/<int:id>', methods=['GET'])
@jwt_required()
def get_subject(id):
    """Get a subject by ID."""
    parent_id = int(get_jwt_identity())

    # Verify the parent has a child in the subject's class
    subject = Subject.query.get(id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Check if parent has a child in this class
    has_child = Student.query.filter_by(
        parent_id=parent_id,
        class_id=subject.class_id
    ).first()

    if not has_child:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(subject.to_dict()), 200


@api_bp.route('/subjects/<int:id>/materials', methods=['GET'])
@jwt_required()
def get_subject_materials(id):
    """Get all materials for a subject."""
    parent_id = int(get_jwt_identity())

    subject = Subject.query.get(id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Check if parent has a child in this class
    has_child = Student.query.filter_by(
        parent_id=parent_id,
        class_id=subject.class_id
    ).first()

    if not has_child:
        return jsonify({'error': 'Access denied'}), 403

    materials = Material.query.filter_by(subject_id=id).order_by(Material.order_index).all()

    return jsonify([material.to_dict() for material in materials]), 200

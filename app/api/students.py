from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Student, Subject
from . import api_bp


@api_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all children of the current parent."""
    parent_id = int(get_jwt_identity())
    students = Student.query.filter_by(parent_id=parent_id).all()

    return jsonify([student.to_dict() for student in students]), 200


@api_bp.route('/students/<int:id>', methods=['GET'])
@jwt_required()
def get_student(id):
    """Get a single child by ID."""
    parent_id = int(get_jwt_identity())
    student = Student.query.filter_by(id=id, parent_id=parent_id).first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student.to_dict()), 200


@api_bp.route('/students/<int:id>/subjects', methods=['GET'])
@jwt_required()
def get_student_subjects(id):
    """Get all subjects for a student's class."""
    parent_id = int(get_jwt_identity())
    student = Student.query.filter_by(id=id, parent_id=parent_id).first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if not student.class_id:
        return jsonify({'error': 'Student is not assigned to a class'}), 400

    subjects = Subject.query.filter_by(class_id=student.class_id).all()

    return jsonify([subject.to_dict() for subject in subjects]), 200

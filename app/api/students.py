from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Student, Subject
from . import api_bp


@api_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all children of the current parent with today's attendance status."""
    from datetime import date
    from app.models import Attendance

    parent_id = int(get_jwt_identity())
    students = Student.query.filter_by(parent_id=parent_id).all()

    # Get today's date
    today = date.today()

    # Get all attendance records for today for these students
    student_ids = [s.id for s in students]
    today_attendance = {}
    if student_ids:
        attendance_records = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == today
        ).all()
        for record in attendance_records:
            today_attendance[record.student_id] = record.status

    # Add attendance status to each student dict
    result = []
    for student in students:
        student_dict = student.to_dict()
        student_dict['today_attendance'] = today_attendance.get(student.id, 'not_marked')
        result.append(student_dict)

    return jsonify(result), 200


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


@api_bp.route('/students/<int:student_id>/attendance/today', methods=['GET'])
@jwt_required()
def get_student_attendance_today(student_id):
    """Get today's attendance status for a specific student"""
    from datetime import date
    from app.models import Attendance
    
    current_user_id = int(get_jwt_identity())
    student = Student.query.get_or_404(student_id)
    
    # Verify the student belongs to the current user (parent)
    if student.parent_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    today = date.today()
    attendance = Attendance.query.filter_by(
        student_id=student_id,
        date=today
    ).first()
    
    if attendance:
        return jsonify({
            'student_id': student_id,
            'date': today.isoformat(),
            'status': attendance.status,
            'marked_at': attendance.created_at.isoformat()
        }), 200
    else:
        # No attendance record for today
        return jsonify({
            'student_id': student_id,
            'date': today.isoformat(),
            'status': 'not_marked',
            'marked_at': None
        }), 200

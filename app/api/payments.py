from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Payment, Student
from . import api_bp


@api_bp.route('/students/<int:student_id>/payments', methods=['GET'])
@jwt_required()
def get_student_payments(student_id):
    """Get all payments for a student."""
    parent_id = int(get_jwt_identity())

    # Verify the student belongs to the parent
    student = Student.query.filter_by(id=student_id, parent_id=parent_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.due_date.desc()).all()

    # Calculate summary
    total_due = sum(p.amount for p in payments if not p.is_paid)
    total_paid = sum(p.amount for p in payments if p.is_paid)
    next_payment = Payment.query.filter_by(
        student_id=student_id,
        is_paid=False
    ).order_by(Payment.due_date).first()

    return jsonify({
        'payments': [payment.to_dict() for payment in payments],
        'summary': {
            'total_due': total_due,
            'total_paid': total_paid,
            'next_payment': next_payment.to_dict() if next_payment else None
        }
    }), 200


@api_bp.route('/payments/summary', methods=['GET'])
@jwt_required()
def get_payments_summary():
    """Get payment summary for all children of the parent."""
    parent_id = int(get_jwt_identity())

    students = Student.query.filter_by(parent_id=parent_id).all()
    student_ids = [s.id for s in students]

    if not student_ids:
        return jsonify({
            'total_due': 0,
            'total_paid': 0,
            'pending_count': 0,
            'children_summary': []
        }), 200

    all_payments = Payment.query.filter(Payment.student_id.in_(student_ids)).all()

    total_due = sum(p.amount for p in all_payments if not p.is_paid)
    total_paid = sum(p.amount for p in all_payments if p.is_paid)
    pending_count = sum(1 for p in all_payments if not p.is_paid)

    # Summary per child
    children_summary = []
    for student in students:
        student_payments = [p for p in all_payments if p.student_id == student.id]
        next_payment = next(
            (p for p in sorted(student_payments, key=lambda x: x.due_date) if not p.is_paid),
            None
        )
        children_summary.append({
            'student': student.to_dict(),
            'total_due': sum(p.amount for p in student_payments if not p.is_paid),
            'total_paid': sum(p.amount for p in student_payments if p.is_paid),
            'next_payment': next_payment.to_dict() if next_payment else None
        })

    return jsonify({
        'total_due': total_due,
        'total_paid': total_paid,
        'pending_count': pending_count,
        'children_summary': children_summary
    }), 200

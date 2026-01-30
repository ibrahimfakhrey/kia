from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Student, Payment
from app.services.firebase_service import FirebaseService
from . import api_bp


@api_bp.route('/notifications/test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """Send a test notification to the current user."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.fcm_token:
        return jsonify({'error': 'User has no FCM token registered'}), 400

    data = request.get_json() or {}
    title = data.get('title', 'Test Notification')
    body = data.get('body', 'This is a test notification from KIA Academy')

    result = FirebaseService.send_notification(
        token=user.fcm_token,
        title=title,
        body=body,
        data={'type': 'test'}
    )

    if result:
        return jsonify({
            'message': 'Test notification sent successfully',
            'message_id': result
        }), 200
    else:
        return jsonify({'error': 'Failed to send notification'}), 500


def send_payment_reminder(payment_id):
    """Send payment reminder notification to parent."""
    from app.extensions import db

    payment = Payment.query.get(payment_id)
    if not payment:
        print(f"Payment {payment_id} not found")
        return False

    student = Student.query.get(payment.student_id)
    if not student:
        print(f"Student {payment.student_id} not found")
        return False

    parent = User.query.get(student.parent_id)
    if not parent or not parent.fcm_token:
        print(f"Parent not found or no FCM token for student {student.id}")
        return False

    title = "تذكير بالدفع - Payment Reminder"
    body = f"مستحق دفع {payment.amount} ريال للطالب {student.full_name}"

    result = FirebaseService.send_notification(
        token=parent.fcm_token,
        title=title,
        body=body,
        data={
            'type': 'payment_reminder',
            'payment_id': str(payment.id),
            'student_id': str(student.id),
            'amount': str(payment.amount),
        }
    )

    return result is not None


def send_new_material_notification(material_id):
    """Send notification about new educational material."""
    from app.models import Material, Subject, Student
    from app.extensions import db

    material = Material.query.get(material_id)
    if not material:
        print(f"Material {material_id} not found")
        return False

    subject = Subject.query.get(material.subject_id)
    if not subject:
        print(f"Subject {material.subject_id} not found")
        return False

    # Get all students in this class
    students = Student.query.filter_by(class_id=subject.class_id).all()

    # Get unique parents
    parent_ids = list(set([s.parent_id for s in students]))
    parents = User.query.filter(
        User.id.in_(parent_ids),
        User.fcm_token.isnot(None)
    ).all()

    if not parents:
        print(f"No parents with FCM tokens found for class {subject.class_id}")
        return False

    title = "محتوى تعليمي جديد - New Material"
    body = f"تم إضافة محتوى جديد: {material.title} في مادة {subject.name}"

    tokens = [p.fcm_token for p in parents]

    result = FirebaseService.send_multicast_notification(
        tokens=tokens,
        title=title,
        body=body,
        data={
            'type': 'new_material',
            'material_id': str(material.id),
            'subject_id': str(subject.id),
            'subject_name': subject.name,
        }
    )

    return result is not None


def send_welcome_notification(user_id):
    """Send welcome notification to new parent."""
    user = User.query.get(user_id)
    if not user or not user.fcm_token:
        print(f"User {user_id} not found or no FCM token")
        return False

    title = "مرحباً بك في أكاديمية كيا - Welcome to KIA"
    body = f"أهلاً {user.full_name}! نحن سعداء بانضمامك إلى أكاديمية كيا الدولية"

    result = FirebaseService.send_notification(
        token=user.fcm_token,
        title=title,
        body=body,
        data={
            'type': 'welcome',
        }
    )

    return result is not None

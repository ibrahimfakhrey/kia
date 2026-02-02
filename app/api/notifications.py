from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Student, Payment
from app.services.firebase_service import FirebaseService
from app.utils.decorators import jwt_admin_required
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


@api_bp.route('/notifications/check-and-test-all', methods=['GET'])
def check_and_test_all_fcm_tokens():
    """Check all users with FCM tokens and send test notifications. Admin only."""

    # Get all users with FCM tokens
    users_with_tokens = User.query.filter(User.fcm_token.isnot(None)).all()
    users_without_tokens = User.query.filter(User.fcm_token.is_(None)).all()

    report = {
        'total_users': User.query.count(),
        'users_with_tokens': len(users_with_tokens),
        'users_without_tokens': len(users_without_tokens),
        'notifications_sent': 0,
        'notifications_failed': 0,
        'users_with_tokens_list': [],
        'users_without_tokens_list': [],
        'notification_results': []
    }

    # Build list of users with tokens
    for user in users_with_tokens:
        report['users_with_tokens_list'].append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        })

    # Build list of users without tokens
    for user in users_without_tokens:
        report['users_without_tokens_list'].append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        })

    # Send test notifications to users with tokens
    title = "إشعار تجريبي - Test Notification"
    body = "هذا إشعار تجريبي من أكاديمية كيا للتحقق من عمل النظام"

    for user in users_with_tokens:
        try:
            result = FirebaseService.send_notification(
                token=user.fcm_token,
                title=title,
                body=body,
                data={
                    'type': 'admin_test',
                    'user_id': str(user.id)
                }
            )

            if result:
                report['notifications_sent'] += 1
                report['notification_results'].append({
                    'user_id': user.id,
                    'email': user.email,
                    'status': 'success',
                    'message_id': result
                })
            else:
                report['notifications_failed'] += 1
                report['notification_results'].append({
                    'user_id': user.id,
                    'email': user.email,
                    'status': 'failed',
                    'error': 'Firebase returned None'
                })
        except Exception as e:
            report['notifications_failed'] += 1
            report['notification_results'].append({
                'user_id': user.id,
                'email': user.email,
                'status': 'error',
                'error': str(e)
            })

    return jsonify(report), 200


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


def send_push_notification(fcm_token, title, body, data=None):
    """
    Send a push notification to a specific FCM token.

    Args:
        fcm_token: The FCM token to send to
        title: Notification title
        body: Notification body
        data: Optional dictionary of data to send with notification

    Returns:
        True if successful, False otherwise
    """
    if not fcm_token:
        print("No FCM token provided")
        return False

    result = FirebaseService.send_notification(
        token=fcm_token,
        title=title,
        body=body,
        data=data or {}
    )

    return result is not None

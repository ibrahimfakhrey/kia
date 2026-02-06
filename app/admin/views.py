from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Classe, Student, Subject, Material, Payment, Attendance
from app.services.s3_service import s3_service
from app.utils.decorators import admin_required
from . import admin_bp
from .forms import (LoginForm, UserForm, ClasseForm, StudentForm,
                    SubjectForm, MaterialForm, PaymentForm, PasswordResetForm)


# ==================== AUTH ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.is_admin():
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Invalid email or password, or not an admin.', 'danger')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.login'))


# ==================== DASHBOARD ====================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_parents': User.query.filter_by(role='parent').count(),
        'total_students': Student.query.count(),
        'total_classes': Classe.query.count(),
        'total_subjects': Subject.query.count(),
        'pending_payments': Payment.query.filter_by(is_paid=False).count(),
    }
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.filter_by(is_paid=False).order_by(Payment.due_date).limit(5).all()

    return render_template('admin/dashboard.html', stats=stats,
                           recent_students=recent_students, recent_payments=recent_payments)


# ==================== USERS ====================

@admin_bp.route('/users')
@admin_required
def users_list():
    users = User.query.filter_by(role='parent').order_by(User.created_at.desc()).all()
    return render_template('admin/users/list.html', users=users)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def users_create():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/users/form.html', form=form, title='Create User')


@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def users_edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(original_email=user.email, obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/users/form.html', form=form, title='Edit User', user=user)


@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def users_delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users_list'))


# ==================== CLASSES ====================

@admin_bp.route('/classes')
@admin_required
def classes_list():
    classes = Classe.query.order_by(Classe.name).all()
    return render_template('admin/classes/list.html', classes=classes)


@admin_bp.route('/classes/create', methods=['GET', 'POST'])
@admin_required
def classes_create():
    form = ClasseForm()
    if form.validate_on_submit():
        classe = Classe(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(classe)
        db.session.commit()
        flash('Class created successfully.', 'success')
        return redirect(url_for('admin.classes_list'))

    return render_template('admin/classes/form.html', form=form, title='Create Class')


@admin_bp.route('/classes/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def classes_edit(id):
    classe = Classe.query.get_or_404(id)
    form = ClasseForm(obj=classe)

    if form.validate_on_submit():
        classe.name = form.name.data
        classe.description = form.description.data
        db.session.commit()
        flash('Class updated successfully.', 'success')
        return redirect(url_for('admin.classes_list'))

    return render_template('admin/classes/form.html', form=form, title='Edit Class')


@admin_bp.route('/classes/<int:id>/delete', methods=['POST'])
@admin_required
def classes_delete(id):
    classe = Classe.query.get_or_404(id)
    db.session.delete(classe)
    db.session.commit()
    flash('Class deleted successfully.', 'success')
    return redirect(url_for('admin.classes_list'))


# ==================== STUDENTS ====================

@admin_bp.route('/students')
@admin_required
def students_list():
    students = Student.query.order_by(Student.full_name).all()
    return render_template('admin/students/list.html', students=students)


@admin_bp.route('/students/create', methods=['GET', 'POST'])
@admin_required
def students_create():
    form = StudentForm()
    form.parent_id.choices = [(u.id, f"{u.full_name} ({u.email})")
                              for u in User.query.filter_by(role='parent').all()]
    form.class_id.choices = [(0, '-- No Class --')] + [(c.id, c.name) for c in Classe.query.all()]

    if form.validate_on_submit():
        student = Student(
            full_name=form.full_name.data,
            date_of_birth=form.date_of_birth.data,
            parent_id=form.parent_id.data,
            class_id=form.class_id.data if form.class_id.data != 0 else None
        )

        if form.profile_image.data:
            url = s3_service.upload_file(form.profile_image.data, 'profiles')
            if url:
                student.profile_image_url = url

        db.session.add(student)
        db.session.commit()
        flash('Student created successfully.', 'success')
        return redirect(url_for('admin.students_list'))

    return render_template('admin/students/form.html', form=form, title='Create Student')


@admin_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def students_edit(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    form.parent_id.choices = [(u.id, f"{u.full_name} ({u.email})")
                              for u in User.query.filter_by(role='parent').all()]
    form.class_id.choices = [(0, '-- No Class --')] + [(c.id, c.name) for c in Classe.query.all()]

    if form.validate_on_submit():
        student.full_name = form.full_name.data
        student.date_of_birth = form.date_of_birth.data
        student.parent_id = form.parent_id.data
        student.class_id = form.class_id.data if form.class_id.data != 0 else None

        if form.profile_image.data:
            url = s3_service.upload_file(form.profile_image.data, 'profiles')
            if url:
                student.profile_image_url = url

        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('admin.students_list'))

    if student.class_id is None:
        form.class_id.data = 0

    return render_template('admin/students/form.html', form=form, title='Edit Student', student=student)


@admin_bp.route('/students/<int:id>/delete', methods=['POST'])
@admin_required
def students_delete(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('admin.students_list'))


# ==================== SUBJECTS ====================

@admin_bp.route('/subjects')
@admin_required
def subjects_list():
    subjects = Subject.query.order_by(Subject.class_id, Subject.name).all()
    return render_template('admin/subjects/list.html', subjects=subjects)


@admin_bp.route('/subjects/create', methods=['GET', 'POST'])
@admin_required
def subjects_create():
    form = SubjectForm()
    form.class_id.choices = [(c.id, c.name) for c in Classe.query.all()]

    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data,
            class_id=form.class_id.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully.', 'success')
        return redirect(url_for('admin.subjects_list'))

    return render_template('admin/subjects/form.html', form=form, title='Create Subject')


@admin_bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def subjects_edit(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    form.class_id.choices = [(c.id, c.name) for c in Classe.query.all()]

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        subject.class_id = form.class_id.data
        db.session.commit()
        flash('Subject updated successfully.', 'success')
        return redirect(url_for('admin.subjects_list'))

    return render_template('admin/subjects/form.html', form=form, title='Edit Subject')


@admin_bp.route('/subjects/<int:id>/delete', methods=['POST'])
@admin_required
def subjects_delete(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully.', 'success')
    return redirect(url_for('admin.subjects_list'))


# ==================== MATERIALS ====================

@admin_bp.route('/materials')
@admin_required
def materials_list():
    materials = Material.query.order_by(Material.subject_id, Material.order_index).all()
    return render_template('admin/materials/list.html', materials=materials)


@admin_bp.route('/materials/create', methods=['GET', 'POST'])
@admin_required
def materials_create():
    form = MaterialForm()
    form.subject_id.choices = [(s.id, f"{s.name} ({s.classe.name})") for s in Subject.query.all()]

    if form.validate_on_submit():
        material = Material(
            title=form.title.data,
            type=form.type.data,
            subject_id=form.subject_id.data
        )

        if form.type.data == 'video':
            material.video_url = form.video_url.data
        elif form.file.data:
            url = s3_service.upload_file(form.file.data, form.subject_id.data)
            if url:
                material.file_url = url

        db.session.add(material)
        db.session.commit()
        flash('Material created successfully.', 'success')
        return redirect(url_for('admin.materials_list'))

    return render_template('admin/materials/form.html', form=form, title='Create Material')


@admin_bp.route('/materials/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def materials_edit(id):
    material = Material.query.get_or_404(id)
    form = MaterialForm(obj=material)
    form.subject_id.choices = [(s.id, f"{s.name} ({s.classe.name})") for s in Subject.query.all()]

    if form.validate_on_submit():
        material.title = form.title.data
        material.type = form.type.data
        material.subject_id = form.subject_id.data

        if form.type.data == 'video':
            material.video_url = form.video_url.data
            material.file_url = None
        elif form.file.data:
            url = s3_service.upload_file(form.file.data, form.subject_id.data)
            if url:
                material.file_url = url
                material.video_url = None

        db.session.commit()
        flash('Material updated successfully.', 'success')
        return redirect(url_for('admin.materials_list'))

    return render_template('admin/materials/form.html', form=form, title='Edit Material', material=material)


@admin_bp.route('/materials/<int:id>/delete', methods=['POST'])
@admin_required
def materials_delete(id):
    material = Material.query.get_or_404(id)
    if material.file_url:
        s3_service.delete_file(material.file_url)
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully.', 'success')
    return redirect(url_for('admin.materials_list'))


# ==================== PAYMENTS ====================

@admin_bp.route('/payments')
@admin_required
def payments_list():
    payments = Payment.query.order_by(Payment.due_date.desc()).all()
    return render_template('admin/payments/list.html', payments=payments)


@admin_bp.route('/payments/create', methods=['GET', 'POST'])
@admin_required
def payments_create():
    form = PaymentForm()
    form.student_id.choices = [(s.id, f"{s.full_name} ({s.parent.full_name})")
                               for s in Student.query.all()]

    if form.validate_on_submit():
        payment = Payment(
            student_id=form.student_id.data,
            amount=form.amount.data,
            due_date=form.due_date.data,
            paid_date=form.paid_date.data,
            is_paid=form.is_paid.data,
            notes=form.notes.data
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment created successfully.', 'success')
        return redirect(url_for('admin.payments_list'))

    return render_template('admin/payments/form.html', form=form, title='Create Payment')


@admin_bp.route('/payments/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def payments_edit(id):
    payment = Payment.query.get_or_404(id)
    form = PaymentForm(obj=payment)
    form.student_id.choices = [(s.id, f"{s.full_name} ({s.parent.full_name})")
                               for s in Student.query.all()]

    if form.validate_on_submit():
        payment.student_id = form.student_id.data
        payment.amount = form.amount.data
        payment.due_date = form.due_date.data
        payment.paid_date = form.paid_date.data
        payment.is_paid = form.is_paid.data
        payment.notes = form.notes.data
        db.session.commit()
        flash('Payment updated successfully.', 'success')
        return redirect(url_for('admin.payments_list'))

    return render_template('admin/payments/form.html', form=form, title='Edit Payment')


@admin_bp.route('/payments/<int:id>/delete', methods=['POST'])
@admin_required
def payments_delete(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted successfully.', 'success')
    return redirect(url_for('admin.payments_list'))


@admin_bp.route('/payments/<int:id>/toggle-paid', methods=['POST'])
@admin_required
def payments_toggle_paid(id):
    payment = Payment.query.get_or_404(id)
    payment.is_paid = not payment.is_paid
    if payment.is_paid:
        from datetime import date
        payment.paid_date = date.today()
    else:
        payment.paid_date = None
    db.session.commit()
    flash(f'Payment marked as {"paid" if payment.is_paid else "unpaid"}.', 'success')
    return redirect(url_for('admin.payments_list'))


# ==================== PASSWORD RESET ====================

@admin_bp.route('/password-reset', methods=['GET', 'POST'])
@admin_required
def password_reset():
    """Reset password for a specific user or all users."""
    form = PasswordResetForm()

    # Populate user choices: All Users + individual parent users
    users = User.query.filter_by(role='parent').order_by(User.full_name).all()
    form.user_id.choices = [('all', 'All Users (All Parents)')] + [(str(u.id), f"{u.full_name} ({u.email})") for u in users]

    if form.validate_on_submit():
        user_id = form.user_id.data
        new_password = form.new_password.data

        if user_id == 'all':
            # Reset password for all parent users
            users_to_reset = User.query.filter_by(role='parent').all()
            for user in users_to_reset:
                user.set_password(new_password)
            db.session.commit()
            flash(f'Password reset successfully for {len(users_to_reset)} parent accounts.', 'success')
        else:
            # Reset password for specific user
            user = User.query.get_or_404(int(user_id))
            user.set_password(new_password)
            db.session.commit()
            flash(f'Password reset successfully for {user.full_name} ({user.email}).', 'success')

        return redirect(url_for('admin.password_reset'))

    return render_template('admin/password_reset.html', form=form, users=users)

# ==================== ATTENDANCE ====================

@admin_bp.route('/attendance')
@admin_required
def attendance_list():
    """Show attendance dashboard - select class and date"""
    from datetime import date
    classes = Classe.query.all()
    today = date.today()
    return render_template('admin/attendance_list.html', classes=classes, today=today)


@admin_bp.route('/attendance/mark/<int:class_id>', methods=['GET', 'POST'])
@admin_required
def attendance_mark(class_id):
    """Mark attendance for a class on a specific date"""
    from datetime import date, datetime
    
    classe = Classe.query.get_or_404(class_id)
    
    if request.method == 'GET':
        # Get date from query params or use today
        date_str = request.args.get('date')
        if date_str:
            try:
                attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                attendance_date = date.today()
        else:
            attendance_date = date.today()
        
        # Get all students in this class
        students = Student.query.filter_by(class_id=class_id).all()
        
        # Get existing attendance records for this date
        existing_attendance = {}
        for record in Attendance.query.filter_by(class_id=class_id, date=attendance_date).all():
            existing_attendance[record.student_id] = record.status
        
        return render_template('admin/attendance_mark.html', 
                             classe=classe, 
                             students=students,
                             attendance_date=attendance_date,
                             existing_attendance=existing_attendance)
    
    elif request.method == 'POST':
        # Process attendance submission
        from app.api.notifications import send_push_notification
        
        attendance_date_str = request.form.get('attendance_date')
        try:
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        except:
            attendance_date = date.today()
        
        students = Student.query.filter_by(class_id=class_id).all()
        absent_students = []
        
        for student in students:
            status = request.form.get(f'student_{student.id}', 'absent')
            
            # Check if attendance record already exists
            existing = Attendance.query.filter_by(
                student_id=student.id,
                date=attendance_date
            ).first()
            
            if existing:
                # Update existing record
                existing.status = status
                existing.marked_by = current_user.id
                existing.class_id = class_id
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    date=attendance_date,
                    status=status,
                    marked_by=current_user.id
                )
                db.session.add(attendance)
            
            # Track absent students for notifications
            if status == 'absent':
                absent_students.append(student)
        
        db.session.commit()
        
        # Send notifications to parents of absent students
        for student in absent_students:
            parent = student.parent
            if parent and parent.fcm_token:
                try:
                    send_push_notification(
                        fcm_token=parent.fcm_token,
                        title='تنبيه غياب',
                        body=f'{student.full_name} غائب اليوم - {attendance_date.strftime("%Y-%m-%d")}',
                        data={
                            'type': 'attendance',
                            'student_id': student.id,
                            'status': 'absent',
                            'date': attendance_date.isoformat()
                        }
                    )
                except Exception as e:
                    print(f'Error sending notification to parent {parent.id}: {e}')
        
        flash(f'تم حفظ الحضور بنجاح. تم إرسال {len(absent_students)} إشعار غياب.', 'success')
        return redirect(url_for('admin.attendance_list'))


@admin_bp.route('/attendance/view/<int:class_id>')
@admin_required
def attendance_view(class_id):
    """View attendance history for a class"""
    from datetime import date, timedelta
    
    classe = Classe.query.get_or_404(class_id)
    
    # Get date range from query params (default to last 7 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    date_from_str = request.args.get('date_from')
    date_to_str = request.args.get('date_to')
    
    if date_from_str:
        try:
            from datetime import datetime
            start_date = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except:
            pass
    
    if date_to_str:
        try:
            from datetime import datetime
            end_date = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except:
            pass
    
    # Get attendance records for this class in date range
    attendance_records = Attendance.query.filter(
        Attendance.class_id == class_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('admin/attendance_view.html',
                         classe=classe,
                         attendance_records=attendance_records,
                         start_date=start_date,
                         end_date=end_date)

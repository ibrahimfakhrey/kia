from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Classe, Student, Subject, Material, Payment
from app.services.s3_service import s3_service
from app.utils.decorators import admin_required
from . import admin_bp
from .forms import (LoginForm, UserForm, ClasseForm, StudentForm,
                    SubjectForm, MaterialForm, PaymentForm)


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

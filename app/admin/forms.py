from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('admin', 'Admin')])
    is_active = BooleanField('Active', default=True)

    def __init__(self, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, field):
        if field.data != self.original_email:
            user = User.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError('Email already registered.')


class ClasseForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])


class StudentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    parent_id = SelectField('Parent', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[Optional()])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])


class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])


class MaterialForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    type = SelectField('Type', choices=[('file', 'File'), ('video', 'Video')])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    file = FileField('File', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'], 'Allowed files: PDF, DOC, PPT, Images')
    ])
    video_url = StringField('YouTube URL', validators=[Optional(), Length(max=500)])


class PaymentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    paid_date = DateField('Paid Date', validators=[Optional()])
    is_paid = BooleanField('Paid')
    notes = TextAreaField('Notes', validators=[Optional()])

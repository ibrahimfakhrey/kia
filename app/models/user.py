from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


# Admin panel sections a manager can be limited to: key -> (label, landing endpoint).
# Managing other managers is not listed here: it is reserved for full-access admins.
ADMIN_SECTIONS = {
    'users': ('أولياء الأمور', 'admin.users_list'),
    'students': ('الطلاب', 'admin.students_list'),
    'classes': ('الفصول', 'admin.classes_list'),
    'attendance': ('تسجيل الحضور', 'admin.attendance_list'),
    'subjects': ('المواد', 'admin.subjects_list'),
    'materials': ('المحتوى التعليمي', 'admin.materials_list'),
    'payments': ('المدفوعات', 'admin.payments_list'),
    'announcements': ('الإعلانات', 'admin.announcements_list'),
    'password_reset': ('إعادة تعيين كلمات المرور', 'admin.password_reset'),
}


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='parent')  # 'admin' or 'parent'
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    fcm_token = db.Column(db.String(255))  # Firebase Cloud Messaging token
    is_active = db.Column(db.Boolean, default=True)
    # Admins only. NULL = full access; otherwise a comma-separated list of
    # ADMIN_SECTIONS keys the manager is limited to ('' = no sections).
    permissions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    students = db.relationship('Student', backref='parent', lazy='dynamic')
    marked_attendance = db.relationship('Attendance', backref='admin', lazy='dynamic', foreign_keys='Attendance.marked_by')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def has_full_access(self):
        return self.is_admin() and self.permissions is None

    @property
    def permission_list(self):
        """Sections this admin may open, in sidebar order."""
        if not self.is_admin():
            return []
        if self.permissions is None:
            return list(ADMIN_SECTIONS)
        granted = {p.strip() for p in self.permissions.split(',')}
        return [key for key in ADMIN_SECTIONS if key in granted]

    def has_permission(self, section):
        return section in self.permission_list

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

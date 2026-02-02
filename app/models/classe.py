from datetime import datetime
from app.extensions import db


class Classe(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    students = db.relationship('Student', backref='classe', lazy='dynamic')
    subjects = db.relationship('Subject', backref='classe', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='classe', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'student_count': self.students.count(),
            'subject_count': self.subjects.count(),
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Classe {self.name}>'

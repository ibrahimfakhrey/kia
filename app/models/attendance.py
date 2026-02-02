from datetime import datetime
from app.extensions import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'present' or 'absent'
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Admin who marked it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add unique constraint: one attendance record per student per day
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_student_date_attendance'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'class_id': self.class_id,
            'class_name': self.classe.name if self.classe else None,
            'date': self.date.isoformat(),
            'status': self.status,
            'marked_by': self.marked_by,
            'marked_by_name': self.admin.full_name if self.admin else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Date:{self.date} Status:{self.status}>'

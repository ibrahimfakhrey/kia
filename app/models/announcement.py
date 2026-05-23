from datetime import datetime
from app.extensions import db


announcement_targets = db.Table(
    'announcement_targets',
    db.Column('announcement_id', db.Integer, db.ForeignKey('announcements.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # 'all' | 'role' | 'users'
    target_type = db.Column(db.String(20), nullable=False, default='all')
    # populated only when target_type == 'role'
    target_role = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', foreign_keys=[created_by])
    target_users = db.relationship(
        'User',
        secondary=announcement_targets,
        lazy='dynamic',
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'target_type': self.target_type,
            'target_role': self.target_role,
            'is_active': self.is_active,
            'created_by_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Announcement {self.id} {self.title}>'

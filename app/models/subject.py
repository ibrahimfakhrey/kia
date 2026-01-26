from datetime import datetime
from app.extensions import db


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    materials = db.relationship('Material', backref='subject', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'class_name': self.classe.name if self.classe else None,
            'name': self.name,
            'description': self.description,
            'material_count': self.materials.count(),
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Subject {self.name}>'

from datetime import datetime
from app.extensions import db


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'file' or 'video'
    file_url = db.Column(db.String(500))  # S3 URL for files
    video_url = db.Column(db.String(500))  # YouTube URL for videos
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'title': self.title,
            'type': self.type,
            'file_url': self.file_url,
            'video_url': self.video_url,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Material {self.title}>'

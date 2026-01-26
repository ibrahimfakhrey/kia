"""
Seed script to create initial admin user and sample data.
Run with: python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, Classe, Subject

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()

    # Check if admin already exists
    admin = User.query.filter_by(email='admin@kia.com').first()
    if not admin:
        admin = User(
            email='admin@kia.com',
            full_name='Admin User',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('Admin user created: admin@kia.com / admin123')
    else:
        print('Admin user already exists')

    # Create sample classes if none exist
    if Classe.query.count() == 0:
        classes = [
            Classe(name='Nursery 1', description='Ages 2-3'),
            Classe(name='Nursery 2', description='Ages 3-4'),
            Classe(name='KG1', description='Kindergarten 1 - Ages 4-5'),
            Classe(name='KG2', description='Kindergarten 2 - Ages 5-6'),
        ]
        db.session.add_all(classes)
        print('Sample classes created')

        # Create sample subjects for KG1
        db.session.flush()  # Get IDs
        kg1 = Classe.query.filter_by(name='KG1').first()
        if kg1:
            subjects = [
                Subject(name='Math', class_id=kg1.id, description='Numbers and counting'),
                Subject(name='English', class_id=kg1.id, description='Alphabet and phonics'),
                Subject(name='Arabic', class_id=kg1.id, description='Arabic language basics'),
                Subject(name='Science', class_id=kg1.id, description='Nature and discovery'),
            ]
            db.session.add_all(subjects)
            print('Sample subjects created for KG1')

    db.session.commit()
    print('Database seeded successfully!')

#!/usr/bin/env python3
"""Seed test data for KIA application."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Student, Classe, Subject, Material, Payment
from datetime import date, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        print("Seeding test data...")

        # Create classes
        classes_data = [
            {"name": "KG1", "description": "Kindergarten 1"},
            {"name": "KG2", "description": "Kindergarten 2"},
            {"name": "Grade 1", "description": "First Grade"},
            {"name": "Grade 2", "description": "Second Grade"},
        ]

        classes = []
        for c_data in classes_data:
            existing = Classe.query.filter_by(name=c_data["name"]).first()
            if not existing:
                c = Classe(**c_data)
                db.session.add(c)
                classes.append(c)
            else:
                classes.append(existing)

        db.session.commit()
        print(f"Created {len(classes)} classes")

        # Create subjects (one for each class)
        subjects_data = [
            {"name": "Arabic", "description": "Arabic Language", "class_idx": 0},
            {"name": "English", "description": "English Language", "class_idx": 0},
            {"name": "Math", "description": "Mathematics", "class_idx": 1},
            {"name": "Science", "description": "General Science", "class_idx": 1},
            {"name": "Arabic", "description": "Arabic Language", "class_idx": 2},
            {"name": "Math", "description": "Mathematics", "class_idx": 2},
            {"name": "English", "description": "English Language", "class_idx": 3},
            {"name": "Science", "description": "General Science", "class_idx": 3},
        ]

        subjects = []
        for s_data in subjects_data:
            class_id = classes[s_data["class_idx"]].id
            existing = Subject.query.filter_by(name=s_data["name"], class_id=class_id).first()
            if not existing:
                s = Subject(
                    name=s_data["name"],
                    description=s_data["description"],
                    class_id=class_id
                )
                db.session.add(s)
                subjects.append(s)
            else:
                subjects.append(existing)

        db.session.commit()
        print(f"Created {len(subjects)} subjects")

        # Create parent users
        parents_data = [
            {"email": "ahmed@test.com", "phone": "0501234567", "full_name": "Ahmed Al-Rashid"},
            {"email": "fatima@test.com", "phone": "0507654321", "full_name": "Fatima Hassan"},
            {"email": "omar@test.com", "phone": "0509876543", "full_name": "Omar Al-Farsi"},
            {"email": "sara@test.com", "phone": "0503456789", "full_name": "Sara Mohammed"},
            {"email": "khalid@test.com", "phone": "0502345678", "full_name": "Khalid Ibrahim"},
        ]

        parents = []
        for p_data in parents_data:
            existing = User.query.filter_by(email=p_data["email"]).first()
            if not existing:
                p = User(
                    email=p_data["email"],
                    phone=p_data["phone"],
                    full_name=p_data["full_name"],
                    role='parent',
                    is_active=True
                )
                p.set_password("password123")
                db.session.add(p)
                parents.append(p)
            else:
                parents.append(existing)

        db.session.commit()
        print(f"Created {len(parents)} parents")

        # Create students
        students_data = [
            {"full_name": "Yusuf Ahmed", "date_of_birth": date(2019, 3, 15), "parent_idx": 0, "class_idx": 0},
            {"full_name": "Maryam Ahmed", "date_of_birth": date(2017, 7, 22), "parent_idx": 0, "class_idx": 2},
            {"full_name": "Ali Fatima", "date_of_birth": date(2018, 11, 8), "parent_idx": 1, "class_idx": 1},
            {"full_name": "Layla Omar", "date_of_birth": date(2019, 5, 3), "parent_idx": 2, "class_idx": 0},
            {"full_name": "Hassan Omar", "date_of_birth": date(2016, 9, 17), "parent_idx": 2, "class_idx": 3},
            {"full_name": "Noor Sara", "date_of_birth": date(2018, 2, 28), "parent_idx": 3, "class_idx": 1},
            {"full_name": "Adam Khalid", "date_of_birth": date(2017, 12, 10), "parent_idx": 4, "class_idx": 2},
        ]

        students = []
        for s_data in students_data:
            existing = Student.query.filter_by(full_name=s_data["full_name"]).first()
            if not existing:
                s = Student(
                    full_name=s_data["full_name"],
                    date_of_birth=s_data["date_of_birth"],
                    parent_id=parents[s_data["parent_idx"]].id,
                    class_id=classes[s_data["class_idx"]].id
                )
                db.session.add(s)
                students.append(s)
            else:
                students.append(existing)

        db.session.commit()
        print(f"Created {len(students)} students")

        # Create payments
        today = date.today()
        payments_data = [
            {"student_idx": 0, "amount": 5000.00, "due_date": today + timedelta(days=7), "is_paid": False, "notes": "Term 1 Tuition"},
            {"student_idx": 1, "amount": 5500.00, "due_date": today + timedelta(days=14), "is_paid": False, "notes": "Term 1 Tuition"},
            {"student_idx": 2, "amount": 5000.00, "due_date": today - timedelta(days=3), "is_paid": True, "paid_date": today - timedelta(days=5), "notes": "Term 1 Tuition"},
            {"student_idx": 3, "amount": 5000.00, "due_date": today + timedelta(days=21), "is_paid": False, "notes": "Term 1 Tuition"},
            {"student_idx": 4, "amount": 6000.00, "due_date": today + timedelta(days=5), "is_paid": False, "notes": "Term 1 Tuition"},
            {"student_idx": 5, "amount": 5000.00, "due_date": today - timedelta(days=10), "is_paid": True, "paid_date": today - timedelta(days=12), "notes": "Term 1 Tuition"},
            {"student_idx": 6, "amount": 5500.00, "due_date": today + timedelta(days=30), "is_paid": False, "notes": "Term 1 Tuition"},
        ]

        for pay_data in payments_data:
            existing = Payment.query.filter_by(
                student_id=students[pay_data["student_idx"]].id,
                notes=pay_data["notes"]
            ).first()
            if not existing:
                p = Payment(
                    student_id=students[pay_data["student_idx"]].id,
                    amount=pay_data["amount"],
                    due_date=pay_data["due_date"],
                    is_paid=pay_data["is_paid"],
                    paid_date=pay_data.get("paid_date"),
                    notes=pay_data["notes"]
                )
                db.session.add(p)

        db.session.commit()
        print("Created payments")

        # Create some materials
        materials_data = [
            {"title": "Arabic Alphabet", "subject_idx": 0, "type": "file"},
            {"title": "Numbers 1-10", "subject_idx": 2, "type": "video", "video_url": "https://www.youtube.com/watch?v=example1"},
            {"title": "English ABC", "subject_idx": 1, "type": "file"},
            {"title": "Basic Addition", "subject_idx": 5, "type": "video", "video_url": "https://www.youtube.com/watch?v=example2"},
        ]

        for m_data in materials_data:
            existing = Material.query.filter_by(title=m_data["title"]).first()
            if not existing:
                m = Material(
                    title=m_data["title"],
                    subject_id=subjects[m_data["subject_idx"]].id,
                    type=m_data["type"],
                    file_url=m_data.get("file_url"),
                    video_url=m_data.get("video_url"),
                    order_index=0
                )
                db.session.add(m)

        db.session.commit()
        print("Created materials")

        print("\n=== Test Data Summary ===")
        print(f"Classes: {Classe.query.count()}")
        print(f"Subjects: {Subject.query.count()}")
        print(f"Parents: {User.query.filter_by(role='parent').count()}")
        print(f"Students: {Student.query.count()}")
        print(f"Payments: {Payment.query.count()}")
        print(f"Materials: {Material.query.count()}")
        print("\nTest data seeded successfully!")
        print("\nParent login credentials:")
        print("Email: ahmed@test.com, Password: password123")

if __name__ == "__main__":
    seed_data()

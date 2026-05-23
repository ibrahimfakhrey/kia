"""Create or promote an admin user.

Usage (interactive):
    python3 scripts/create_admin.py

Usage (non-interactive):
    python3 scripts/create_admin.py --email admin@kia.com --name "Admin" --password "<pw>"

If a user with the given email already exists, this script promotes them
to admin, activates the account, and resets the password.
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from app import create_app
from app.extensions import db
from app.models import User


def main():
    parser = argparse.ArgumentParser(description="Create or promote an admin user.")
    parser.add_argument("--email", help="Admin email")
    parser.add_argument("--name", help="Full name")
    parser.add_argument("--password", help="Password (omit to be prompted)")
    args = parser.parse_args()

    email = args.email or input("Email: ").strip()
    name = args.name or input("Full name: ").strip()
    password = args.password or getpass.getpass("Password: ")

    if not email or not name or not password:
        print("Error: email, name, and password are required.", file=sys.stderr)
        sys.exit(1)

    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = "admin"
            user.is_active = True
            user.full_name = name
            user.set_password(password)
            db.session.commit()
            print(f"Updated existing user to admin: {email}")
        else:
            user = User(email=email, full_name=name, role="admin", is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created admin: {email}")


if __name__ == "__main__":
    main()

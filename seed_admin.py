"""
Tengeneza (au badilisha password ya) mtumiaji wa kwanza wa Admin.

Tumia hii mara moja tu unapoanzisha database mpya, au unapohitaji
ku-reset password ya admin. SIYO route ya wavuti (kwa usalama) -
inaendeshwa moja kwa moja kwenye terminal.

Matumizi:
    python seed_admin.py
"""

import getpass

from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash


def main():
    with app.app_context():

        print("=== Tengeneza / Sasisha Admin ===")

        fullname = input("Jina kamili [Admin]: ").strip() or "Admin"
        email = input("Barua pepe: ").strip()

        if not email:
            print("Barua pepe inahitajika. Imekatishwa.")
            return

        password = getpass.getpass("Password mpya (angalau herufi 6): ")

        if len(password) < 6:
            print("Password ni fupi mno (angalau herufi 6). Imekatishwa.")
            return

        confirm = getpass.getpass("Rudia password: ")

        if password != confirm:
            print("Password hazifanani. Imekatishwa.")
            return

        user = User.query.filter_by(email=email).first()

        if user:
            user.fullname = fullname
            user.password = generate_password_hash(password)
            db.session.commit()
            print(f"Umesasisha password ya mtumiaji aliyepo: {email}")
        else:
            user = User(
                fullname=fullname,
                email=email,
                password=generate_password_hash(password),
                role="admin",
            )
            db.session.add(user)
            db.session.commit()
            print(f"Umetengeneza admin mpya: {email}")


if __name__ == "__main__":
    main()

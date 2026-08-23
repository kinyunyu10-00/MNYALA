from flask_login import UserMixin
from extensions import db
from datetime import datetime


# ==========================================================
# USER MODEL
# ==========================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    # ID CREATIONS
    
    account_id = db.Column(db.String(30), unique=True, nullable=True)

    username = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    username = db.Column(
        db.String(100),
        nullable=False
    )

    fullname = db.Column(
        db.String(150),
        nullable=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    # ======================================================
    # USER ROLE
    # ======================================================

    role = db.Column(
        db.String(20),
        nullable=False,
        default="customer"
    )

    # ======================================================
    # ACCOUNT STATUS
    # ======================================================

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # ======================================================
    # EMAIL VERIFICATION
    # ======================================================

    email_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    verification_token = db.Column(
        db.String(255),
        nullable=True
    )

    verification_token_expires = db.Column(
        db.DateTime,
        nullable=True
    )

    # ======================================================
    # PASSWORD RESET
    # ======================================================

    reset_token = db.Column(
        db.String(255),
        nullable=True
    )

    reset_token_expires = db.Column(
        db.DateTime,
        nullable=True
    )

    # ======================================================
    # CREATED AT
    # ======================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================================================
# MESSAGE MODEL
# ==========================================================

class Message(db.Model):

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    fullname = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(30)
    )

    subject = db.Column(
        db.String(100)
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )


# ==========================================================
# ACTIVITY LOG MODEL
# ==========================================================

class ActivityLog(db.Model):

    __tablename__ = "activity_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    action = db.Column(
        db.String(200),
        nullable=False
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    ip_address = db.Column(
        db.String(50),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="activities",
        lazy=True
    )

    def __repr__(self):

        return f"<ActivityLog {self.action}>"
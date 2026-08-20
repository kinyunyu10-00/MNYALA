from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

import secrets

from datetime import datetime, timedelta

from extensions import db
from flask_mail import Message
from extensions import mail

from models import (
    User,
    Message
)


auth = Blueprint("auth", __name__)


# ==========================================================
# ADMIN REQUIRED
# ==========================================================

def admin_required():

    # User hajalogin
    if "user_id" not in session:
        return False

    # Tafuta user kwenye database
    user = User.query.get(session["user_id"])

    # User hayupo tena kwenye database
    if not user:
        session.clear()
        return False

    # Admin na Super Admin wanaruhusiwa
    return user.role in ["admin", "super_admin"]


# ==========================================================
# SUPER ADMIN REQUIRED
# ==========================================================

def super_admin_required():

    # User hajalogin
    if "user_id" not in session:
        return False

    # Tafuta user kwenye database
    user = User.query.get(session["user_id"])

    # User hayupo kwenye database
    if not user:
        session.clear()
        return False

    # Super Admin pekee
    return user.role == "super_admin"


# ==========================================================
# SEND RESET EMAIL
# ==========================================================

def send_reset_email(user, reset_url):
    """Send password reset email to user"""
    try:
        # Email HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body {{
                    font-family: 'Poppins', Arial, sans-serif;
                    background: #f8fafc;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: #ffffff;
                    border-radius: 16px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #4a6cf7 0%, #6d8ff7 100%);
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header p {{
                    color: rgba(255,255,255,0.9);
                    margin: 8px 0 0;
                    font-size: 16px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #1e293b;
                    font-size: 22px;
                    margin: 0 0 16px;
                }}
                .content p {{
                    color: #64748b;
                    font-size: 16px;
                    line-height: 1.6;
                    margin: 0 0 12px;
                }}
                .btn {{
                    display: inline-block;
                    background: #4a6cf7;
                    color: white !important;
                    padding: 14px 32px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0 10px;
                    transition: all 0.3s ease;
                }}
                .btn:hover {{
                    background: #3a5bd9;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(74, 108, 247, 0.3);
                }}
                .footer {{
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e5e7eb;
                    color: #94a3b8;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #4a6cf7;
                    text-decoration: none;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 12px 16px;
                    border-radius: 4px;
                    margin: 16px 0;
                    font-size: 14px;
                    color: #92400e;
                }}
                .code-box {{
                    background: #f1f5f9;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-family: monospace;
                    font-size: 14px;
                    word-break: break-all;
                    color: #1e293b;
                    margin: 12px 0;
                }}
                @media (max-width: 480px) {{
                    .container {{
                        margin: 20px 10px;
                    }}
                    .header {{
                        padding: 30px 20px;
                    }}
                    .content {{
                        padding: 24px 20px;
                    }}
                    .btn {{
                        width: 100%;
                        text-align: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Reset Password</h1>
                    <p>MNYALA Business Management System</p>
                </div>
                <div class="content">
                    <h2>Hello {user.fullname or 'User'} 👋</h2>
                    <p>We received a request to reset the password for your MNYALA account.</p>
                    <p>Click the button below to create a new password:</p>
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="btn">Reset Password</a>
                    </div>
                    <p style="font-size: 14px; color: #94a3b8; text-align: center; margin-top: 8px;">
                        Or copy and paste this link in your browser:
                    </p>
                    <div class="code-box">
                        {reset_url}
                    </div>
                    <div class="warning">
                        ⏰ This link will expire in <strong>30 minutes</strong>.
                    </div>
                    <p style="font-size: 14px; color: #64748b; margin-top: 20px;">
                        If you didn't request this, please ignore this email or contact support.
                    </p>
                </div>
                <div class="footer">
                    <p style="margin: 0;">
                        &copy; 2026 <a href="#">MNYALA</a> Business Management System.
                    </p>
                    <p style="margin: 4px 0 0; font-size: 12px;">
                        This is an automated message, please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Reset Your Password - MNYALA
        
        Hello {user.fullname or 'User'},
        
        We received a request to reset the password for your MNYALA account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 30 minutes.
        
        If you didn't request this, please ignore this email.
        
        ---
        © 2026 MNYALA Business Management System
        """
        
        # Create message
        msg = Message(
            subject='Reset Your MNYALA Account Password',
            recipients=[user.email],
            body=text_content,
            html=html_content
        )
        
        # Send email
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"❌ Email send error: {str(e)}")
        return False


# ==========================================================
# LOGIN
# ==========================================================
@auth.route("/login", methods=["GET", "POST"])
def login():

    # ------------------------------------------------------
    # ALREADY LOGGED IN
    # ------------------------------------------------------

    if "user_id" in session:

        user = User.query.get(session["user_id"])

        if user:

            if user.role in ["admin", "super_admin"]:
                return redirect(
                    url_for("auth.dashboard")
                )

            elif user.role == "customer":
                return redirect(
                    url_for("public.home")
                )

        session.clear()

    # ------------------------------------------------------
    # LOGIN FORM
    # ------------------------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        ).strip()

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # --------------------------------------------------
        # FIND USER
        # --------------------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()

        # --------------------------------------------------
        # CHECK USER + PASSWORD
        # --------------------------------------------------

        if user and check_password_hash(
            user.password,
            password
        ):

            # ------------------------------------------------
            # CREATE SESSION
            # ------------------------------------------------

            session.clear()

            session["user_id"] = user.id
            session["user_role"] = user.role

            # ------------------------------------------------
            # SUPER ADMIN
            # ------------------------------------------------

            if user.role == "super_admin":

                flash(
                    "Welcome, Super Administrator!",
                    "success"
                )

                return redirect(
                    url_for("auth.dashboard")
                )

            # ------------------------------------------------
            # ADMIN
            # ------------------------------------------------

            elif user.role == "admin":

                flash(
                    "Welcome to the Admin Dashboard.",
                    "success"
                )

                return redirect(
                    url_for("auth.dashboard")
                )

            # ------------------------------------------------
            # CUSTOMER
            # ------------------------------------------------

            elif user.role == "customer":

                flash(
                    "Welcome back!",
                    "success"
                )

                return redirect(
                    url_for("public.home")
                )

            # ------------------------------------------------
            # UNKNOWN ROLE
            # ------------------------------------------------

            else:

                session.clear()

                flash(
                    "Your account role is not recognized.",
                    "danger"
                )

                return redirect(
                    url_for("auth.login")
                )

        # --------------------------------------------------
        # INVALID LOGIN
        # --------------------------------------------------

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )


# ==========================================================
# FORGOT PASSWORD - WITH EMAIL
# ==========================================================

@auth.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    # ------------------------------------------------------
    # SHOW PAGE
    # ------------------------------------------------------

    if request.method == "GET":
        return render_template(
            "auth/forgot_password.html"
        )

    # ------------------------------------------------------
    # GET EMAIL
    # ------------------------------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    # ------------------------------------------------------
    # VALIDATE EMAIL
    # ------------------------------------------------------

    if not email:

        flash(
            "Please enter your email address.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ------------------------------------------------------
    # FIND USER
    # ------------------------------------------------------

    user = User.query.filter_by(
        email=email
    ).first()

    # ------------------------------------------------------
    # USER NOT FOUND
    # ------------------------------------------------------

    if not user:

        flash(
            "No account was found with that email address.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ------------------------------------------------------
    # GENERATE SECURE TOKEN
    # ------------------------------------------------------

    token = secrets.token_urlsafe(32)

    # ------------------------------------------------------
    # TOKEN EXPIRATION (30 minutes)
    # ------------------------------------------------------

    expires_at = (
        datetime.utcnow()
        + timedelta(minutes=30)
    )

    # ------------------------------------------------------
    # SAVE TOKEN TO USER
    # ------------------------------------------------------

    user.reset_token = token
    user.reset_token_expires = expires_at
    db.session.commit()

    # ------------------------------------------------------
    # CREATE RESET URL
    # ------------------------------------------------------

    reset_url = url_for(
        "auth.reset_password",
        token=token,
        _external=True
    )

    # ------------------------------------------------------
    # SEND EMAIL
    # ------------------------------------------------------

    email_sent = send_reset_email(user, reset_url)

    # ------------------------------------------------------
    # CHECK EMAIL STATUS
    # ------------------------------------------------------

    if email_sent:
        flash(
            "Password reset instructions have been sent to your email.",
            "success"
        )
    else:
        flash(
            "Unable to send email. Please try again later.",
            "danger"
        )
        
        # Clear token if email failed
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()

    return redirect(
        url_for("auth.login")
    )


# ==========================================================
# RESET PASSWORD
# ==========================================================

@auth.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    # ------------------------------------------------------
    # FIND USER USING RESET TOKEN
    # ------------------------------------------------------

    user = User.query.filter_by(
        reset_token=token
    ).first()

    # ------------------------------------------------------
    # TOKEN NOT FOUND
    # ------------------------------------------------------

    if not user:

        flash(
            "Invalid or expired password reset link.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ------------------------------------------------------
    # CHECK TOKEN EXPIRATION
    # ------------------------------------------------------

    if (
        not user.reset_token_expires
        or datetime.utcnow() > user.reset_token_expires
    ):

        # Clear expired token
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()

        flash(
            "This password reset link has expired.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ------------------------------------------------------
    # GET REQUEST - Display reset password page
    # ------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ------------------------------------------------------
    # POST REQUEST
    # ------------------------------------------------------

    password = request.form.get(
        "password",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password",
        ""
    ).strip()

    # ------------------------------------------------------
    # REQUIRED FIELDS
    # ------------------------------------------------------

    if not password or not confirm_password:

        flash(
            "Both password fields are required.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ------------------------------------------------------
    # PASSWORD LENGTH
    # ------------------------------------------------------

    if len(password) < 6:

        flash(
            "Password must be at least 6 characters.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ------------------------------------------------------
    # PASSWORD MATCH
    # ------------------------------------------------------

    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ------------------------------------------------------
    # PREVENT SAME PASSWORD
    # ------------------------------------------------------

    if check_password_hash(
        user.password,
        password
    ):

        flash(
            "New password must be different from your current password.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ------------------------------------------------------
    # HASH NEW PASSWORD
    # ------------------------------------------------------

    user.password = generate_password_hash(
        password
    )

    # ------------------------------------------------------
    # CLEAR USED RESET TOKEN
    # ------------------------------------------------------

    user.reset_token = None
    user.reset_token_expires = None

    # ------------------------------------------------------
    # SAVE DATABASE
    # ------------------------------------------------------

    db.session.commit()

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    flash(
        "Password reset successfully. You can now login.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@auth.route("/dashboard")
def dashboard():

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access the admin dashboard.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # MESSAGE STATISTICS
    # ------------------------------------------------------

    total_messages = Message.query.count()

    unread_messages = Message.query.filter_by(
        is_read=False
    ).count()

    read_messages = Message.query.filter_by(
        is_read=True
    ).count()

    # ------------------------------------------------------
    # LATEST MESSAGES
    # ------------------------------------------------------

    latest_messages = Message.query.order_by(
        Message.created_at.desc()
    ).limit(5).all()

    # ------------------------------------------------------
    # RENDER DASHBOARD
    # ------------------------------------------------------

    return render_template(
        "admin/dashboard.html",
        total_messages=total_messages,
        unread_messages=unread_messages,
        read_messages=read_messages,
        latest_messages=latest_messages
    )


# ==========================================================
# MESSAGES
# ==========================================================

@auth.route("/messages")
def messages():

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access messages.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # GET ALL MESSAGES
    # ------------------------------------------------------

    messages = Message.query.order_by(
        Message.created_at.desc()
    ).all()

    # ------------------------------------------------------
    # STATISTICS
    # ------------------------------------------------------

    total = Message.query.count()

    unread = Message.query.filter_by(
        is_read=False
    ).count()

    read = Message.query.filter_by(
        is_read=True
    ).count()

    # ------------------------------------------------------
    # RENDER
    # ------------------------------------------------------

    return render_template(
        "admin/messages.html",
        messages=messages,
        total=total,
        unread=unread,
        read=read
    )


# ==========================================================
# VIEW SINGLE MESSAGE
# ==========================================================

@auth.route("/messages/<int:id>")
def view_message(id):

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to view this message.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # FIND MESSAGE
    # ------------------------------------------------------

    message = Message.query.get_or_404(
        id
    )

    # ------------------------------------------------------
    # MARK AS READ
    # ------------------------------------------------------

    message.is_read = True

    db.session.commit()

    # ------------------------------------------------------
    # RENDER
    # ------------------------------------------------------

    return render_template(
        "admin/view_message.html",
        message=message
    )


# ==========================================================
# DELETE MESSAGE
# ==========================================================

@auth.route(
    "/messages/delete/<int:id>"
)
def delete_message(id):

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to delete messages.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # FIND MESSAGE
    # ------------------------------------------------------

    message = Message.query.get_or_404(
        id
    )

    # ------------------------------------------------------
    # DELETE
    # ------------------------------------------------------

    db.session.delete(
        message
    )

    db.session.commit()

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    flash(
        "Message deleted successfully.",
        "success"
    )

    return redirect(
        url_for("auth.messages")
    )


# ==========================================================
# SETTINGS
# ==========================================================

@auth.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access settings.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # GET CURRENT USER
    # ------------------------------------------------------

    user = User.query.get_or_404(
        session["user_id"]
    )

    # ------------------------------------------------------
    # UPDATE PROFILE
    # ------------------------------------------------------

    if request.method == "POST":

        fullname = request.form.get(
            "fullname",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not fullname or not email:

            flash(
                "Full name and email are required.",
                "danger"
            )

            return redirect(
                url_for("auth.settings")
            )

        # --------------------------------------------------
        # CHECK DUPLICATE EMAIL
        # --------------------------------------------------

        existing_user = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if existing_user:

            flash(
                "This email is already being used.",
                "danger"
            )

            return redirect(
                url_for("auth.settings")
            )

        # --------------------------------------------------
        # UPDATE USER
        # --------------------------------------------------

        user.fullname = fullname

        user.email = email

        db.session.commit()

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # DISPLAY SETTINGS
    # ------------------------------------------------------

    return render_template(
        "admin/settings.html",
        user=user
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@auth.route(
    "/settings/password",
    methods=["POST"]
)
def change_password():

    # ------------------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to change password.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------------------
    # GET USER
    # ------------------------------------------------------

    user = User.query.get_or_404(
        session["user_id"]
    )

    # ------------------------------------------------------
    # GET FORM DATA
    # ------------------------------------------------------

    current_password = request.form.get(
        "current_password",
        ""
    ).strip()

    new_password = request.form.get(
        "new_password",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password",
        ""
    ).strip()

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if (
        not current_password
        or not new_password
        or not confirm_password
    ):

        flash(
            "All password fields are required.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # CHECK CURRENT PASSWORD
    # ------------------------------------------------------

    if not check_password_hash(
        user.password,
        current_password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # PASSWORD LENGTH
    # ------------------------------------------------------

    if len(new_password) < 6:

        flash(
            "New password must be at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # CONFIRM PASSWORD
    # ------------------------------------------------------

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # PREVENT SAME PASSWORD
    # ------------------------------------------------------

    if check_password_hash(
        user.password,
        new_password
    ):

        flash(
            "New password must be different from your current password.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------------------
    # HASH NEW PASSWORD
    # ------------------------------------------------------

    user.password = generate_password_hash(
        new_password
    )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    db.session.commit()

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    flash(
        "Password changed successfully.",
        "success"
    )

    return redirect(
        url_for("auth.settings")
    )


# ==========================================================
# LOGOUT
# ==========================================================

@auth.route("/logout")
def logout():

    # ------------------------------------------------------
    # CLEAR SESSION
    # ------------------------------------------------------

    session.clear()

    # ------------------------------------------------------
    # SUCCESS MESSAGE
    # ------------------------------------------------------

    flash(
        "Logged out successfully.",
        "success"
    )

    # ------------------------------------------------------
    # REDIRECT TO LOGIN
    # ------------------------------------------------------

    return redirect(
        url_for("auth.login")
    )
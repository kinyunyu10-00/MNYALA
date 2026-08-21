from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
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
    Message,
    ActivityLog
)

auth = Blueprint("auth", __name__)


# ==========================================================
# ADMIN REQUIRED - CHECK FUNCTION
# ==========================================================

def admin_required():
    """Check if user is admin or super admin"""
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
# SUPER ADMIN REQUIRED - CHECK FUNCTION
# ==========================================================

def super_admin_required():
    """Check if user is super admin"""
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
# ACTIVITY LOG
# ==========================================================

def log_activity(user_id, action, details=None):
    """Log user activity"""
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"❌ Log error: {str(e)}")


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
            <title>Reset Your Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f8fafc; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; }}
                .header {{ background: #4a6cf7; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center; }}
                .btn {{ display: inline-block; background: #4a6cf7; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; }}
                .footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Reset Password</h1>
                    <p>MNYALA Business Management System</p>
                </div>
                <div style="padding: 20px;">
                    <h2>Hello {user.fullname or 'User'} 👋</h2>
                    <p>We received a request to reset your password.</p>
                    <p>Click the button below to create a new password:</p>
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="btn">Reset Password</a>
                    </div>
                    <p style="font-size: 14px; color: #94a3b8; text-align: center; margin-top: 8px;">
                        Or copy this link: {reset_url}
                    </p>
                    <p style="font-size: 14px; color: #64748b; margin-top: 20px;">
                        This link will expire in 30 minutes.
                    </p>
                    <p style="font-size: 14px; color: #64748b;">
                        If you didn't request this, please ignore this email.
                    </p>
                </div>
                <div class="footer">
                    © 2026 MNYALA Business Management System
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = Message(
            subject='Reset Your MNYALA Account Password',
            recipients=[user.email],
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

            # Log login activity
            log_activity(
                user.id,
                "User logged in",
                f"Email: {user.email}"
            )

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
# FORGOT PASSWORD
# ==========================================================

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    
    # ------------------------------------------------------
    # SHOW PAGE (GET)
    # ------------------------------------------------------
    if request.method == "GET":
        return render_template("auth/forgot_password.html")
    
    # ------------------------------------------------------
    # PROCESS FORM (POST)
    # ------------------------------------------------------
    email = request.form.get("email", "").strip().lower()
    
    # ------------------------------------------------------
    # VALIDATE EMAIL
    # ------------------------------------------------------
    if not email:
        flash("Please enter your email address.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    # ------------------------------------------------------
    # FIND USER
    # ------------------------------------------------------
    user = User.query.filter_by(email=email).first()
    
    # ------------------------------------------------------
    # IF USER NOT FOUND - SHOW SAME MESSAGE (Security)
    # ------------------------------------------------------
    if not user:
        flash("If an account exists with that email, a reset link has been sent.", "info")
        flash("📧 Please check your inbox (and spam folder).", "info")
        return render_template("auth/forgot_password.html", email_sent=True, user_email=email)
    
    # ------------------------------------------------------
    # GENERATE TOKEN
    # ------------------------------------------------------
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    user.reset_token = token
    user.reset_token_expires = expires_at
    db.session.commit()
    
    # ------------------------------------------------------
    # CREATE RESET URL
    # ------------------------------------------------------
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    
    # ------------------------------------------------------
    # SEND EMAIL
    # ------------------------------------------------------
    email_sent = send_reset_email(user, reset_url)
    
    # ------------------------------------------------------
    # REDIRECT WITH MESSAGE
    # ------------------------------------------------------
    if email_sent:
        flash("✅ Password reset link has been sent to your email address!", "success")
        flash("📧 Please check your inbox (and spam folder). The link expires in 30 minutes.", "info")
    else:
        flash("❌ Unable to send email. Please try again later.", "danger")
        flash(f"🔗 Use this link: {reset_url}", "warning")
    
    # ------------------------------------------------------
    # RENDER SAME PAGE WITH SUCCESS MESSAGE
    # ------------------------------------------------------
    return render_template("auth/forgot_password.html", email_sent=True, user_email=email)


# ==========================================================
# RESET PASSWORD
# ==========================================================

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
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

    # Log password reset
    log_activity(
        user.id,
        "Password reset successfully",
        f"User: {user.email}"
    )

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

@auth.route("/messages/delete/<int:id>")
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

@auth.route("/settings", methods=["GET", "POST"])
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

@auth.route("/settings/password", methods=["POST"])
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

    # Log password change
    log_activity(
        user.id,
        "Password changed",
        f"User: {user.email}"
    )

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

    # Log logout activity
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            log_activity(
                user.id,
                "User logged out",
                f"Email: {user.email}"
            )

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


# ==========================================================
# SUPER ADMIN - DASHBOARD
# ==========================================================

@auth.route("/super-admin/dashboard")
def super_admin_dashboard():
    """Super Admin Dashboard"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    # Statistics
    total_users = User.query.count()
    total_admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).count()
    total_customers = User.query.filter_by(role='customer').count()
    total_active = User.query.filter_by(is_active=True).count() if hasattr(User, 'is_active') else total_users
    
    # Recent users
    recent_users = User.query.order_by(
        User.id.desc()
    ).limit(10).all()
    
    return render_template(
        "admin/super_admin/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        total_customers=total_customers,
        total_active=total_active,
        recent_users=recent_users
    )


# ==========================================================
# SUPER ADMIN - MANAGE ADMINS
# ==========================================================

@auth.route("/super-admin/admins")
def manage_admins():
    """View all administrators"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admins = User.query.filter(
        User.role.in_(['admin', 'super_admin'])
    ).order_by(User.id.desc()).all()
    
    return render_template(
        "admin/super_admin/admins.html",
        admins=admins
    )


@auth.route("/super-admin/admins/add", methods=["GET", "POST"])
def add_admin():
    """Add new administrator"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "admin").strip()
        
        # Validation
        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        # Check if email exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash(f"Email '{email}' is already registered.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        # Create admin
        new_admin = User(
            fullname=fullname,
            username=fullname.replace(" ", "_").lower(),
            email=email,
            password=generate_password_hash(password),
            role=role,
            email_verified=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        # Log activity
        log_activity(
            session['user_id'],
            f"Added new {role}: {email}",
            f"Name: {fullname}"
        )
        
        flash(f"✅ {role.title()} '{fullname}' added successfully!", "success")
        return redirect(url_for("auth.manage_admins"))
    
    return render_template("admin/super_admin/add_admin.html")


@auth.route("/super-admin/admins/edit/<int:user_id>", methods=["GET", "POST"])
def edit_admin(user_id):
    """Edit administrator details"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admin = User.query.get_or_404(user_id)
    
    # Prevent editing self
    if admin.id == session['user_id']:
        flash("You cannot edit your own account here. Use Settings.", "warning")
        return redirect(url_for("auth.manage_admins"))
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "admin").strip()
        is_active = request.form.get("is_active") == "on"
        
        # Validation
        if not fullname or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("auth.edit_admin", user_id=user_id))
        
        # Check email duplicate
        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            flash(f"Email '{email}' is already taken.", "danger")
            return redirect(url_for("auth.edit_admin", user_id=user_id))
        
        # Update
        admin.fullname = fullname
        admin.username = fullname.replace(" ", "_").lower()
        admin.email = email
        admin.role = role
        if hasattr(admin, 'is_active'):
            admin.is_active = is_active
        
        db.session.commit()
        
        # Log activity
        log_activity(
            session['user_id'],
            f"Updated admin: {email}",
            f"Role: {role}"
        )
        
        flash(f"✅ Admin '{fullname}' updated successfully!", "success")
        return redirect(url_for("auth.manage_admins"))
    
    return render_template("admin/super_admin/edit_admin.html", admin=admin)


@auth.route("/super-admin/admins/delete/<int:user_id>", methods=["POST"])
def delete_admin(user_id):
    """Delete administrator"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admin = User.query.get_or_404(user_id)
    
    # Prevent deleting self
    if admin.id == session['user_id']:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("auth.manage_admins"))
    
    # Prevent deleting the last super_admin
    if admin.role == 'super_admin':
        super_admins = User.query.filter_by(role='super_admin').count()
        if super_admins <= 1:
            flash("Cannot delete the last Super Admin.", "danger")
            return redirect(url_for("auth.manage_admins"))
    
    # Log before deletion
    log_activity(
        session['user_id'],
        f"Deleted admin: {admin.email}",
        f"Name: {admin.fullname}"
    )
    
    db.session.delete(admin)
    db.session.commit()
    
    flash(f"✅ Admin '{admin.fullname}' deleted successfully!", "success")
    return redirect(url_for("auth.manage_admins"))


# ==========================================================
# SUPER ADMIN - MANAGE ALL USERS
# ==========================================================

@auth.route("/super-admin/users")
def manage_users():
    """View all users"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    users = User.query.order_by(User.id.desc()).all()
    
    return render_template(
        "admin/super_admin/users.html",
        users=users
    )


@auth.route("/super-admin/users/toggle/<int:user_id>", methods=["POST"])
def toggle_user_status(user_id):
    """Activate/Deactivate user"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent toggling self
    if user.id == session['user_id']:
        flash("You cannot change your own status.", "danger")
        return redirect(url_for("auth.manage_users"))
    
    if hasattr(user, 'is_active'):
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        log_activity(
            session['user_id'],
            f"{status.title()} user: {user.email}",
            f"User: {user.fullname}"
        )
        
        flash(f"✅ User '{user.fullname}' {status}!", "success")
    else:
        flash("User status toggle not available.", "warning")
    
    return redirect(url_for("auth.manage_users"))


@auth.route("/super-admin/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Delete user"""
    
    # Check if user is super admin
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting admin/super_admin
    if user.role in ['admin', 'super_admin']:
        flash("Use the admin management page to delete administrators.", "danger")
        return redirect(url_for("auth.manage_users"))
    
    # Log before deletion
    log_activity(
        session['user_id'],
        f"Deleted user: {user.email}",
        f"Name: {user.fullname}"
    )
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"✅ User '{user.fullname}' deleted successfully!", "success")
    return redirect(url_for("auth.manage_users"))
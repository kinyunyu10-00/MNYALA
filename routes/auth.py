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
import re

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

import secrets

from datetime import datetime, timedelta

from extensions import db
from flask_mail import Message as MailMessage
from extensions import mail

from models import (
    User,
    Message,
    ActivityLog
)

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    existing_super_admin = User.query.filter_by(role='super_admin').first()
    if existing_super_admin:
        flash("System already has a Super Admin. Please login.", "info")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        if not fullname or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")
        
        # Password must be at least 9 characters
        if len(password) < 9:
            flash("Password must be at least 9 characters.", "danger")
            return render_template("auth/register.html")
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("This email is already registered.", "danger")
            return render_template("auth/register.html")
        
        new_admin = User(
            account_id="ADM-001",
            username=fullname.replace(" ", "_").lower(),
            fullname=fullname,
            email=email,
            password=generate_password_hash(password),
            role="super_admin",
            is_active=True,
            email_verified=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        log_activity(new_admin.id, "Super Admin registered", f"Email: {email}")
        
        flash("Super Admin registered successfully! Please login.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")
# ============================================================
# ACCOUNT ID GENERATOR
# ============================================================
def generate_account_id(role):
    role_prefixes = {
        "super_admin": "SADM",
        "admin": "ADM",
        "staff": "STF",
        "customer": "USR"
    }
    prefix = role_prefixes.get(role.lower(), "USR")
    
    now = datetime.now()
    year_day_str = f"{now.strftime('%Y')}{now.strftime('%d')}" # Mfano: 202623
    
    count = User.query.filter_by(role=role).count() + 1
    account_id = f"{prefix}-{year_day_str}-{count:04d}"
    
    while User.query.filter_by(account_id=account_id).first():
        count += 1
        account_id = f"{prefix}-{year_day_str}-{count:04d}"
        
    return account_id
# ============================================================
# PASSWORD POLICY
# ============================================================

def validate_password_strength(password):
    """
    Password must:
    - Have at least 9 characters
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one number
    - Contain at least one special character
    """

    if not password:
        return False, "Password is required."

    if len(password) < 9:
        return False, "Password must contain at least 9 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character."

    return True, "Password is strong."
# ==========================================================
# ADMIN REQUIRED - CHECK FUNCTION
# ==========================================================

def admin_required():
    """Check if user is admin or super admin"""
    if "user_id" not in session:
        return False

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return False

    return user.role in ["admin", "super_admin"]


# ==========================================================
# SUPER ADMIN REQUIRED - CHECK FUNCTION
# ==========================================================

def super_admin_required():
    """Check if user is super admin"""
    if "user_id" not in session:
        return False

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return False

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
# SEND PASSWORD RESET EMAIL
# ==========================================================
def send_reset_email(user, reset_url):
    """Send password reset email to user"""
    try:
        html_content = f"""..."""
        
        msg = Message(
            subject='Reset Your MNYALA Account Password',
            recipients=[user.email]
        )
        msg.html = html_content
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"❌ Email send error: {str(e)}")
        return False
# ==========================================================
# LOGIN
# ==========================================================

# ==========================================================
# LOGIN
# ==========================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    # ======================================================
    # CHECK EXISTING SESSION
    # ======================================================

    if "user_id" in session:

        user = User.query.get(session["user_id"])

        if user:

            if user.role in ["admin", "super_admin"]:
                return redirect(url_for("auth.dashboard"))

            elif user.role == "customer":
                return redirect(url_for("public.index"))

        session.clear()

    # ======================================================
    # LOGIN POST
    # ======================================================

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        ).strip()

        # ==================================================
        # VALIDATE INPUT
        # ==================================================

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # ==================================================
        # FIND USER
        # ==================================================

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # ==================================================
        # CHECK ACCOUNT STATUS
        # ==================================================

        if hasattr(user, "is_active") and not user.is_active:

            flash(
                "Your account has been deactivated. "
                "Please contact the administrator.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # ==================================================
        # CHECK PASSWORD
        # ==================================================

        if not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # ==================================================
        # CHECK PASSWORD STRENGTH
        # ==================================================

        password_valid, password_message = (
            validate_password_strength(password)
        )

        if not password_valid:

            flash(
                "Your password does not meet the current "
                "security requirements. Please reset your password.",
                "warning"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # ==================================================
        # LOGIN SUCCESS
        # ==================================================

        session.clear()

        session["user_id"] = user.id
        session["user_role"] = user.role

        # ==================================================
        # ACTIVITY LOG
        # ==================================================

        log_activity(
            user.id,
            "User logged in",
            f"Email: {user.email}"
        )

        flash(
            "Login successful.",
            "success"
        )

        # ==================================================
        # REDIRECT BY ROLE
        # ==================================================

        if user.role == "super_admin":

            return redirect(
                url_for("auth.dashboard")
            )

        elif user.role == "admin":
             return redirect(url_for("auth.admin_dashboard"))

        elif user.role == "customer":

            return redirect(
                url_for("public.index")
            )

        else:

            session.clear()

            flash(
                "Your account role is not recognized.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

    # ======================================================
    # GET REQUEST
    # ======================================================

    return render_template(
        "auth/login.html"
    )
#================================
#FORGORT PASSWORD
#=============================
@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        # ==================================================
        # GET EMAIL
        # ==================================================

        email = request.form.get(
            "email",
            ""
        ).strip().lower()


        # ==================================================
        # VALIDATE EMAIL INPUT
        # ==================================================

        if not email:

            flash(
                "Please enter your email address.",
                "danger"
            )

            return render_template(
                "auth/forgot_password.html"
            )


        # ==================================================
        # FIND USER
        # ==================================================

        user = User.query.filter_by(
            email=email
        ).first()


        # ==================================================
        # EMAIL DOES NOT EXIST
        # ==================================================

        if not user:

            flash(
                "This email address is not registered. "
                "Please enter the email associated with your account.",
                "danger"
            )

            return render_template(
                "auth/forgot_password.html"
            )


        # ==================================================
        # GENERATE RESET TOKEN
        # ==================================================

        token = secrets.token_urlsafe(32)


        # ==================================================
        # SAVE TOKEN TO USER
        # ==================================================

        user.reset_token = token

        user.reset_token_expires = (
            datetime.utcnow()
            + timedelta(minutes=30)
        )


        # ==================================================
        # SAVE TO DATABASE
        # ==================================================

        db.session.commit()


        # ==================================================
        # CREATE RESET URL
        # ==================================================

        reset_url = url_for(
            "auth.reset_password",
            token=token,
            _external=True
        )
        # ==================================================
        # SEND RESET EMAIL
        # ==================================================

        email_sent = send_reset_email(
        user,
        reset_url
        ) 

        # ==================================================
        # DEVELOPMENT TEST
        # ==================================================

        print()
        print("=" * 70)
        print("PASSWORD RESET URL")
        print(reset_url)
        print("=" * 70)
        print()


        # ==================================================
        # SHOW SUCCESS PAGE
        # ==================================================

        return render_template(
    "auth/forgot_password.html",
    email_sent=True,
    email_success=email_sent,
    user_email=email
)


    # ======================================================
    # GET REQUEST
    # ======================================================

    return render_template(
        "auth/forgot_password.html"
    )

# ==========================================================
# RESET PASSWORD
# ==========================================================

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    # ======================================================
    # FIND USER USING RESET TOKEN
    # ======================================================

    user = User.query.filter_by(
        reset_token=token
    ).first()

    # ======================================================
    # INVALID TOKEN
    # ======================================================

    if not user:

        flash(
            "This password reset link is invalid or has already been used.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ======================================================
    # CHECK TOKEN EXPIRATION
    # ======================================================

    if (
        not user.reset_token_expires
        or user.reset_token_expires < datetime.utcnow()
    ):

        user.reset_token = None
        user.reset_token_expires = None

        db.session.commit()

        flash(
            "This password reset link has expired. "
            "Please request a new one.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    # ======================================================
    # GET REQUEST
    # ======================================================

    if request.method == "GET":

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ======================================================
    # POST REQUEST
    # ======================================================

    password = request.form.get(
        "password",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password",
        ""
    ).strip()

    # ======================================================
    # REQUIRED FIELDS
    # ======================================================

    if not password or not confirm_password:

        flash(
            "Both password fields are required.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ======================================================
    # CHECK PASSWORD MATCH
    # ======================================================

    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ======================================================
    # PASSWORD STRENGTH
    # ======================================================

    password_valid, password_message = (
        validate_password_strength(password)
    )

    if not password_valid:

        flash(
            password_message,
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ======================================================
    # PREVENT SAME PASSWORD
    # ======================================================

    if check_password_hash(
        user.password,
        password
    ):

        flash(
            "Your new password must be different "
            "from your previous password.",
            "danger"
        )

        return render_template(
            "auth/reset_password.html",
            token=token
        )

    # ======================================================
    # HASH NEW PASSWORD
    # ======================================================

    user.password = generate_password_hash(
        password
    )

    # ======================================================
    # CLEAR RESET TOKEN
    # ======================================================

    user.reset_token = None
    user.reset_token_expires = None

    # ======================================================
    # SAVE CHANGES
    # ======================================================

    db.session.commit()

    # ======================================================
    # LOG ACTIVITY
    # ======================================================

    log_activity(
        user.id,
        "Password reset",
        f"Password reset for: {user.email}"
    )

    # ======================================================
    # SUCCESS
    # ======================================================

    flash(
        "Your password has been reset successfully. "
        "You can now login with your new password.",
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
    if not admin_required():
        flash("You are not authorized to access the admin dashboard.", "danger")
        return redirect(url_for("auth.login"))

    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    read_messages = Message.query.filter_by(is_read=True).count()
    latest_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_messages=total_messages,
        unread_messages=unread_messages,
        read_messages=read_messages,
        latest_messages=latest_messages
    )

#==============================-----------
#ADMIN-----DASHBOARD(wa kawaida)
#====================================
@auth.route("/admin-dashboard")
def admin_dashboard():
    if not admin_required():
        flash("You are not authorized to access the admin dashboard.", "danger")
        return redirect(url_for("auth.login"))

    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    latest_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()

    return render_template(
        "admin/admin_dashboard.html",
        total_messages=total_messages,
        unread_messages=unread_messages,
        latest_messages=latest_messages
    )

# ==========================================================
# MESSAGES
# ==========================================================

@auth.route("/messages")
def messages():
    if not admin_required():
        flash("You are not authorized to access messages.", "danger")
        return redirect(url_for("auth.login"))

    messages = Message.query.order_by(Message.created_at.desc()).all()
    total = Message.query.count()
    unread = Message.query.filter_by(is_read=False).count()
    read = Message.query.filter_by(is_read=True).count()

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
    if not admin_required():
        flash("You are not authorized to view this message.", "danger")
        return redirect(url_for("auth.login"))

    message = Message.query.get_or_404(id)
    message.is_read = True
    db.session.commit()

    return render_template("admin/view_message.html", message=message)


# ==========================================================
# DELETE MESSAGE
# ==========================================================

@auth.route("/messages/delete/<int:id>")
def delete_message(id):
    if not admin_required():
        flash("You are not authorized to delete messages.", "danger")
        return redirect(url_for("auth.login"))

    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()

    flash("Message deleted successfully.", "success")
    return redirect(url_for("auth.messages"))


# ==========================================================
# SETTINGS
# ==========================================================

@auth.route("/settings", methods=["GET", "POST"])
def settings():
    if not admin_required():
        flash("You are not authorized to access settings.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not fullname or not email:
            flash("Full name and email are required.", "danger")
            return redirect(url_for("auth.settings"))

        existing_user = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_user:
            flash("This email is already being used.", "danger")
            return redirect(url_for("auth.settings"))

        user.fullname = fullname
        user.email = email
        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.settings"))

    return render_template("admin/settings.html", user=user)


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@auth.route("/settings/password", methods=["POST"])
def change_password():
    if not admin_required():
        flash("You are not authorized to change password.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(session["user_id"])

    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "danger")
        return redirect(url_for("auth.settings"))

    if not check_password_hash(user.password, current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("auth.settings"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("auth.settings"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("auth.settings"))

    if check_password_hash(user.password, new_password):
        flash("New password must be different from your current password.", "danger")
        return redirect(url_for("auth.settings"))

    user.password = generate_password_hash(new_password)
    db.session.commit()

    log_activity(user.id, "Password changed", f"User: {user.email}")

    flash("Password changed successfully.", "success")
    return redirect(url_for("auth.settings"))


# ==========================================================
# LOGOUT
# ==========================================================

@auth.route("/logout")
def logout():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            log_activity(user.id, "User logged out", f"Email: {user.email}")

    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


# ==========================================================
# SUPER ADMIN - DASHBOARD
# ==========================================================

@auth.route("/super-admin/dashboard")
def super_admin_dashboard():
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    total_users = User.query.count()
    total_admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).count()
    total_customers = User.query.filter_by(role='customer').count()
    total_active = User.query.filter_by(is_active=True).count() if hasattr(User, 'is_active') else total_users
    
    recent_users = User.query.order_by(User.id.desc()).limit(10).all()
    
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
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).order_by(User.id.desc()).all()
    
    return render_template("admin/super_admin/admins.html", admins=admins)

#ADD ADMIN
@auth.route("/super-admin/admins/add", methods=["GET", "POST"])
def add_admin():
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "admin").strip()
        
        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash(f"Email '{email}' is already registered.", "danger")
            return redirect(url_for("auth.add_admin"))
        
        # GENERATE SECURE ACCOUNT ID AUTOMATICALLY
        new_account_id = generate_account_id(role)
        
        new_admin = User(
            account_id=new_account_id,  # ADDED HERE
            fullname=fullname,
            username=fullname.replace(" ", "_").lower(),
            email=email,
            password=generate_password_hash(password),
            role=role,
            email_verified=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        log_activity(session['user_id'], f"Added new {role}: {email}", f"Name: {fullname} | ID: {new_account_id}")
        
        flash(f"✅ {role.title()} '{fullname}' added successfully with ID: {new_account_id}!", "success")
        return redirect(url_for("auth.manage_admins"))
    
    return render_template("admin/super_admin/add_admin.html")


@auth.route("/super-admin/admins/edit/<int:user_id>", methods=["GET", "POST"])
def edit_admin(user_id):
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admin = User.query.get_or_404(user_id)
    
    if admin.id == session['user_id']:
        flash("You cannot edit your own account here. Use Settings.", "warning")
        return redirect(url_for("auth.manage_admins"))
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "admin").strip()
        is_active = request.form.get("is_active") == "on"
        
        if not fullname or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("auth.edit_admin", user_id=user_id))
        
        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            flash(f"Email '{email}' is already taken.", "danger")
            return redirect(url_for("auth.edit_admin", user_id=user_id))
        
        admin.fullname = fullname
        admin.username = fullname.replace(" ", "_").lower()
        admin.email = email
        admin.role = role
        if hasattr(admin, 'is_active'):
            admin.is_active = is_active
        
        db.session.commit()
        
        log_activity(session['user_id'], f"Updated admin: {email}", f"Role: {role}")
        
        flash(f"✅ Admin '{fullname}' updated successfully!", "success")
        return redirect(url_for("auth.manage_admins"))
    
    return render_template("admin/super_admin/edit_admin.html", admin=admin)


@auth.route("/super-admin/admins/delete/<int:user_id>", methods=["POST"])
def delete_admin(user_id):
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    admin = User.query.get_or_404(user_id)
    
    if admin.id == session['user_id']:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("auth.manage_admins"))
    
    if admin.role == 'super_admin':
        super_admins = User.query.filter_by(role='super_admin').count()
        if super_admins <= 1:
            flash("Cannot delete the last Super Admin.", "danger")
            return redirect(url_for("auth.manage_admins"))
    
    log_activity(session['user_id'], f"Deleted admin: {admin.email}", f"Name: {admin.fullname}")
    
    db.session.delete(admin)
    db.session.commit()
    
    flash(f"✅ Admin '{admin.fullname}' deleted successfully!", "success")
    return redirect(url_for("auth.manage_admins"))


# ==========================================================
# SUPER ADMIN - MANAGE ALL USERS
# ==========================================================

@auth.route("/super-admin/users")
def manage_users():
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    users = User.query.order_by(User.id.desc()).all()
    
    return render_template("admin/super_admin/users.html", users=users)


@auth.route("/super-admin/users/toggle/<int:user_id>", methods=["POST"])
def toggle_user_status(user_id):
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == session['user_id']:
        flash("You cannot change your own status.", "danger")
        return redirect(url_for("auth.manage_users"))
    
    if hasattr(user, 'is_active'):
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        log_activity(session['user_id'], f"{status.title()} user: {user.email}", f"User: {user.fullname}")
        
        flash(f"✅ User '{user.fullname}' {status}!", "success")
    else:
        flash("User status toggle not available.", "warning")
    
    return redirect(url_for("auth.manage_users"))


@auth.route("/super-admin/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not super_admin_required():
        flash("Super Admin access required.", "danger")
        return redirect(url_for("auth.dashboard"))
    
    user = User.query.get_or_404(user_id)
    
    if user.role in ['admin', 'super_admin']:
        flash("Use the admin management page to delete administrators.", "danger")
        return redirect(url_for("auth.manage_users"))
    
    log_activity(session['user_id'], f"Deleted user: {user.email}", f"Name: {user.fullname}")
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"✅ User '{user.fullname}' deleted successfully!", "success")
    return redirect(url_for("auth.manage_users"))
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

from extensions import db
from models import User, Message


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

    # User hayupo tena kwenye database
    if not user:
        session.clear()
        return False

    # Super Admin pekee
    return user.role == "super_admin"


# ==========================================================
# LOGIN
# ==========================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    # ------------------------------------------
    # ALREADY LOGGED IN
    # ------------------------------------------

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

    # ------------------------------------------
    # LOGIN FORM
    # ------------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        ).strip()

        # --------------------------------------
        # VALIDATION
        # --------------------------------------

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        # --------------------------------------
        # FIND USER
        # --------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()

        # --------------------------------------
        # CHECK USER + PASSWORD
        # --------------------------------------

        if user and check_password_hash(
            user.password,
            password
        ):

            # ----------------------------------
            # CREATE SESSION
            # ----------------------------------

            session.clear()

            session["user_id"] = user.id
            session["user_role"] = user.role

            # ----------------------------------
            # SUCCESS MESSAGE
            # ----------------------------------

            flash(
                "Welcome back!",
                "success"
            )

            # ----------------------------------
            # ROLE REDIRECTION
            # ----------------------------------

            if user.role == "super_admin":

                return redirect(
                    url_for("auth.dashboard")
                )

            elif user.role == "admin":

                return redirect(
                    url_for("auth.dashboard")
                )

            elif user.role == "customer":

                return redirect(
                    url_for("public.home")
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

        # --------------------------------------
        # INVALID LOGIN
        # --------------------------------------

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@auth.route("/dashboard")
def dashboard():

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access the admin dashboard.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # MESSAGE STATISTICS
    # ------------------------------------------

    total_messages = Message.query.count()

    unread_messages = Message.query.filter_by(
        is_read=False
    ).count()

    read_messages = Message.query.filter_by(
        is_read=True
    ).count()

    # ------------------------------------------
    # LATEST MESSAGES
    # ------------------------------------------

    latest_messages = Message.query.order_by(
        Message.created_at.desc()
    ).limit(5).all()

    # ------------------------------------------
    # RENDER DASHBOARD
    # ------------------------------------------

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

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access messages.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # GET ALL MESSAGES
    # ------------------------------------------

    messages = Message.query.order_by(
        Message.created_at.desc()
    ).all()

    # ------------------------------------------
    # STATISTICS
    # ------------------------------------------

    total = Message.query.count()

    unread = Message.query.filter_by(
        is_read=False
    ).count()

    read = Message.query.filter_by(
        is_read=True
    ).count()

    # ------------------------------------------
    # RENDER
    # ------------------------------------------

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

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to view this message.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # FIND MESSAGE
    # ------------------------------------------

    message = Message.query.get_or_404(id)

    # ------------------------------------------
    # MARK AS READ
    # ------------------------------------------

    message.is_read = True

    db.session.commit()

    # ------------------------------------------
    # RENDER MESSAGE
    # ------------------------------------------

    return render_template(
        "admin/view_message.html",
        message=message
    )


# ==========================================================
# DELETE MESSAGE
# ==========================================================

@auth.route("/messages/delete/<int:id>")
def delete_message(id):

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to delete messages.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # FIND MESSAGE
    # ------------------------------------------

    message = Message.query.get_or_404(id)

    # ------------------------------------------
    # DELETE
    # ------------------------------------------

    db.session.delete(message)

    db.session.commit()

    # ------------------------------------------
    # SUCCESS MESSAGE
    # ------------------------------------------

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

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to access settings.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # GET CURRENT USER
    # ------------------------------------------

    user = User.query.get_or_404(
        session["user_id"]
    )

    # ------------------------------------------
    # UPDATE PROFILE
    # ------------------------------------------

    if request.method == "POST":

        fullname = request.form.get(
            "fullname",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        # --------------------------------------
        # VALIDATION
        # --------------------------------------

        if not fullname or not email:

            flash(
                "Full name and email are required.",
                "danger"
            )

            return redirect(
                url_for("auth.settings")
            )

        # --------------------------------------
        # CHECK DUPLICATE EMAIL
        # --------------------------------------

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

        # --------------------------------------
        # UPDATE USER
        # --------------------------------------

        user.fullname = fullname
        user.email = email

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------
    # DISPLAY SETTINGS
    # ------------------------------------------

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

    # ------------------------------------------
    # CHECK ADMIN ACCESS
    # ------------------------------------------

    if not admin_required():

        flash(
            "You are not authorized to change password.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ------------------------------------------
    # GET USER
    # ------------------------------------------

    user = User.query.get_or_404(
        session["user_id"]
    )

    # ------------------------------------------
    # GET FORM DATA
    # ------------------------------------------

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

    # ------------------------------------------
    # VALIDATION
    # ------------------------------------------

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

    # ------------------------------------------
    # CHECK CURRENT PASSWORD
    # ------------------------------------------

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

    # ------------------------------------------
    # PASSWORD LENGTH
    # ------------------------------------------

    if len(new_password) < 6:

        flash(
            "New password must be at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------
    # CONFIRM PASSWORD
    # ------------------------------------------

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("auth.settings")
        )

    # ------------------------------------------
    # PREVENT SAME PASSWORD
    # ------------------------------------------

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

    # ------------------------------------------
    # HASH NEW PASSWORD
    # ------------------------------------------

    user.password = generate_password_hash(
        new_password
    )

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

    db.session.commit()

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

    # ------------------------------------------
    # CLEAR SESSION
    # ------------------------------------------

    session.clear()

    # ------------------------------------------
    # MESSAGE
    # ------------------------------------------

    flash(
        "Logged out successfully.",
        "success"
    )

    # ------------------------------------------
    # REDIRECT
    # ------------------------------------------

    return redirect(
        url_for("auth.login")
    )
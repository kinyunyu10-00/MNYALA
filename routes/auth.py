from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User, Message


auth = Blueprint("auth", __name__)


# ======================================
# LOGIN
# ======================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    # TEMPORARY LOGIN FOR TESTING
    session["user_id"] = 1

    return redirect(url_for("auth.dashboard"))

    # REAL LOGIN - TUTAITUMIA BAADAYE
    """
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            flash("Welcome back!", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")
    """


# ======================================
# DASHBOARD
# ======================================

@auth.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    total_messages = Message.query.count()

    unread_messages = Message.query.filter_by(
        is_read=False
    ).count()

    latest_messages = Message.query.order_by(
        Message.created_at.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_messages=total_messages,
        unread_messages=unread_messages,
        latest_messages=latest_messages
    )


# ======================================
# MESSAGES
# ======================================

@auth.route("/messages")
def messages():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    messages = Message.query.order_by(
        Message.created_at.desc()
    ).all()

    total = Message.query.count()

    unread = Message.query.filter_by(
        is_read=False
    ).count()

    read = Message.query.filter_by(
        is_read=True
    ).count()

    return render_template(
        "admin/messages.html",
        messages=messages,
        total=total,
        unread=unread,
        read=read
    )


# ======================================
# SETTINGS
# ======================================

@auth.route("/settings", methods=["GET", "POST"])
def settings():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(
        session["user_id"]
    )

    # UPDATE PROFILE
    if request.method == "POST":

        fullname = request.form.get(
            "fullname",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        if not fullname or not email:

            flash(
                "Full name and email are required.",
                "danger"
            )

            return redirect(
                url_for("auth.settings")
            )

        # CHECK EMAIL
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

        # UPDATE DATABASE
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

    return render_template(
        "admin/settings.html",
        user=user
    )


# ======================================
# VIEW MESSAGE
# ======================================

@auth.route("/messages/<int:id>")
def view_message(id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    message = Message.query.get_or_404(id)

    # Mark as read
    message.is_read = True

    db.session.commit()

    return render_template(
        "admin/view_message.html",
        message=message
    )

# ======================================
# CHANGE PASSWORD
# ======================================

@auth.route("/settings/password", methods=["POST"])
def change_password():

    # Hakikisha admin ameingia
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(session["user_id"])

    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # -------------------------------
    # VALIDATION
    # -------------------------------

    if not current_password or not new_password or not confirm_password:

        flash(
            "All password fields are required.",
            "danger"
        )

        return redirect(url_for("auth.settings"))

    # -------------------------------
    # CHECK CURRENT PASSWORD
    # -------------------------------

    if not check_password_hash(user.password, current_password):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(url_for("auth.settings"))

    # -------------------------------
    # CHECK NEW PASSWORD
    # -------------------------------

    if len(new_password) < 6:

        flash(
            "New password must be at least 6 characters.",
            "danger"
        )

        return redirect(url_for("auth.settings"))

    # -------------------------------
    # CONFIRM PASSWORD
    # -------------------------------

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(url_for("auth.settings"))

    # -------------------------------
    # PREVENT SAME PASSWORD
    # -------------------------------

    if check_password_hash(user.password, new_password):

        flash(
            "New password must be different from your current password.",
            "danger"
        )

        return redirect(url_for("auth.settings"))

    # -------------------------------
    # HASH NEW PASSWORD
    # -------------------------------

    user.password = generate_password_hash(new_password)

    # -------------------------------
    # SAVE TO DATABASE
    # -------------------------------

    db.session.commit()

    flash(
        "Password changed successfully.",
        "success"
    )

    return redirect(url_for("auth.settings"))
# ======================================
# DELETE MESSAGE
# ======================================

@auth.route("/messages/delete/<int:id>")
def delete_message(id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    message = Message.query.get_or_404(id)

    db.session.delete(message)

    db.session.commit()

    flash(
        "Message deleted successfully.",
        "success"
    )

    return redirect(
        url_for("auth.messages")
    )


# ======================================
# LOGOUT
# ======================================

@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import check_password_hash

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
from flask import Blueprint, render_template, session, redirect, url_for

admin = Blueprint("admin", __name__)


@admin.route("/")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("admin/dashboard.html")
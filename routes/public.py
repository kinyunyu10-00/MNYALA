from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db

from models import Message


public = Blueprint("public", __name__)


@public.route("/")
def home():
    return render_template("index.html")


@public.route("/about")
def about():
    return render_template("about.html")


@public.route("/products")
def products():
    return render_template("products.html")


@public.route("/gallery")
def gallery():
    return render_template("gallery.html")


@public.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        new_message = Message(

            fullname=request.form.get("fullname"),

            email=request.form.get("email"),

            phone=request.form.get("phone"),

            subject=request.form.get("subject"),

            message=request.form.get("message")

        )

        db.session.add(new_message)

        db.session.commit()

        flash("Ujumbe wako umetumwa kikamilifu.", "success")

        return redirect(url_for("public.contact"))

    return render_template("contact.html")
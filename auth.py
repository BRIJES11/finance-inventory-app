from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_login import login_user, logout_user
from models import User
from db import db
import bcrypt

auth = Blueprint("auth", __name__ , url_prefix="/auth")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = db.users.find_one({"email": email})
        if existing_user:
            return redirect(url_for("auth.register")) 
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user_data = db.users.find_one({"email": email})
        
        if user_data and bcrypt.checkpw(password.encode("utf-8"), user_data["password"]):
            user = User(
                id=str(user_data["_id"]),
                name=user_data["name"],
                email=user_data["email"],
                password=user_data["password"]
            )
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        return redirect(url_for("auth.login"))
    return render_template("auth/login.html")
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))




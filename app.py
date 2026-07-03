from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_login import LoginManager, login_required, current_user
from auth import auth
from db import client, db
from bson import ObjectId
from models import User
from expense import expense
from inventory import inventory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

try:
    client.admin.command("ping")
    print("MongoDB connection successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

#flask -login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(
            id=str(user_data["_id"]),
            name=user_data["name"],
            email=user_data["email"],
            password=user_data["password"]
        )
    return None

app.register_blueprint(auth)
app.register_blueprint(expense)
app.register_blueprint(inventory)

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("expense.dashboard"))
    return render_template("home.html")



if __name__ == '__main__':
    app.run(debug=True)
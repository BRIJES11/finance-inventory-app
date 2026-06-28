from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from db import db
from bson import ObjectId

inventory = Blueprint("inventory", __name__, url_prefix="/inventory")

@inventory.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form["name"]
        sku = request.form["sku"]
        category = request.form["category"]
        buying_price = float(request.form["buying_price"])
        selling_price = float(request.form["selling_price"])
        quantity = int(request.form["quantity"])
        low_stock_threshold = int(request.form["low_stock_threshold"])
        supplier = request.form["supplier"]

        db.products.insert_one({
            "user_id": current_user.id,
            "name": name,
            "sku": sku,
            "category": category,
            "buying_price": buying_price,
            "selling_price": selling_price,
            "quantity": quantity,
            "low_stock_threshold": low_stock_threshold,
            "supplier": supplier
        })
        return redirect(url_for("inventory.products"))
    return render_template("inventory/add_product.html")

@inventory.route("/products", methods=["GET"])
@login_required
def products():
    products = list(db.products.find({"user_id": current_user.id}))
    return render_template("inventory/products.html", products=products)
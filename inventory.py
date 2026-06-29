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
    search = request.args.get("search")
    category = request.args.get("category")
    query = {"user_id": current_user.id}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"sku": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options":"i"}

    products = list(db.products.find(query))
    return render_template("inventory/products.html", products=products)

@inventory.route("/edit/<product_id>", methods=["GET", "POST"])
@login_required
def edit(product_id):
    product = db.products.find_one({"_id": ObjectId(product_id),})
    if request.method == "POST":
        name = request.form["name"]
        sku = request.form["sku"]
        category = request.form["category"]
        buying_price = float(request.form["buying_price"])
        selling_price = float(request.form["selling_price"])
        quantity = int(request.form["quantity"])
        low_stock_threshold = int(request.form["low_stock_threshold"])
        supplier = request.form["supplier"]
        
        db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {
                "name": name,
                "sku": sku,
                "category": category,
                "buying_price": buying_price,
                "selling_price": selling_price,
                "quantity": quantity,
                "low_stock_threshold": low_stock_threshold,
                "supplier": supplier,
            }}
        )
        return redirect(url_for("inventory.products"))
    return render_template("inventory/edit_product.html", product=product)

@inventory.route("/delete/<product_id>")
@login_required
def delete(product_id):
    db.products.delete_one({"_id":ObjectId(product_id)})
    return redirect(url_for("inventory.products"))


from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from auth import login
from db import db
from bson import ObjectId
from datetime import date

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
    product = db.products.find_one({"_id": ObjectId(product_id)})
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

@inventory.route("/restock/<product_id>", methods=["GET", "POST"])
@login_required
def restock(product_id):
    product = db.products.find_one({"_id":ObjectId(product_id)})
    if request.method == "POST":
        quantity = int(request.form["quantity"])
        note = request.form["note"]
        
        db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": quantity}}
        )
        db.history.insert_one({
            "product_id": product_id,
            "user_id": current_user.id,
            "action": "restock",
            "quantity": quantity,
            "date": str(date.today()),
            "note": note
        })
        return redirect(url_for("inventory.products"))
    return render_template("inventory/restock.html", product=product)

@inventory.route("/sell/<product_id>", methods=["GET", "POST"])
@login_required
def sell(product_id):
    product = db.products.find_one({"_id":ObjectId(product_id)})
    if request.method == "POST":
        quantity = int(request.form["quantity"])
        note = request.form["note"]
        
        db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": -quantity}}
        )
        db.history.insert_one({
            "product_id": product_id,
            "user_id": current_user.id,
            "action": "sell",
            "quantity": quantity,
            "date": str(date.today()),
            "note": note
        })
        return redirect(url_for("inventory.products"))
    return render_template("inventory/sell.html", product=product)

@inventory.route("/history/<product_id>", methods=["GET"])
@login_required
def history(product_id):
    product = db.products.find_one({"_id": ObjectId(product_id)})
    history = list(db.history.find({"product_id": product_id}))
    return render_template("inventory/history.html", product=product, history=history)

@inventory.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    products = list(db.products.find({"user_id": current_user.id}))

    total_products = len(products)
    total_stock_value = sum(int(p["buying_price"]) * int(p["quantity"]) for p in products)
    low_stock_items = [p for p in products if int(p["quantity"]) <= int(p["low_stock_threshold"])]
    
    category_stock = {}
    for p in products:
        category = p["category"]
        category_stock[category] = category_stock.get(category, 0) + p["quantity"]
        
        
    return render_template("inventory/dashboard.html",
        total_products = total_products,
        total_stock_value = total_stock_value,
        low_stock_items = low_stock_items,
        category_stock=category_stock                      
    )
    








from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required, current_user
from db import db
from bson import ObjectId

expense = Blueprint("expense", __name__, url_prefix="/expense")

@expense.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        account = request.form["account"]
        type = request.form["type"]
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        note = request.form["note"]

        db.transactions.insert_one({
            "user_id": current_user.id,
            "account":account,
            "type":type,
            "category":category,
            "amount":float(amount),
            "date":date,
            "note":note
        })
        return redirect(url_for("expense.transactions"))
    return render_template("expense/add_transaction.html")

@expense.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    month = request.args.get("month")
    category = request.args.get("category")
    query = {"user_id": current_user.id}
    if month:
        query["date"] = {"$regex": f"^{month}"}
    if category:
        query["category"] = category
    transactions = list(db.transactions.find({"user_id": current_user.id}))
    return render_template("expense/transactions.html", transactions=transactions)

@expense.route("/edit/<transaction_id>", methods=["GET", "POST"])
@login_required
def edit(transaction_id):
    transaction = db.transactions.find_one({"_id": ObjectId(transaction_id), })
    if request.method == "POST":
        account = request.form["account"]
        type = request.form["type"]
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        note = request.form["note"]
        db.transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            {"$set": {
                "account": account,
                "type": type,
                "category": category,
                "amount": float(amount),
                "date": date,
                "note" : note,
           }}
        )
        return redirect(url_for("expense.transactions"))
    return render_template("expense/edit_transaction.html", transaction=transaction)

@expense.route("/delete/<transaction_id>")
@login_required
def delete(transaction_id):
    db.transactions.delete_one({"_id": ObjectId(transaction_id)})
    return redirect(url_for("expense.transactions"))




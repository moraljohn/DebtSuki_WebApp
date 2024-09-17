from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from helpers import login_required, php

from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

app.jinja_env.filters["usd"] = php

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///debt.db")

PAYMENT_METHOD = ["CASH", "GCASH", "PAYMAYA", "CREDIT/DEBIT CARD"]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homepage', methods=["GET", "POST"])
@login_required
def homepage():
    if request.method == "POST":
        user_id = session["user_id"]
    else:
        total = 0
        user_id = session["user_id"]
        user_db = db.execute("SELECT name FROM users WHERE id = ?", user_id)
        user = user_db[0]["name"]
        table_db = db.execute("SELECT table_name, SUM(debtors) as debtors, SUM(paid) as paid, SUM(unpaid) as unpaid, date, SUM(total_amount) as total FROM tables WHERE user_id = ? GROUP BY table_name", user_id)
        check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ?", user_id)
        if table_db:
            total_db = db.execute("SELECT SUM(total_amount) as total FROM tables WHERE user_id = ?", user_id)
            total = total_db[0]["total"]

        return render_template("homepage.html", table=check_table_db, user_tables=table_db, user=user, payments=PAYMENT_METHOD, total=total, php=php)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        user_id = session["user_id"]
        table_name = request.form.get("table_name")
        name = request.form.getlist("name")
        gross = request.form.getlist("gross")
        interest = request.form.getlist("interest")
        payment = request.form.getlist("payment")
        due_date = request.form.getlist("due-date")
        calendar_date = datetime.now()
        action = "TABLE CREATED"


        table_name_total_db = db.execute("SELECT SUM(total_amount) as total_amount FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        summary_total = 0
        if table_name_total_db[0]["total_amount"]:
            summary_total = float(table_name_total_db[0]["total_amount"])


        for i in range(len(name)):
            if not name[i] or not gross[i] or not interest[i] or not payment[i] or payment[i] not in PAYMENT_METHOD:
                flash("All fields are required!")
                return redirect("/homepage")

            debtors = 1
            unpaid = 1
            paid = 0
            interest_percentage_rate = float(interest[i]) / 100
            interest_rate = float(gross[i]) * interest_percentage_rate
            total_amount = float(gross[i]) + interest_rate
            db.execute("INSERT INTO table_summary (user_id, table_name, name, gross, interest, interest_rate, total_amount, payment, date, due_date, total_gross, total_interest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name[i], gross[i], interest[i], interest_rate, total_amount, payment[i], calendar_date, due_date[i], gross[i], interest_rate)
            summary_total += total_amount
            db.execute("INSERT INTO tables (user_id, table_name, debtors, debtor_name, paid, unpaid, date, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, debtors, name[i], paid, unpaid, calendar_date, total_amount)
            debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name[i])
            debtor_id = debtor_id_db[0]["id"]
            db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name[i], gross[i], interest[i], payment[i], calendar_date, due_date[i], total_amount, action, debtor_id)

        flash("Created new table successfully")
        return redirect("/homepage")



@app.route('/check_table_name/<table_name>')
def check_table_name(table_name):
    if table_name:
        user_id = session["user_id"]
        result = db.execute("SELECT table_name FROM tables WHERE user_id = ? AND table_name = ?", user_id, table_name)
        if result:
            return jsonify({"exists": True})
        return jsonify({"exists": False})



@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username!")
            return redirect("/")
        if not password:
            flash("Must provide password!")
            return redirect("/")

        user_credential = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not user_credential or not check_password_hash(user_credential[0]["hash"], password):
            flash("Invalid username and/or password")
            return redirect("/")

        session["user_id"] = user_credential[0]["id"]

        return redirect("/homepage")

    else:
        return render_template("login.html")



@app.route("/summary", methods=["GET", "POST"])
@login_required
def summary():
    if request.method == "POST":
        user_id = session["user_id"]
        table_name = request.form.get("table-name")

        if not table_name:
            flash("Must provide what table!")
            return redirect("/")

        table_data_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        table_total_db = db.execute("SELECT SUM(total_amount) as total FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)
        total_gross_db = db.execute("SELECT SUM(total_gross) as total_gross FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        total_interest_db = db.execute("SELECT SUM(total_interest) as total_interest FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        total_amount_paid_db = db.execute("SELECT SUM(amount_paid) as amount_paid FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        if not total_amount_paid_db[0]["amount_paid"]:
            total_amount_paid = 0
        else:
            total_amount_paid = total_amount_paid_db[0]["amount_paid"]

        if table_total_db[0]["total"]:
            total = table_total_db[0]["total"]
        else:
            total = 0

        total_gross = total_gross_db[0]["total_gross"]
        total_interest = total_interest_db[0]["total_interest"]


        return render_template("summary.html", payments=PAYMENT_METHOD, table_data=table_data_db, total=total, tables=check_table_db, total_interest=total_interest, total_gross=total_gross, paid=total_amount_paid, selected_table=table_name, php=php, int=int)

    else:
        user_id = session["user_id"]
        check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)

        return render_template("summary.html", tables=check_table_db, payments=PAYMENT_METHOD)


@app.route('/summaryHome/<table_name>')
@login_required
def summaryHome(table_name):
    user_id = session["user_id"]

    table_data_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    table_total_db = db.execute("SELECT SUM(total_amount) as total FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)
    total_gross_db = db.execute("SELECT SUM(total_gross) as total_gross FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    total_interest_db = db.execute("SELECT SUM(total_interest) as total_interest FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    total_amount_paid_db = db.execute("SELECT SUM(amount_paid) as amount_paid FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    if not total_amount_paid_db[0]["amount_paid"]:
        total_amount_paid = 0
    else:
        total_amount_paid = total_amount_paid_db[0]["amount_paid"]

    if table_total_db[0]["total"]:
        total = table_total_db[0]["total"]
    else:
        total = 0

    total_gross = total_gross_db[0]["total_gross"]
    total_interest = total_interest_db[0]["total_interest"]

    return render_template("summaryHome.html", payments=PAYMENT_METHOD, table_data=table_data_db, total=total, tables=check_table_db, total_interest=total_interest, total_gross=total_gross, paid=total_amount_paid, selected_table=table_name, php=php, int=int)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        hashed_password = generate_password_hash(password)
        if not name:
            flash("Must provide name!")
            return redirect("/")
        if not username:
            flash("Must provide username to register!")
            return redirect("/")
        if not password:
            flash("Must provide password to register!")
            return redirect("/")
        if not confirmation:
            flash("Must provide confirmation password to register!")
            return redirect("/")

        user_credential = db.execute("SELECT username FROM users WHERE username = ?", username)

        if user_credential:
            flash("Username already exists!")
            return redirect("/")

        if not check_password_hash(hashed_password, confirmation):
            flash("Passwords do not match!")
            return redirect("/")

        db.execute("INSERT INTO users (name, username, hash) VALUES (?, ?, ?)", name, username, hashed_password)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        flash("Welcome to SukiDebt!")
        return redirect("/homepage")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/edit", methods=["POST"])
@login_required
def edit():
    if request.method == "POST":
        user_id = session["user_id"]
        table_id = request.form.get("id")
        table_name = request.form.get("table-name")
        calendar_date = datetime.now()
        name = request.form.get("edit-name")
        gross = request.form.get("edit-gross")
        interest = request.form.get("edit-interest")
        payment = request.form.get("edit-payment")
        due_date = request.form.get("edit-due-date")
        total_gross = request.form.get("edit-total-gross")
        total_interest = request.form.get("edit-total-interest")
        action = "EDIT"

        gross_and_interest = False
        new_name = False
        new_payment = False
        new_due_date = False
        new_gross = False
        new_interest = False

        if name and gross and interest and payment:
            current_data_db = db.execute("SELECT * FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
            current_name = current_data_db[0]["name"]
            current_gross = current_data_db[0]["gross"]
            current_interest = current_data_db[0]["interest"]
            current_payment = current_data_db[0]["payment"]
            current_due_date = current_data_db[0]["due_date"]
            current_total_gross = current_data_db[0]["total_gross"]
            current_total_interest = current_data_db[0]["total_interest"]

            remaining_bal_db = db.execute("SELECT total_amount FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, current_name)
            total_amount = remaining_bal_db[0]["total_amount"]

            if current_interest == '':
                current_interest = 0


            if name != current_name or float(gross) != float(current_gross) or float(interest) != float(current_interest) or payment != current_payment or due_date != current_due_date:
                if payment in PAYMENT_METHOD:

                    if name != current_name:
                        new_name = True
                        db.execute("UPDATE table_summary SET name = ? WHERE id = ? AND user_id = ? AND table_name = ?", name, table_id, user_id, table_name)
                        db.execute("UPDATE tables SET debtor_name = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", name, current_name, user_id, table_name)
                    if float(gross) != float(current_gross) and float(interest) != float(current_interest):
                        gross_and_interest = True
                        if float(total_gross) != float(current_total_gross) and float(total_interest) != float(current_total_interest):
                            name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                            makeSureName = name_db[0]["name"]

                            tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                            debtor_number = tables_debtor_db[0]["debtors"]
                            debtor_paid = tables_debtor_db[0]["paid"]
                            debtor_unpaid = tables_debtor_db[0]["unpaid"]

                            if int(debtor_number) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                                debtor_count = 1
                                paid_count = 0
                                unpaid_count = 1
                                update_amount_paid = 0
                                db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtor_count, paid_count, unpaid_count, user_id, table_name, makeSureName)
                                db.execute("UPDATE table_summary SET amount_paid = ? WHERE id = ? AND user_id = ? AND table_name = ?", update_amount_paid, table_id, user_id, table_name)

                            db.execute("UPDATE table_summary SET gross = ?, interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", gross, interest, table_id, user_id, table_name)
                            interest_percentage_rate = float(interest) / 100
                            interest_rate = float(gross) * interest_percentage_rate
                            total_amount = float(gross) + interest_rate
                            db.execute("UPDATE table_summary SET interest_rate = ?, total_amount = ?, total_gross = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", interest_rate, total_amount, total_gross, total_interest, table_id, user_id, table_name)
                            db.execute("UPDATE tables SET total_amount = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", total_amount, makeSureName, user_id, table_name)
                        else:
                            flash("You are required to also change the Total Gross and Total Interest column if you either edit existing gross or interest recorded!")
                            return redirect("/homepage")
                    if not gross_and_interest:
                        if float(gross) != float(current_gross):
                            if float(total_gross) != float(current_total_gross) and float(total_interest) != float(current_total_interest):
                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]

                                tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                                debtor_number = tables_debtor_db[0]["debtors"]
                                debtor_paid = tables_debtor_db[0]["paid"]
                                debtor_unpaid = tables_debtor_db[0]["unpaid"]

                                if int(debtor_number) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                                    debtor_count = 1
                                    paid_count = 0
                                    unpaid_count = 1
                                    update_amount_paid = 0
                                    db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtor_count, paid_count, unpaid_count, user_id, table_name, makeSureName)
                                    db.execute("UPDATE table_summary SET amount_paid = ? WHERE id = ? AND user_id = ? AND table_name = ?", update_amount_paid, table_id, user_id, table_name)

                                new_gross = True
                                db.execute("UPDATE table_summary SET gross = ? WHERE id = ? AND user_id = ? AND table_name = ?", gross, table_id, user_id, table_name)
                                interest_percentage_rate = float(current_interest) / 100
                                interest_rate = float(gross) * interest_percentage_rate
                                total_amount = float(gross) + interest_rate
                                db.execute("UPDATE table_summary SET total_amount = ?, interest_rate = ?, total_gross = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", total_amount, interest_rate, total_gross, total_interest, table_id, user_id, table_name)
                                db.execute("UPDATE tables SET total_amount = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", total_amount, makeSureName, user_id, table_name)
                            else:
                                flash("You are required to also change the Total Gross and Total interest column if you edit the existing Gross recorded!")
                                return redirect("/homepage")
                        if float(interest) != float(current_interest):
                            if float(total_gross) != float(current_total_gross) and float(total_interest) != float(current_total_interest):
                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]

                                tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                                debtor_count = tables_debtor_db[0]["debtors"]
                                debtor_paid = tables_debtor_db[0]["paid"]
                                debtor_unpaid = tables_debtor_db[0]["unpaid"]

                                if int(debtor_count) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                                    flash("Debtor is already paid, can't edit interest!")
                                    return redirect("/homepage")

                                new_interest = True
                                db.execute("UPDATE table_summary SET interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", interest, table_id, user_id, table_name)
                                interest_percentage_rate = float(interest) / 100
                                interest_rate = float(current_gross) * interest_percentage_rate
                                total_amount = float(current_gross) + interest_rate
                                db.execute("UPDATE table_summary SET interest_rate = ?, total_amount = ?, total_gross = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", interest_rate, total_amount, total_gross, total_interest, table_id, user_id, table_name)
                                db.execute("UPDATE tables SET total_amount = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", total_amount, makeSureName, user_id, table_name)
                            else:
                                flash("You are required to also change the Total Gross and Total Interest column if you edit the existing Interest recorded!")
                                return redirect("/homepage")
                    if payment != current_payment:
                        name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                        makeSureName = name_db[0]["name"]

                        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                        debtor_count = tables_debtor_db[0]["debtors"]
                        debtor_paid = tables_debtor_db[0]["paid"]
                        debtor_unpaid = tables_debtor_db[0]["unpaid"]

                        if int(debtor_count) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                            flash("Debtor is already paid, can't edit payment!")
                            return redirect("/homepage")

                        new_payment = True
                        db.execute("UPDATE table_summary SET payment = ? WHERE id = ? AND user_id = ? AND table_name = ?", payment, table_id, user_id, table_name)

                    if due_date != current_due_date:
                        name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                        makeSureName = name_db[0]["name"]

                        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                        debtor_count = tables_debtor_db[0]["debtors"]
                        debtor_paid = tables_debtor_db[0]["paid"]
                        debtor_unpaid = tables_debtor_db[0]["unpaid"]

                        if int(debtor_count) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                            flash("Debtor is already paid, can't edit due date!")
                            return redirect("/homepage")

                        new_due_date = True
                        db.execute("UPDATE table_summary SET due_date = ? WHERE id = ? AND user_id = ? AND table_name = ?", due_date, table_id, user_id, table_name)


                    if new_name or gross_and_interest or new_gross or new_interest or new_payment or new_due_date:
                        if new_gross:
                            if float(gross == 0):
                                action = "PAID BY EDIT!"
                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]
                                debtors = 0
                                unpaid = 0
                                paid = 1
                                db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtors, paid, unpaid, user_id, table_name, makeSureName)
                                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                                debtor_id = debtor_id_db[0]["id"]
                                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)
                            else:
                                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                                debtor_id = debtor_id_db[0]["id"]
                                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)
                        else:
                            debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                            debtor_id = debtor_id_db[0]["id"]
                            db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)

                    flash(f"Table {table_name} edited successfully!")
                    return redirect("/summary")
                else:
                    flash("Invalid payment method!")
                    return redirect("/homepage")
            else:
                flash("No edits found!")
                check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)

                return render_template("summary.html", tables=check_table_db, payments=PAYMENT_METHOD)


        if name and gross and not interest and payment:
            current_data_db = db.execute("SELECT * FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
            current_name = current_data_db[0]["name"]
            current_gross = current_data_db[0]["gross"]
            current_interest = current_data_db[0]["interest"]
            current_payment = current_data_db[0]["payment"]
            current_due_date = current_data_db[0]["due_date"]
            current_total_gross = current_data_db[0]["total_gross"]
            current_total_interest = current_data_db[0]["total_interest"]

            remaining_bal_db = db.execute("SELECT remaining_bal FROM history WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, current_name)
            total_amount = remaining_bal_db[0]["remaining_bal"]

            if current_interest == '':
                current_interest = 0


            if name != current_name or float(gross) != float(current_gross) or payment != current_payment or due_date != current_due_date:
                if payment in PAYMENT_METHOD:

                    if name != current_name:
                        new_name = True
                        db.execute("UPDATE table_summary SET name = ? WHERE id = ? AND user_id = ? AND table_name = ?", name, table_id, user_id, table_name)
                        db.execute("UPDATE tables SET debtor_name = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", name, current_name, user_id, table_name)
                    if not gross_and_interest:
                        if float(gross) != float(current_gross):
                            if float(total_gross) != float(current_total_gross) and float(total_interest) != float(current_total_interest):
                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]

                                tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                                debtor_number = tables_debtor_db[0]["debtors"]
                                debtor_paid = tables_debtor_db[0]["paid"]
                                debtor_unpaid = tables_debtor_db[0]["unpaid"]

                                if int(debtor_number) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                                    debtor_count = 1
                                    paid_count = 0
                                    unpaid_count = 1
                                    update_amount_paid = 0
                                    db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtor_count, paid_count, unpaid_count, user_id, table_name, makeSureName)
                                    db.execute("UPDATE table_summary SET amount_paid = ? WHERE id = ? AND user_id = ? AND table_name = ?", update_amount_paid, table_id, user_id, table_name)

                                new_gross = True
                                db.execute("UPDATE table_summary SET gross = ? WHERE id = ? AND user_id = ? AND table_name = ?", gross, table_id, user_id, table_name)
                                interest_percentage_rate = float(current_interest) / 100
                                interest_rate = float(gross) * interest_percentage_rate
                                total_amount = float(gross) + interest_rate
                                db.execute("UPDATE table_summary SET total_amount = ?, interest_rate = ?, total_gross = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ?", total_amount, interest_rate, total_gross, total_interest, table_id, user_id, table_name)

                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]
                                db.execute("UPDATE tables SET total_amount = ? WHERE debtor_name = ? AND user_id = ? AND table_name = ?", total_amount, makeSureName, user_id, table_name)
                            else:
                                flash("You are required to also change the Total Gross and Total interest column if you edit the existing Gross recorded!")
                                return redirect("/homepage")
                    if payment != current_payment:
                        name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                        makeSureName = name_db[0]["name"]

                        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                        debtor_count = tables_debtor_db[0]["debtors"]
                        debtor_paid = tables_debtor_db[0]["paid"]
                        debtor_unpaid = tables_debtor_db[0]["unpaid"]

                        if int(debtor_count) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                            flash("Debtor is already paid, can't edit payment!")
                            return redirect("/homepage")

                        new_payment = True
                        db.execute("UPDATE table_summary SET payment = ? WHERE id = ? AND user_id = ? AND table_name = ?", payment, table_id, user_id, table_name)

                    if due_date != current_due_date:
                        name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                        makeSureName = name_db[0]["name"]

                        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, makeSureName)
                        debtor_count = tables_debtor_db[0]["debtors"]
                        debtor_paid = tables_debtor_db[0]["paid"]
                        debtor_unpaid = tables_debtor_db[0]["unpaid"]

                        if int(debtor_count) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
                            flash("Debtor is already paid, can't edit due date!")
                            return redirect("/homepage")

                        new_due_date = True
                        db.execute("UPDATE table_summary SET due_date = ? WHERE id = ? AND user_id = ? AND table_name = ?", due_date, table_id, user_id, table_name)


                    if new_name or new_gross or new_payment or new_due_date:
                        if new_gross:
                            if float(gross == 0):
                                action = "PAID BY EDIT!"
                                name_db = db.execute("SELECT name FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ?", table_id, user_id, table_name)
                                makeSureName = name_db[0]["name"]
                                debtors = 0
                                unpaid = 0
                                paid = 1
                                db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtors, paid, unpaid, user_id, table_name, makeSureName)
                                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                                debtor_id = debtor_id_db[0]["id"]
                                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)
                            else:
                                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                                debtor_id = debtor_id_db[0]["id"]
                                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)
                        else:
                            debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                            debtor_id = debtor_id_db[0]["id"]
                            db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, total_amount, action, debtor_id)

                    flash(f"Table {table_name} edited successfully!")
                    return redirect("/summary")
                else:
                    flash("Invalid payment method!")
                    return redirect("/homepage")
            else:
                flash("No edits found!")
                check_table_db = db.execute("SELECT * FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)

                return render_template("summary.html", tables=check_table_db, payments=PAYMENT_METHOD)


@app.route("/addRow", methods=["POST", "GET"])
@login_required
def addRow():
    if request.method == "POST":
        user_id = session["user_id"]
        table_names = request.form.getlist("tableName")
        table_name = table_names[0]
        name = request.form.getlist("name")
        gross = request.form.getlist("gross")
        interest = request.form.getlist("interest")
        payment = request.form.getlist("payment")
        due_date = request.form.getlist("due-date")
        calendar_date = datetime.now()
        action = "ADDED ROW"


        table_name_total_db = db.execute("SELECT SUM(total_amount) as total_amount FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        name_db = db.execute("SELECT name FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
        summary_total = 0
        if table_name_total_db[0]["total_amount"]:
            summary_total = float(table_name_total_db[0]["total_amount"])

        if name and gross and interest and payment:
            names_list = db.execute("SELECT name FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)


        for i in range(len(name)):
            if not name[i] or not gross[i] or not interest[i] or not payment[i] or payment[i] not in PAYMENT_METHOD:
                flash("All fields are required!")
                return redirect("/homepage")

            if name[i].strip().lower() in [eachName["name"].strip().lower() for eachName in name_db]:
                flash(f"{name[i]} already exists in {table_names[i]}")
                return redirect("/homepage")


            debtors = 1
            unpaid = 1
            paid = 0
            interest_percentage_rate = float(interest[i]) / 100
            interest_rate = float(gross[i]) * interest_percentage_rate
            total_amount = float(gross[i]) + interest_rate
            db.execute("INSERT INTO table_summary (user_id, table_name, name, gross, interest, interest_rate, total_amount, payment, date, due_date, total_gross, total_interest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name[i], gross[i], interest[i], interest_rate, total_amount, payment[i], calendar_date, due_date[i], gross[i], interest_rate)
            summary_total += total_amount
            db.execute("INSERT INTO tables (user_id, table_name, debtors, debtor_name, paid, unpaid, date, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, debtors, name[i], paid, unpaid, calendar_date, total_amount)
            debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name[i])
            debtor_id = debtor_id_db[0]["id"]
            db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name[i], gross[i], interest[i], payment[i], calendar_date, due_date[i], total_amount, action, debtor_id)

        flash("Added new row successfully")
        return redirect("/homepage")


@app.route("/history/<debtor_id>/<name>/<table_name>", methods=["GET", "POST"])
@login_required
def history(debtor_id, name, table_name):

    if request.method == "POST":
        user_id = session["user_id"]
        tables = request.form.get("specific_table")
        debtors = request.form.get("names_list")

        table_summary_db = db.execute("SELECT * FROM table_summary WHERE user_id = ?", user_id)
        tablenames_summary_db = db.execute("SELECT table_name FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)
        tables_list = [all_tables["table_name"] for all_tables in tablenames_summary_db]
        names_list = [all_names["name"] for all_names in table_summary_db]

        list_selected_names = db.execute("SELECT name FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, tables)
        debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, tables, debtors)
        if debtor_id_db:
            debtor_id = debtor_id_db[0]["id"]
            history_db = db.execute("SELECT * FROM history WHERE user_id = ? AND table_name = ? AND debtor_id = ?", user_id, tables, debtor_id)
        if debtors in names_list and tables in tables_list:
            return render_template("historyView.html", table_names=tablenames_summary_db, selected_name=debtors, selected_table=tables, names=list_selected_names, tables=history_db, php=php, int=int)
        else:
            flash("Selection of table or debtor is invalid!")
            return redirect("/homepage")

    else:
        user_id = session["user_id"]
        table_summary_db = db.execute("SELECT * FROM table_summary WHERE user_id = ?", user_id)
        tablenames_summary_db = db.execute("SELECT table_name FROM table_summary WHERE user_id = ? GROUP BY table_name", user_id)
        tables_list = [all_tables["table_name"] for all_tables in tablenames_summary_db]
        names_list = [all_names["name"] for all_names in table_summary_db]
        selected_from_summary = False
        if table_summary_db:
            if tablenames_summary_db and name not in names_list and table_name not in tables_list:
                selected_from_summary = False
                return render_template("history.html", table=table_summary_db, table_names=tablenames_summary_db, from_summary=selected_from_summary)
            elif tablenames_summary_db and name in names_list and table_name in tables_list:
                selected_from_summary = True
                history_db = db.execute("SELECT * FROM history WHERE user_id = ? AND table_name = ? AND debtor_id = ?", user_id, table_name, debtor_id)
                list_selected_names = db.execute("SELECT name FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
                return render_template("history.html", table=table_summary_db, table_names=tablenames_summary_db, from_summary=selected_from_summary, selected_name=name, selected_table=table_name, names=list_selected_names, tables=history_db, php=php, int=int)
        else:
            return render_template("history.html")

@app.route('/get_debtors/<specific_table>')
def get_debtors(specific_table):
    user_id = session["user_id"]
    debtors = db.execute("SELECT debtor_name FROM tables WHERE user_id = ? AND table_name = ?", user_id, specific_table)
    debtor_names = [debtor["debtor_name"] for debtor in debtors]
    return jsonify({"names": debtor_names})




@app.route('/addInterest', methods=["POST"])
@login_required
def addInterest():
    if request.method == "POST":
        user_id = session["user_id"]
        table_id = request.form.get("id")
        table_name = request.form.get("table-name")
        name = request.form.get("debtor_name")
        gross = request.form.get("debtor_gross")
        interest = request.form.get("add-interest")
        payment = request.form.get("debtor_payment")
        due_date = request.form.get("due-date")
        total_amount = request.form.get("total_amount")
        calendar_date = datetime.now()
        action = "ADD INTEREST"

        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, name)
        debtor = tables_debtor_db[0]["debtors"]
        debtor_paid = tables_debtor_db[0]["paid"]
        debtor_unpaid = tables_debtor_db[0]["unpaid"]

        if int(debtor) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
            flash("Debtor is already paid!")
            return redirect("/homepage")

        if not due_date:
            flash("Due date is required!")
            return redirect("/homepage")

        new_gross = float(total_amount)
        interest_percentage_rate = float(interest) / 100
        new_interest_rate = float(new_gross) * interest_percentage_rate
        new_total_amount = float(new_gross) + new_interest_rate


        total_interest_db = db.execute("SELECT total_interest FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, name)
        total_interest = total_interest_db[0]["total_interest"]

        new_total_interest = float(total_interest) + float(new_interest_rate)


        db.execute("UPDATE table_summary SET gross = ?, interest = ?, interest_rate = ?, total_amount = ?, due_date = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", new_gross, interest, new_interest_rate, new_total_amount, due_date, new_total_interest, table_id, user_id, table_name, name)
        db.execute("UPDATE tables SET total_amount = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", new_total_amount, user_id, table_name, name)
        debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
        debtor_id = debtor_id_db[0]["id"]
        db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, new_gross, interest, payment, calendar_date, due_date, new_total_amount, action, debtor_id)

        flash(f"Added New Interest to {name} from {table_name}!")
        return redirect("/homepage")


@app.route('/addPartial', methods=["POST"])
@login_required
def addPartial():
    if request.method == "POST":
        user_id = session["user_id"]
        table_id = request.form.get("id")
        table_name = request.form.get("table-name")
        name = request.form.get("debtor_name")
        debtor_gross = request.form.get("debtor_gross")
        debtor_interest = request.form.get("debtor_interest")
        total_amount = request.form.get("total_amount")
        interest = request.form.get("interest")
        payment = request.form.get("payment")
        calendar_date = datetime.now()
        due_date = request.form.get("due-date")
        last_payment_date = request.form.get("last-payment-date")
        payment_amount = request.form.get("payment-amount")

        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, name)
        debtor = tables_debtor_db[0]["debtors"]
        debtor_paid = tables_debtor_db[0]["paid"]
        debtor_unpaid = tables_debtor_db[0]["unpaid"]

        if int(debtor) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
            flash("Debtor is already paid!")
            return redirect("/homepage")


        if not payment or payment not in PAYMENT_METHOD:
            flash("Payment method is required!")
            return redirect("/homepage")

        if not due_date:
            flash("Due date is required!")
            return redirect("/homepage")

        if not last_payment_date:
            flash("Last Payment Date is required!")
            return redirect("/homepage")

        if not payment_amount:
            flash("Payment amount is required!")
            return redirect("/homepage")


        if interest == '':
            interest = 0

        if int(interest) == 0:
            interest = None


        if interest:
            action = "ADD PARTIAL PAYMENT WITH INTEREST"

            if float(payment_amount) > float(total_amount):
                flash(f"Invalid partial amount of {php(payment_amount)}")
                return redirect("/homepage")


            if float(payment_amount) > float(total_amount):
                new_gross = 0
                interest_percentage_rate = float(interest) / 100
                new_interest_rate = float(payment_amount) * float(interest_percentage_rate)
                remaining_bal = 0
            elif float(payment_amount) < float(total_amount):
                new_gross = float(total_amount) - float(payment_amount)
                interest_percentage_rate = float(interest) / 100
                new_interest_rate = float(new_gross) * interest_percentage_rate
                remaining_bal = float(new_gross) + float(new_interest_rate)


            total_interest_db = db.execute("SELECT total_interest FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, name)
            total_interest = total_interest_db[0]["total_interest"]

            new_total_interest = float(total_interest) + float(new_interest_rate)

            amount_paid_db = db.execute("SELECT amount_paid FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
            if amount_paid_db[0]["amount_paid"]:
                amount_paid = amount_paid_db[0]["amount_paid"]
            elif not amount_paid_db[0]["amount_paid"]:
                amount_paid = 0

            update_payment_amount = float(payment_amount) + float(amount_paid)

            db.execute("UPDATE table_summary SET gross = ?, interest = ?, interest_rate = ?, total_amount = ?, payment = ?, due_date = ?, amount_paid = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", new_gross, interest, new_interest_rate, remaining_bal, payment, due_date, update_payment_amount, new_total_interest, table_id, user_id, table_name, name)
            db.execute("UPDATE tables SET total_amount = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", remaining_bal, user_id, table_name, name)
            if remaining_bal == 0:
                action = "PAID BY PARTIAL WITH INTEREST!"
                debtors = 0
                paid = 1
                unpaid = 0
                db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND name = ?", debtors, paid, unpaid, user_id, table_name, name)
                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                debtor_id = debtor_id_db[0]["id"]
                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, last_payment_date, remaining_bal, action, debtor_id, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, new_gross, interest, payment, calendar_date, due_date, last_payment_date, remaining_bal, action, debtor_id, payment_amount)
            else:
                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                debtor_id = debtor_id_db[0]["id"]
                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, last_payment_date, remaining_bal, action, debtor_id, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, new_gross, interest, payment, calendar_date, due_date, last_payment_date, remaining_bal, action, debtor_id, payment_amount)
            flash("Added Partial With Interest")
            return redirect("/homepage")

        elif not interest:
            action = "ADD PARTIAL PAYMENT NO INTEREST"
            new_interest = ""

            if float(payment_amount) > float(total_amount):
                flash(f"Invalid partial amount of {php(float(payment_amount))}")
                return redirect("/homepage")

            remaining_bal = float(total_amount) - float(payment_amount)

            if float(payment_amount) > float(debtor_gross):
                new_gross = 0
            else:
                new_gross = float(remaining_bal)


            amount_paid_db = db.execute("SELECT amount_paid FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
            if amount_paid_db[0]["amount_paid"]:
                amount_paid = amount_paid_db[0]["amount_paid"]
            elif not amount_paid_db[0]["amount_paid"]:
                amount_paid = 0

            update_payment_amount = float(payment_amount) + float(amount_paid)

            db.execute("UPDATE table_summary SET gross = ?, interest = ?, total_amount = ?, payment = ?, due_date = ?, amount_paid = ? WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", new_gross, new_interest, remaining_bal, payment, due_date, update_payment_amount, table_id, user_id, table_name, name)
            db.execute("UPDATE tables SET total_amount = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", remaining_bal, user_id, table_name, name)
            if remaining_bal == 0:
                action = "PAID BY PARTIAL WITH NO INTEREST!"
                debtors = 0
                paid = 1
                unpaid = 0
                db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtors, paid, unpaid, user_id, table_name, name)
                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                debtor_id = debtor_id_db[0]["id"]
                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, last_payment_date, remaining_bal, action, debtor_id, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, new_gross, debtor_interest, payment, calendar_date, due_date, last_payment_date, remaining_bal, action, debtor_id, payment_amount)
            else:
                debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
                debtor_id = debtor_id_db[0]["id"]
                db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, last_payment_date, remaining_bal, action, debtor_id, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, new_gross, debtor_interest, payment, calendar_date, due_date, last_payment_date, remaining_bal, action, debtor_id, payment_amount)
            flash("Added Partial With No Interest")
            return redirect("/homepage")


@app.route('/addDebt', methods=["POST"])
@login_required
def addDebt():
    if request.method == "POST":
        user_id = session["user_id"]
        table_id = request.form.get("id")
        table_name = request.form.get("table-name")
        name = request.form.get("debtor_name")
        gross = request.form.get("gross")
        interest = request.form.get("interest")
        payment = request.form.get("payment")
        due_date = request.form.get("due-date")
        calendar_date = datetime.now()
        total_amount = request.form.get("total_amount")
        total_gross = request.form.get("total_gross")
        total_interest = request.form.get("total_interest")
        action = "EXTRA DEBT"

        if not gross:
            flash("Gross is required!")
            return redirect("/homepage")
        if not interest:
            flash("Interest is required!")
            return redirect("/homepage")
        if not payment or payment not in PAYMENT_METHOD:
            flash("Payment method is required!")
            return redirect("/homepage")
        if not due_date:
            flash("Due date is required!")
            return redirect("/homepage")



        new_gross = float(total_amount) + float(gross)
        interest_percentage_rate = float(interest) / 100
        new_interest_rate = float(new_gross) * interest_percentage_rate
        new_total_amount = float(new_gross) + new_interest_rate


        new_total_gross = float(total_gross) + float(gross)
        new_total_interest = float(total_interest) + float(new_interest_rate)

        tables_debtor_db = db.execute("SELECT * FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, name)
        debtor = tables_debtor_db[0]["debtors"]
        debtor_paid = tables_debtor_db[0]["paid"]
        debtor_unpaid = tables_debtor_db[0]["unpaid"]

        if int(debtor) == 0 and int(debtor_paid) == 1 and int(debtor_unpaid) == 0:
            debtor_count = 1
            paid_count = 0
            unpaid_count = 1
            db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtor_count, paid_count, unpaid_count, user_id, table_name, name)


        db.execute("UPDATE table_summary SET user_id = ?, table_name = ?, name = ?, gross = ?, interest = ?, interest_rate = ?, total_amount = ?, payment = ?, due_date = ?, total_gross = ?, total_interest = ? WHERE id = ? AND user_id = ? AND table_name = ? AND name = ? ", user_id, table_name, name, new_gross, interest, new_interest_rate, new_total_amount, payment, due_date, new_total_gross, new_total_interest, table_id, user_id, table_name, name)
        db.execute("UPDATE tables SET total_amount = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", new_total_amount, user_id, table_name, name)
        debtor_id_db = db.execute("SELECT id FROM table_summary WHERE user_id = ? AND table_name = ? AND name = ?", user_id, table_name, name)
        debtor_id = debtor_id_db[0]["id"]
        db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, remaining_bal, action, debtor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, new_total_amount, action, debtor_id)
        flash("Added new debt successfully!")
        return redirect("/homepage")



@app.route('/paidRow/<table_id>/<name>/<table_name>')
@login_required
def paidRow(table_id, name, table_name):
    user_id = session["user_id"]
    action = "PAID"
    interest = ""
    calendar_date = datetime.now()
    due_date = " "
    total_amount_db = db.execute("SELECT total_amount FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, name)
    amount_paid_db = db.execute("SELECT amount_paid FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, name)
    payment_db = db.execute("SELECT payment FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", table_id, user_id, table_name, name)

    if payment_db[0]["payment"]:
        payment = payment_db[0]["payment"]
    else:
        payment = ""

    if total_amount_db[0]["total_amount"]:
        total = total_amount_db[0]["total_amount"]
        updated_total = 0
    else:
        flash("Already paid!")
        return redirect("/homepage")

    if amount_paid_db[0]["amount_paid"]:
        paid = amount_paid_db[0]["amount_paid"]
        updated_paid = float(total) + float(paid)
    else:
        paid = 0
        updated_paid = float(total)

    history_deducted = float(total)
    total = 0
    gross = 0
    debtors = 0
    paid = 1
    unpaid = 0

    db.execute("UPDATE table_summary SET gross = ?, interest = ?, total_amount = ?, amount_paid = ? WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", gross, interest, updated_total, updated_paid, table_id, user_id, table_name, name)
    db.execute("UPDATE tables SET debtors = ?, paid = ?, unpaid = ?, total_amount = ? WHERE user_id = ? AND table_name = ? AND debtor_name = ?", debtors, paid, unpaid, updated_total, user_id, table_name, name)
    db.execute("INSERT INTO history (user_id, table_name, name, gross, interest, payment, date, due_date, last_payment_date, remaining_bal, action, debtor_id, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_id, table_name, name, gross, interest, payment, calendar_date, due_date, calendar_date, updated_total, action, table_id, history_deducted)

    flash(f"{name} is now paid!")
    return redirect("/homepage")



@app.route('/deleteRow/<debtor_id>/<name>/<table_name>')
@login_required
def deleteRow(debtor_id, name, table_name):
    user_id = session["user_id"]
    db.execute("DELETE FROM table_summary WHERE id = ? AND user_id = ? AND table_name = ? AND name = ?", debtor_id, user_id, table_name, name)
    db.execute("DELETE FROM tables WHERE user_id = ? AND table_name = ? AND debtor_name = ?", user_id, table_name, name)
    db.execute("DELETE FROM history WHERE user_id = ? AND table_name = ? AND debtor_id = ?", user_id, table_name, debtor_id)

    flash("Deleted row successfully!")
    return redirect("/homepage")



@app.route('/deleteTable/<table_name>')
@login_required
def deleteTable(table_name):
    user_id = session["user_id"]
    db.execute("DELETE FROM table_summary WHERE user_id = ? AND table_name = ?", user_id, table_name)
    db.execute("DELETE FROM tables WHERE user_id = ? AND table_name = ?", user_id, table_name)
    db.execute("DELETE FROM history WHERE user_id = ? AND table_name = ?", user_id, table_name)

    flash("Deleted table successully!")
    return redirect("/homepage")







if __name__ == '__main__':
    app.run(debug=True)

# Snippets of CS50 code for PS9 Finance, were used and/or modified to fit the project
import os
import shutil
import sqlite3
import json

from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
today = date.today()

from helpers import error, login_required, execute_query, fetch_data, process_data, cache_clear, fetch_by_fdc_id, sum_selected, run_transaction, fetch_averages


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies) - Borrowed from CS50 PS9
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

local_cache = os.path.abspath("flask_session")
cache_clear(local_cache)

@app.route("/")
@login_required
def index():
    return render_template("layout.html")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Written by me for CS50 PS9 with Ducky's help
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return error("must provide username", 400)
        if len(execute_query("SELECT * FROM users WHERE username = ?", (username,))) > 0:
            return error("username already in use", 400)

        # Ensure contact was submitted - Currently not linked or needed but for future expansion
        contact = request.form.get("contact")
        if not contact:
            return error("must provide email", 400)
        if len(execute_query("SELECT * FROM users WHERE contact = ?", (contact,))) > 0:
            return error("email already in use", 400)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return error("must provide password", 400)
        # Ensure confirmation was submitted
        confirmation = request.form.get("confirmation")
        if confirmation != password:
            return error("passwords do not match, try again", 400)

        # Hash password
        hash = generate_password_hash(password)
        # Insert new user into database
        execute_query("INSERT INTO users (username, contact, hash) VALUES (?, ?, ?)", (username, contact, hash))

        return redirect("/")

    else:
        return render_template("register.html")



# CS50 code for PS9, modified
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username & password was submitted
        if not request.form.get("username"):
            return error("must provide username", 403)
        elif not request.form.get("password"):
            return error("must provide password", 403)

        # Query database for username & check username exists and password is correct
        rows = execute_query("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return error("invalid username and/or password", 403)

        # Remember which user has logged in & redirect user to home page
        session["user_id"] = rows[0]["id"]
        return redirect("/profile")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/calorie_calc", methods=["GET", "POST"])
@login_required
def calorie_calc():
    """Search for and select food & meal types"""
    if request.method == "POST":
        food_item = request.form.get("food_item")
        data = fetch_data(food_item)
        results = process_data(data)
        return render_template("calorie_calc.html", results=results[:10])
    elif request.method == "GET":
        query = request.args.get("query")
        fdcId = request.args.get("fdcId")
        if query:
            data = fetch_data(query)
            results = process_data(data)
            return jsonify(results[:10])
        elif fdcId:
            data = fetch_by_fdc_id(fdcId)
            return jsonify(data)
        else:
            return render_template("calorie_calc.html")



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user information + historical data"""
    if request.method == "GET":
        # Daily average data
        day_total_query = """
            SELECT SUM(meal_totals.total_serving) AS total_serving,
                SUM(meals.total_calories) AS total_calories,
                SUM(meal_totals.total_fat) AS total_fat,
                SUM(meal_totals.total_protein) AS total_protein,
                SUM(meal_totals.total_carbs) AS total_carbs,
                SUM(meal_totals.total_sugar) AS total_sugar,
                SUM(meal_totals.total_salt) AS total_salt
            FROM meal_totals JOIN meals ON meal_totals.meal_id = meals.id
            WHERE meals.user_id = ? AND DATE(meals.date) = DATE('now');
        """
        day_total = execute_query(day_total_query, (session["user_id"],))
        day_total = [dict(row) for row in day_total][0] if day_total else {}

        # Last meal logged
        last_meal_query = "SELECT * FROM meals WHERE user_id = ? ORDER BY id DESC LIMIT 1"
        last_meal = execute_query(last_meal_query, (session["user_id"],))
        last_meal = [dict(row) for row in last_meal][0] if last_meal else {}

        return render_template("profile.html", day_total=day_total, last_meal=last_meal)

    elif request.method == "POST":
        selected_items = json.loads(request.form.get("selectedItems"))
        result = sum_selected(selected_items)
        meal_type = request.form.get("mealType")
        try:
            queries = [
                ("INSERT INTO meals (user_id, date, meal_type, total_calories) VALUES (?, CURRENT_DATE, ?, ?)",
                (session["user_id"], meal_type, result["total_calories"]))
            ]
            meal_id = run_transaction(queries)

            additional_queries = [
                ("INSERT INTO meal_totals (meal_id, total_serving, total_fat, total_protein, total_carbs, total_sugar, total_salt, total_items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (meal_id, result["total_serving"], result["total_fat"], result["total_protein"], result["total_carbs"], result["total_sugar"], result["total_salt"], result["total_items"]))
            ]
            for item in selected_items:
                additional_queries.append(("INSERT INTO meal_items (meal_id, description, serving_size, calories, fats, proteins, carbohydrates, sugars, salt, fdcId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (meal_id, item["description"], item["servingSize"], item["calories"], item["fats"], item["proteins"], item["carbohydrates"], item["sugars"], item["salt"], item["fdcId"])))

            run_transaction(additional_queries)
        except Exception as e:
            print(f"Transaction failed: {e}")
        return redirect(url_for("profile"))



@app.route("/history", methods=["GET"])
@login_required
def history():
    """Show 7 day history of saved food items"""
    food_items = execute_query(
        "SELECT meal_items.*, meals.date, meals.meal_type FROM meal_items JOIN meals ON meal_items.meal_id = meals.id WHERE meals.user_id = ? AND date >= DATE('now', '-7 days') ORDER BY meals.date DESC, meals.id DESC",
        (session["user_id"],))
    return render_template("history.html", food_items=food_items)



@app.route("/averages", methods=["GET"])
@login_required
def average():
    """Provide daily averages according to time increments to track consistency"""
    period = request.args.get("period")

    base_query = """
        SELECT SUM(meal_totals.total_serving) AS total_serving,
            SUM(meals.total_calories) AS total_calories,
            SUM(meal_totals.total_fat) AS total_fat,
            SUM(meal_totals.total_protein) AS total_protein,
            SUM(meal_totals.total_carbs) AS total_carbs,
            SUM(meal_totals.total_sugar) AS total_sugar,
            SUM(meal_totals.total_salt) AS total_salt,
            COUNT(DISTINCT date) AS active_days
        FROM meal_totals JOIN meals ON meal_totals.meal_id = meals.id
        WHERE meals.user_id = ? AND
    """

    if period == "today":
        where_clause = "date = DATE('now');"
    elif period == "last_week":
        where_clause = "date >= DATE('now', '-7 days');"
    elif period == "this_month":
        where_clause = "date >= DATE('now', 'start of month');"
    elif period == "3_months":
        where_clause = "date >= DATE('now', 'start of month', '-2 months');"
    elif period == "6_months":
        where_clause = "date >= DATE('now', 'start of month', '-5 months');"
    elif period == "12_months":
        where_clause = "date >= DATE('now', 'start of month', '-11 months');"
    else:
        return render_template("averages.html")

    query = base_query + where_clause
    averages, active_days = fetch_averages(query, (session["user_id"],))
    return jsonify(averages=averages, active_days=active_days)



@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    """Provide top 5 foods per serving amount or per occurrence"""
    sort_by = request.form.get("sort_by")
    if sort_by == "occurence":
        most_occurence = execute_query(
            "SELECT description, COUNT(*) as count FROM meal_items JOIN meals ON meal_items.meal_id = meals.id WHERE meals.user_id = ? GROUP BY description ORDER BY count DESC LIMIT 5",
            (session["user_id"],))
        return render_template("favorites.html", most_occurence=most_occurence)
    elif sort_by == "volume":
        most_volume = execute_query(
            "SELECT description, SUM(serving_size) as total_volume FROM meal_items JOIN meals ON meal_items.meal_id = meals.id WHERE meals.user_id = ? GROUP BY description ORDER BY total_volume DESC LIMIT 5",
            (session["user_id"],))
        return render_template("favorites.html", most_volume=most_volume)
    else:
        return render_template("favorites.html")


# CS50 code for PS9, modified
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    print("Session after clear:", session)
    # Redirect user to login form
    return redirect("/login")

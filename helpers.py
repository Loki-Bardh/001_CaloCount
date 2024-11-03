# Snippets of CS50 code for PS9 Finance, were used and/or modified to fit the project
import os
import requests
import json
import sqlite3

from flask import redirect, render_template, session
from functools import wraps

# Created using ChatGPT and Ducky
def cache_clear(local_cache):
    for item in os.listdir(local_cache):
        item_path = os.path.join(local_cache, item)
        try:
            if os.path.isfile(item_path):
                    os.remove(item_path)  # Remove the file
            elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove the directory and its contents
        except Exception as e:
             print(f"Error deleting {item_path}: {e}")


def error(message, code=400):
    """Render message as an error to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Connect to the database & Create a cursor object made with Ducky
def execute_query(query, params=()):
    with sqlite3.connect('calorie_count.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()


# Allow the creation of a transaction to ensure that the sequel queries are made sequentially made with Ducky
def run_transaction(queries):
    with sqlite3.connect('calorie_count.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute("BEGIN TRANSACTION")
            for i, (query, params) in enumerate(queries):
                if i == 0:
                    cur.execute(query, params)
                    meal_id = cur.lastrowid
                else:
                    cur.execute(query, params)
            conn.commit()
            return meal_id
        except Exception as e:
            conn.rollback()
            raise e


# Connect to the API for dynamic search
def fetch_data(query):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key=xYOExBtPaNoBAzRFUlJYOafh3s3vNc8irTALRsBx&query={query}&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "foods" in data:
            return [entry for entry in data["foods"] if entry.get("dataType") != "Branded"]
        else:
            print("Unexpected JSON structure")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


# Connect to the API for search by fdcID
def fetch_by_fdc_id(fdcId):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdcId}?api_key=xYOExBtPaNoBAzRFUlJYOafh3s3vNc8irTALRsBx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        nutrients = {nutrient["nutrient"]["name"]: nutrient["amount"] for nutrient in data["foodNutrients"] if "amount" in nutrient}
        if "Total Sugars" in nutrients:
            sugars = nutrients.get("Total Sugars", 0)
        else:
            sugars = nutrients.get("Sucrose", 0) + nutrients.get("Fructose", 0) + nutrients.get("Glucose", 0) + nutrients.get("Lactose", 0) + nutrients.get("Maltose", 0)
        calories = int(3.57 * nutrients.get("Carbohydrate, by difference", 0) + 8.87 * nutrients.get("Total lipid (fat)", 0) + 2.44 * nutrients.get("Protein", 0))
        return {
            "description": data["description"],
            "calories": calories,  # Default to 0 if not found
            "fats": nutrients.get("Total lipid (fat)", 0),
            "proteins": nutrients.get("Protein", 0),
            "carbohydrates": nutrients.get("Carbohydrate, by difference", 0),
            "sugars": sugars,
            "salt": nutrients.get("Sodium, Na", 0),
            "fdcId": data.get("fdcId")
        }

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {}


# Extrapolate only the necessary data
def process_data(data):
    processed_data = []
    for item in data:
        nutrients = []
        for nutrient in item.get("foodNutrients", []):
            if "nutrient" in nutrient:
                nutrients.append({
                    "name": nutrient["nutrient"]["name"],
                    "amount": nutrient["amount"],
                    "unit": nutrient["nutrient"]["unitName"]
                })

        processed_item = {
            "description": item["description"],
            "fdcId": item["fdcId"],
            "foodNutrients": nutrients
        }
        processed_data.append(processed_item)
    return processed_data


# Total calculations for data inserts
def sum_selected(items_json):
    # Parse the JSON string into a list of dictionaries
    selected_items = items_json

    # Initialize totals
    total_serving = 0
    total_calories = 0
    total_fat = 0
    total_protein = 0
    total_carbs = 0
    total_sugar = 0
    total_salt = 0

    # Helper function to strip units and convert to float
    def strip_units(value, is_integer=False):
        number = value.split()[0]
        return int(number) if is_integer else float(number)

    # Iterate over each item and sum the nutrients
    for item in selected_items:

        if not item['calories']:
            continue
        total_serving += strip_units(item['servingSize'], is_integer=True)
        total_calories += strip_units(item['calories'], is_integer=True)
        total_fat += strip_units(item['fats'])
        total_protein += strip_units(item['proteins'])
        total_carbs += strip_units(item['carbohydrates'])
        total_sugar += strip_units(item['sugars'])
        total_salt += strip_units(item['salt'], is_integer=True)

    # Return or use the totals
    return {
        'total_serving': total_serving,
        'total_calories': total_calories,
        'total_fat': round(total_fat, 2),
        'total_protein': round(total_protein, 2),
        'total_carbs': round(total_carbs, 2),
        'total_sugar': round(total_sugar, 2),
        'total_salt': total_salt,
        'total_items': len(selected_items)
    }


# Calculate averages from the internal database
def fetch_averages(query, params):
    results = execute_query(query, params)
    if results:
        data = [dict(row) for row in results][0]
        active_days = data.get("active_days", 1)  # Default to 1 to avoid division by zero
        if active_days == 0:
            active_days = 1  # Avoid division by zero
        averages = {
            "total_serving": round((data["total_serving"] or 0) / active_days),
            "total_calories": round((data["total_calories"] or 0) / active_days),
            "total_fat": round((data["total_fat"] or 0) / active_days),
            "total_protein": round((data["total_protein"] or 0) / active_days),
            "total_carbs": round((data["total_carbs"] or 0) / active_days),
            "total_sugar": round((data["total_sugar"] or 0) / active_days),
            "total_salt": round((data["total_salt"] or 0) / active_days),
        }
        return averages, active_days
    return {}, 0



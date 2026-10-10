"""
app.py — Main application for Smart Pantry & Macro Tracker.
"""

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (CS50-style)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Configure strong secret key
app.config["SECRET_KEY"] = "super-secret-key-change-in-production"


# ─── AUTHENTICATION ROUTES ──────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username")
        elif not password:
            return apology("must provide password")
        elif password != confirmation:
            return apology("passwords do not match")

        try:
            goal_calories = float(request.form.get("goal_calories", 2500))
            goal_protein = float(request.form.get("goal_protein", 200))
            goal_carbs = float(request.form.get("goal_carbs", 250))
            goal_fats = float(request.form.get("goal_fats", 80))
        except ValueError:
            return apology("invalid macro goals")

        hash = generate_password_hash(password)
        try:
            result = db.execute(
                "INSERT INTO users (username, hash, goal_calories, goal_protein, goal_carbs, goal_fats) VALUES (?, ?, ?, ?, ?, ?)",
                username, hash, goal_calories, goal_protein, goal_carbs, goal_fats
            )
        except Exception:
            return apology("username already exists")

        session["user_id"] = result
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username")
        elif not password:
            return apology("must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password")

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""
    session.clear()
    return redirect("/login")

# ─── PANTRY MANAGEMENT ROUTES ───────────────────────────────────────────────────

@app.route("/pantry")
@login_required
def pantry():
    """Show user's pantry inventory."""
    user_id = session["user_id"]
    
    # Get all pantry items with ingredient details
    pantry_items = db.execute("""
        SELECT 
            p.id AS pantry_id,
            p.ingredient_id,
            p.quantity_grams,
            i.name AS ingredient_name,
            i.protein_per_100g,
            i.carbs_per_100g,
            i.fats_per_100g,
            i.calories_per_100g
        FROM pantry p
        JOIN ingredients i ON p.ingredient_id = i.id
        WHERE p.user_id = ?
        ORDER BY i.name
    """, user_id)
    
    # Get all available ingredients for the dropdown
    all_ingredients = db.execute("SELECT id, name FROM ingredients ORDER BY name")
    
    return render_template(
        "pantry.html",
        pantry_items=pantry_items,
        all_ingredients=all_ingredients
    )


@app.route("/pantry/add", methods=["POST"])
@login_required
def pantry_add():
    """Add ingredient to user's pantry."""
    user_id = session["user_id"]
    ingredient_id = request.form.get("ingredient_id")
    quantity_grams = request.form.get("quantity_grams")
    
    if not ingredient_id or not quantity_grams:
        return apology("must provide ingredient and quantity")
    
    try:
        quantity_grams = float(quantity_grams)
        if quantity_grams <= 0:
            return apology("quantity must be positive")
    except ValueError:
        return apology("invalid quantity")
    
    # Check if ingredient already exists in pantry
    existing = db.execute(
        "SELECT id, quantity_grams FROM pantry WHERE user_id = ? AND ingredient_id = ?",
        user_id, ingredient_id
    )
    
    if existing:
        # Update existing entry
        new_quantity = existing[0]["quantity_grams"] + quantity_grams
        db.execute(
            "UPDATE pantry SET quantity_grams = ? WHERE id = ?",
            new_quantity, existing[0]["id"]
        )
    else:
        # Insert new entry
        db.execute(
            "INSERT INTO pantry (user_id, ingredient_id, quantity_grams) VALUES (?, ?, ?)",
            user_id, ingredient_id, quantity_grams
        )
    
    flash("Ingredient added to pantry!", "success")
    return redirect("/pantry")


@app.route("/pantry/update", methods=["POST"])
@login_required
def pantry_update():
    """Update ingredient quantity in user's pantry."""
    user_id = session["user_id"]
    pantry_id = request.form.get("pantry_id")
    quantity_grams = request.form.get("quantity_grams")
    
    if not pantry_id or not quantity_grams:
        return apology("must provide pantry item and quantity")
    
    try:
        quantity_grams = float(quantity_grams)
        if quantity_grams < 0:
            return apology("quantity cannot be negative")
    except ValueError:
        return apology("invalid quantity")
    
    # Verify ownership
    item = db.execute(
        "SELECT id FROM pantry WHERE id = ? AND user_id = ?",
        pantry_id, user_id
    )
    
    if not item:
        return apology("invalid pantry item")
    
    if quantity_grams == 0:
        # Remove item if quantity is 0
        db.execute("DELETE FROM pantry WHERE id = ?", pantry_id)
        flash("Ingredient removed from pantry!", "success")
    else:
        # Update quantity
        db.execute(
            "UPDATE pantry SET quantity_grams = ? WHERE id = ?",
            quantity_grams, pantry_id
        )
        flash("Pantry updated!", "success")
    
    return redirect("/pantry")


@app.route("/pantry/remove", methods=["POST"])
@login_required
def pantry_remove():
    """Remove ingredient from user's pantry."""
    user_id = session["user_id"]
    pantry_id = request.form.get("pantry_id")
    
    if not pantry_id:
        return apology("must provide pantry item")
    
    # Verify ownership
    item = db.execute(
        "SELECT id FROM pantry WHERE id = ? AND user_id = ?",
        pantry_id, user_id
    )
    
    if not item:
        return apology("invalid pantry item")
    
    db.execute("DELETE FROM pantry WHERE id = ?", pantry_id)
    flash("Ingredient removed from pantry!", "success")
    return redirect("/pantry")


# ─── RECIPE MATCHER ENGINE ──────────────────────────────────────────────────────

@app.route("/recipes")
@login_required
def recipes():
    """Show recipes and suggest cookable meals based on pantry inventory."""
    user_id = session["user_id"]
    
    # Get all recipes
    all_recipes = db.execute("SELECT id, name, instructions FROM recipes ORDER BY name")
    
    cookable_recipes = []
    not_cookable_recipes = []
    
    for recipe in all_recipes:
        recipe_id = recipe["id"]
        
        # Get all required ingredients for this recipe
        required_ingredients = db.execute("""
            SELECT 
                ri.ingredient_id,
                ri.required_grams,
                i.name AS ingredient_name
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, recipe_id)
        
        # Check if user has enough of each ingredient
        can_cook = True
        missing_ingredients = []
        
        for req in required_ingredients:
            # Check user's pantry for this ingredient
            pantry_item = db.execute(
                "SELECT quantity_grams FROM pantry WHERE user_id = ? AND ingredient_id = ?",
                user_id, req["ingredient_id"]
            )
            
            if not pantry_item:
                can_cook = False
                missing_ingredients.append({
                    "name": req["ingredient_name"],
                    "required": req["required_grams"],
                    "have": 0
                })
            elif pantry_item[0]["quantity_grams"] < req["required_grams"]:
                can_cook = False
                missing_ingredients.append({
                    "name": req["ingredient_name"],
                    "required": req["required_grams"],
                    "have": pantry_item[0]["quantity_grams"]
                })
        
        recipe_data = {
            "id": recipe_id,
            "name": recipe["name"],
            "instructions": recipe["instructions"],
            "ingredients": required_ingredients,
            "missing": missing_ingredients
        }
        
        if can_cook:
            cookable_recipes.append(recipe_data)
        else:
            not_cookable_recipes.append(recipe_data)
    
    return render_template(
        "recipes.html",
        cookable_recipes=cookable_recipes,
        not_cookable_recipes=not_cookable_recipes
    )


# ─── MACRO ENGINE (DASHBOARD) ───────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    """Dashboard showing today's macro tracking."""
    user_id = session["user_id"]
    
    # Get user data with goals
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    
    # Calculate TODAY's consumed macros (aggregated)
    today_macros = db.execute("""
        SELECT 
            COALESCE(SUM(c.grams_consumed * i.protein_per_100g / 100.0), 0) AS total_protein,
            COALESCE(SUM(c.grams_consumed * i.carbs_per_100g / 100.0), 0) AS total_carbs,
            COALESCE(SUM(c.grams_consumed * i.fats_per_100g / 100.0), 0) AS total_fats,
            COALESCE(SUM(c.grams_consumed * i.calories_per_100g / 100.0), 0) AS total_calories
        FROM consumption_log c
        JOIN ingredients i ON c.ingredient_id = i.id
        WHERE c.user_id = ? AND DATE(c.timestamp) = DATE('now')
    """, user_id)[0]
    
    # Get today's individual consumption log entries for the table
    today_log = db.execute("""
        SELECT 
            i.name,
            c.grams_consumed,
            i.calories_per_100g,
            i.protein_per_100g,
            i.carbs_per_100g,
            i.fats_per_100g,
            c.timestamp
        FROM consumption_log c
        JOIN ingredients i ON c.ingredient_id = i.id
        WHERE c.user_id = ? AND DATE(c.timestamp) = DATE('now')
        ORDER BY c.timestamp DESC
    """, user_id)
    
    # Calculate per-entry macros
    log_with_macros = []
    for entry in today_log:
        grams = entry["grams_consumed"]
        log_with_macros.append({
            "name": entry["name"],
            "grams": grams,
            "calories": grams * entry["calories_per_100g"] / 100.0,
            "protein": grams * entry["protein_per_100g"] / 100.0,
            "carbs": grams * entry["carbs_per_100g"] / 100.0,
            "fats": grams * entry["fats_per_100g"] / 100.0,
            "timestamp": entry["timestamp"]
        })
    
    # Get ingredients for food logging dropdown
    ingredients = db.execute("SELECT id, name FROM ingredients ORDER BY name")
    
    return render_template(
        "index.html",
        user=user,
        today_macros=today_macros,
        log=log_with_macros,
        ingredients=ingredients
    )


@app.route("/consume", methods=["POST"])
@login_required
def consume():
    """Log food consumption and deduct from pantry."""
    user_id = session["user_id"]
    ingredient_id = request.form.get("ingredient_id")
    grams_consumed = request.form.get("grams")
    
    if not ingredient_id or not grams_consumed:
        return apology("must provide ingredient and grams")
    
    try:
        grams_consumed = float(grams_consumed)
        if grams_consumed <= 0:
            return apology("grams must be positive")
    except ValueError:
        return apology("invalid grams amount")
    
    # Check if user has enough in pantry
    pantry_item = db.execute(
        "SELECT id, quantity_grams FROM pantry WHERE user_id = ? AND ingredient_id = ?",
        user_id, ingredient_id
    )
    
    if not pantry_item:
        return apology("ingredient not in your pantry")
    
    if pantry_item[0]["quantity_grams"] < grams_consumed:
        return apology(f"insufficient quantity in pantry (you have {pantry_item[0]['quantity_grams']}g)")
    
    # Insert into consumption_log
    db.execute(
        "INSERT INTO consumption_log (user_id, ingredient_id, grams_consumed) VALUES (?, ?, ?)",
        user_id, ingredient_id, grams_consumed
    )
    
    # Deduct from pantry
    new_quantity = pantry_item[0]["quantity_grams"] - grams_consumed
    if new_quantity == 0:
        db.execute("DELETE FROM pantry WHERE id = ?", pantry_item[0]["id"])
    else:
        db.execute("UPDATE pantry SET quantity_grams = ? WHERE id = ?", new_quantity, pantry_item[0]["id"])
    
    flash("Food consumption logged!", "success")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

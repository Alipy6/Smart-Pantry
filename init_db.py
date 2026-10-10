"""
init_db.py — Creates the SQLite schema and seeds initial data.
Run once: python init_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project.db")

# Remove existing DB so we start fresh
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ─── SCHEMA ────────────────────────────────────────────────────────────────────

cur.executescript("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    goal_calories REAL DEFAULT 2500,
    goal_protein REAL DEFAULT 200,
    goal_carbs REAL DEFAULT 250,
    goal_fats REAL DEFAULT 80
);

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    protein_per_100g REAL NOT NULL,
    carbs_per_100g REAL NOT NULL,
    fats_per_100g REAL NOT NULL,
    calories_per_100g REAL NOT NULL
);

CREATE TABLE pantry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    UNIQUE(user_id, ingredient_id)
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    instructions TEXT NOT NULL
);

CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    required_grams REAL NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE consumption_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    grams_consumed REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);
""")

# ─── SEED: INGREDIENTS (high-performance sports nutrition) ────────────────────

ingredients = [
    # (name, protein, carbs, fats, calories per 100g)
    ("Whey Protein Isolate", 90.0, 3.0, 1.0, 380),
    ("Chicken Breast (cooked)", 31.0, 0.0, 3.6, 165),
    ("White Rice (cooked)", 2.7, 28.0, 0.3, 130),
    ("Whole Eggs", 13.0, 1.1, 11.0, 155),
    ("Oats (dry)", 13.5, 67.0, 7.0, 389),
    ("Olive Oil", 0.0, 0.0, 100.0, 900),
    ("Greek Yogurt (0%)", 10.0, 4.0, 0.5, 59),
    ("Banana", 1.1, 23.0, 0.3, 89),
    ("Peanut Butter", 25.0, 20.0, 50.0, 588),
    ("Sweet Potato (cooked)", 1.6, 20.0, 0.1, 86),
    ("Salmon Fillet (cooked)", 25.0, 0.0, 12.0, 208),
    ("Broccoli (steamed)", 2.8, 7.0, 0.4, 35),
    ("Almonds", 21.0, 22.0, 49.0, 579),
    ("Cottage Cheese (low-fat)", 12.0, 4.5, 1.5, 72),
    ("Tuna (canned in water)", 26.0, 0.0, 1.0, 116),
]

cur.executemany(
    "INSERT INTO ingredients (name, protein_per_100g, carbs_per_100g, fats_per_100g, calories_per_100g) VALUES (?, ?, ?, ?, ?)",
    ingredients,
)

# ─── SEED: RECIPES ─────────────────────────────────────────────────────────────

recipes = [
    (
        "Protein Power Bowl",
        "1. Cook rice and let cool slightly.\n"
        "2. Grill seasoned chicken breast, slice.\n"
        "3. Steam broccoli for 4 minutes.\n"
        "4. Assemble bowl: rice base, chicken, broccoli.\n"
        "5. Drizzle with olive oil. Season with salt & pepper.",
    ),
    (
        "Overnight Oats & Whey",
        "1. Combine oats, whey protein, and Greek yogurt in a jar.\n"
        "2. Add water/milk to desired consistency.\n"
        "3. Slice banana on top.\n"
        "4. Refrigerate overnight (6+ hours).\n"
        "5. Top with almonds before serving.",
    ),
    (
        "Salmon & Sweet Potato Plate",
        "1. Preheat oven to 200°C.\n"
        "2. Season salmon with olive oil, salt, lemon.\n"
        "3. Cube sweet potato, toss in olive oil.\n"
        "4. Roast sweet potato 25 min, salmon 12-15 min.\n"
        "5. Plate together, garnish with steamed broccoli.",
    ),
]

cur.executemany("INSERT INTO recipes (name, instructions) VALUES (?, ?)", recipes)

# ─── SEED: RECIPE_INGREDIENTS ──────────────────────────────────────────────────

# Recipe 1: Protein Power Bowl
# Rice (id=3), Chicken (id=2), Broccoli (id=12), Olive Oil (id=6)
recipe_ingredients = [
    (1, 3, 200),   # 200g cooked rice
    (1, 2, 150),   # 150g chicken breast
    (1, 12, 100),  # 100g broccoli
    (1, 6, 10),    # 10ml olive oil
    # Recipe 2: Overnight Oats & Whey
    # Oats (id=5), Whey (id=1), Greek Yogurt (id=7), Banana (id=8), Almonds (id=13)
    (2, 5, 80),    # 80g oats
    (2, 1, 30),    # 30g whey
    (2, 7, 150),   # 150g greek yogurt
    (2, 8, 100),   # 100g banana
    (2, 13, 20),   # 20g almonds
    # Recipe 3: Salmon & Sweet Potato Plate
    # Salmon (id=11), Sweet Potato (id=10), Olive Oil (id=6), Broccoli (id=12)
    (3, 11, 180),  # 180g salmon
    (3, 10, 200),  # 200g sweet potato
    (3, 6, 15),    # 15ml olive oil
    (3, 12, 80),   # 80g broccoli
]

cur.executemany(
    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, required_grams) VALUES (?, ?, ?)",
    recipe_ingredients,
)

conn.commit()
conn.close()

print(f"✅ Database created and seeded at: {DB_PATH}")
print(f"   - {len(ingredients)} ingredients")
print(f"   - {len(recipes)} recipes")
print(f"   - {len(recipe_ingredients)} recipe-ingredient links")

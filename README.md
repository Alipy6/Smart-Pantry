# Smart Pantry & Macro Tracker
# CS50x Final Project

## Overview

Smart Pantry & Macro Tracker is a full-stack web application built with Python/Flask for fitness and bodybuilding enthusiasts. It manages kitchen inventory, calculates exact macronutrients for daily goals, and dynamically suggests recipes based on available pantry items.

### Key Features

1. **User Authentication** — Secure registration and login using werkzeug password hashing
2. **Pantry Management** — Track ingredient quantities with add/update/remove functionality
3. **Macro Tracking** — Log food consumption and view today's totals with visual progress bars
4. **Recipe Matcher** — Algorithm compares pantry inventory against recipe requirements
5. **Custom Goals** — Set personalized daily calorie, protein, carb, and fat targets

---

## Architecture

### Tech Stack

- **Backend**: Python 3, Flask framework
- **Database**: SQLite3 via cs50 library (`from cs50 import SQL`)
- **Frontend**: HTML5, Jinja2 templates, Bootstrap 5 (CDN), Vanilla JavaScript
- **Security**: werkzeug.security for password hashing

### Database Schema

The application uses 6 tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts with authentication hashes and daily macro goals |
| `ingredients` | Nutritional database (protein/carbs/fats/calories per 100g) |
| `pantry` | User-specific ingredient inventory tracked in grams |
| `recipes` | Recipe definitions with cooking instructions |
| `recipe_ingredients` | Junction table linking recipes to required ingredients |
| `consumption_log` | Audit trail of all food consumed with timestamps |

#### The `consumption_log` Table

This table is critical to the macro tracking system:

```sql
CREATE TABLE consumption_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    grams_consumed REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);
```

**Function:** Records every food consumption event with a timestamp. The dashboard queries this table filtered by `DATE(timestamp) = DATE('now')` to calculate today's running totals for protein, carbs, fats, and calories.

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd "final cs50x"
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database (first run only):
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser to `http://127.0.0.1:5000/`

---

## Usage Guide

### First-Time Setup

1. **Register** a new account with your username, password, and daily macro goals
2. **Add ingredients** to your pantry via the Pantry page
3. **Log meals** on the Dashboard by selecting ingredients and entering grams consumed
4. **Browse recipes** to see which meals you can cook with current inventory

### Macro Calculation Formula

Macros are calculated using this formula for each logged entry:

```
consumed_protein = (grams_consumed × protein_per_100g) / 100
consumed_carbs   = (grams_consumed × carbs_per_100g) / 100
consumed_fats    = (grams_consumed × fats_per_100g) / 100
consumed_calories= (grams_consumed × calories_per_100g) / 100
```

Daily totals are the sum of all entries logged within the current calendar day.

---

## Security Considerations

- Passwords are hashed using `werkzeug.security.generate_password_hash()`
- All SQL queries use parameterized placeholders (`?`) to prevent SQL injection
- Session-based authentication with Flask-Session
- Routes protected by `@login_required` decorator

---

## Project Structure

```
final cs50x/
├── app.py                  # Main Flask application
├── helpers.py              # @login_required decorator and apology() function
├── init_db.py              # Database initialization and seeding script
├── project.db              # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
├── .gitignore             # Excludes venv/, *.db, __pycache__
├── static/
│   ├── styles.css         # Custom CSS styling
│   └── script.js          # Vanilla JavaScript enhancements
└── templates/
    ├── layout.html         # Base template with navbar
    ├── index.html          # Dashboard with macro progress bars
    ├── pantry.html         # Inventory management interface
    ├── recipes.html        # Recipe matcher results
    ├── register.html       # User registration form
    ├── login.html          # User login form
    └── apology.html        # Error message template
```

---

## Author

Built as a CS50x Final Project.

## License

Educational use — CS50x coursework.

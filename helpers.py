"""
helpers.py — CS50-style helper functions for Smart Pantry & Macro Tracker.
"""

from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    """
    Decorator to enforce login requirement for routes.
    Redirects to /login if user_id not in session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    """
    Renders a CS50-style apology page with the provided message.
    """
    return render_template("apology.html", top=code, bottom=message), code

import calendar
import sqlite3
import re
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
DB_PATH = Path("calendar.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not DB_PATH.exists():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                time TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#e8f0fe'
            )
        """)
        conn.commit()
        conn.close()
        app.logger.info("Database initialized.")

def validate_color(color):
    """Validate hex color code to prevent XSS"""
    if not color:
        return '#e8f0fe'
    # Only allow hex colors in format #RRGGBB
    if re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return color
    return '#e8f0fe'

def validate_date(date_str):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False

def validate_time(time_str):
    """Validate time format HH:MM"""
    if not time_str:
        return True
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except (ValueError, TypeError):
        return False

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'"
    return response

@app.route("/")
def index():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    now = datetime.now()
    if not year or not month:
        year, month = now.year, now.month
    
    # Validate year and month ranges
    if not (1900 <= year <= 2100) or not (1 <= month <= 12):
        year, month = now.year, now.month

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, title, time, color, id
        FROM events
        WHERE strftime('%Y-%m', date) = ?
    """, (f"{year}-{month:02d}",))
    events = {}
    for row in cur.fetchall():
        day = int(row["date"].split("-")[2])
        # Escape output to prevent XSS
        events.setdefault(day, []).append((
            escape(row["time"]),
            escape(row["title"]),
            validate_color(row["color"]),
            row["id"]
        ))
    conn.close()

    return render_template("index.html", year=year, month=month, month_days=month_days, events=events)

def save_event(data, update=False):
    """Save event with input validation"""
    # Validate required fields
    if not data.get("title"):
        raise ValueError("Title is required")
    
    date = data.get("date", "")
    if not validate_date(date):
        raise ValueError("Invalid date format")
    
    time = data.get("time", "")
    if not validate_time(time):
        raise ValueError("Invalid time format")
    
    # Sanitize and validate color
    color = validate_color(data.get("color", "#e8f0fe"))
    
    # Limit title length to prevent abuse
    title = data["title"][:200]
    
    conn = get_db()
    cur = conn.cursor()
    try:
        if update:
            event_id = data.get("id")
            if not event_id:
                raise ValueError("Event ID is required for update")
            cur.execute(
                "UPDATE events SET date=?, time=?, title=?, color=? WHERE id=?",
                (date, time, title, color, event_id)
            )
            event_id = data["id"]
        else:
            cur.execute(
                "INSERT INTO events (date, time, title, color) VALUES (?, ?, ?, ?)",
                (date, time, title, color)
            )
            event_id = cur.lastrowid
        conn.commit()
        return event_id
    finally:
        conn.close()

@app.route("/add", methods=["POST"])
def add_event():
    try:
        event_id = save_event(request.get_json())
        return jsonify({"status": "success", "id": event_id})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/update", methods=["POST"])
def update_event():
    try:
        event_id = save_event(request.get_json(), update=True)
        return jsonify({"status": "success", "id": event_id})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    # Validate event_id is positive integer
    if event_id <= 0:
        return ("Invalid event ID", 400)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return ("", 204)

if __name__ == "__main__":
    init_db()
    # Disable debug mode in production - use environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)

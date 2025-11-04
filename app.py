import calendar
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
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

@app.route("/")
def index():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    now = datetime.now()
    if not year or not month:
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
        events.setdefault(day, []).append((row["time"], row["title"], row["color"], row["id"]))
    conn.close()

    return render_template("index.html", year=year, month=month, month_days=month_days, events=events)

def save_event(data, update=False):
    conn = get_db()
    cur = conn.cursor()
    try:
        if update:
            cur.execute(
                "UPDATE events SET date=?, time=?, title=?, color=? WHERE id=?",
                (data["date"], data.get("time", ""), data["title"], data.get("color", "#e8f0fe"), data["id"])
            )
            event_id = data["id"]
        else:
            cur.execute(
                "INSERT INTO events (date, time, title, color) VALUES (?, ?, ?, ?)",
                (data["date"], data.get("time", ""), data["title"], data.get("color", "#e8f0fe"))
            )
            event_id = cur.lastrowid
        conn.commit()
        return event_id
    finally:
        conn.close()

@app.route("/add", methods=["POST"])
def add_event():
    event_id = save_event(request.get_json())
    return jsonify({"status": "success", "id": event_id})

@app.route("/update", methods=["POST"])
def update_event():
    event_id = save_event(request.get_json(), update=True)
    return jsonify({"status": "success", "id": event_id})

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return ("", 204)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

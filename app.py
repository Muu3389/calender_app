import calendar
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

DB_PATH = Path("calendar.db")

def init_db():
    if not DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
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
        print("Database initialized.")

@app.route("/")
def index():
    # クエリパラメータから年月を取得
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    # クエリパラメータがない場合は現在の年月を使用
    now = datetime.now()
    if not year or not month:
        year, month = now.year, now.month

    # カレンダーのデータを生成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # 予定データ取得
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT date, title, time, color, id FROM events WHERE date LIKE ?", (f"{year}-{month:02d}-%",))
    events = {}
    for date,title,time,color,eid in cur.fetchall():
        day = int(date.split("-")[2])
        events.setdefault(day, []).append((time, title, color, eid))
    conn.close()
    print(events)

    return render_template(
        "index.html",
        year=year,
        month=month,
        month_days=month_days,
        events=events,
    )

@app.route("/add", methods=["POST"])
def add_event():
    data = request.get_json()
    date = data["date"]
    time = data.get("time", "")
    title = data["title"]
    color = data.get("color", "#e8f0fe")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO events (date, time, title, color) VALUES (?, ?, ?, ?)", (date, time, title, color))
    event_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"id": event_id})

@app.route("/update", methods=["POST"])
def update_event():
    data = request.get_json()
    event_id = data["id"]
    date = data["date"]
    time = data.get("time", "")
    title = data["title"]
    color = data.get("color", "#e8f0fe")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE events SET date=?, time=?, title=?, color=? WHERE id=?", (date, time, title, color, event_id))
    conn.commit()
    conn.close()

    return jsonify({"id": event_id})

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return ("", 204)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

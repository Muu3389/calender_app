from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    # クエリパラメータから年月を取得
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    now = datetime.now()
    if not year or not month:
        year, month = now.year, now.month

    cal = calendar.month(year, month)
    return render_template(
        "index.html",
        calendar_text=cal,
        year=year,
        month=month
    )

if __name__ == "__main__":
    app.run(debug=True)

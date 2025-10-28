from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

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

    return render_template(
        "index.html",
        year=year,
        month=month,
        month_days=month_days
    )

if __name__ == "__main__":
    app.run(debug=True)

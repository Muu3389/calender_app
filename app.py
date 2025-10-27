from flask import Flask, render_template
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/month")
def month():
    now = datetime.now()
    cal = calendar.month(now.year, now.month)
    return f"<pre>{cal}</pre>"

if __name__ == "__main__":
    app.run(debug=True)

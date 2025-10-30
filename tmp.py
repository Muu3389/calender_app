import sqlite3
conn = sqlite3.connect("calendar.db")
cur = conn.cursor()

# すべてのtimeを"00:00"に
cur.execute("UPDATE events SET time = '00:00' WHERE time IS NULL;")

conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("calendar.db")
cur = conn.cursor()

# colorがNULLの行をデフォルト色に更新
cur.execute("UPDATE events SET color = '#e8f0fe' WHERE color IS NULL;")

conn.commit()
conn.close()

print("既存データにデフォルト色を設定しました。")

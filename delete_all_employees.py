import sqlite3

conn = sqlite3.connect("attendance.db")
c = conn.cursor()

c.execute("DELETE FROM attendance")

c.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")

conn.commit()
conn.close()
print("✅ Tous les employés ont été supprimés.")

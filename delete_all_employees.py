import sqlite3

conn = sqlite3.connect("employees.db")
c = conn.cursor()

c.execute("DELETE FROM employees")

c.execute("DELETE FROM sqlite_sequence WHERE name='employees'")

conn.commit()
conn.close()
print("✅ Tous les employés ont été supprimés.")

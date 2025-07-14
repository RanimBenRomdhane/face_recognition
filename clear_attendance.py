import sqlite3

def clear_attendance():
    conn = sqlite3.connect("employees.db")
    c = conn.cursor()

    c.execute("DELETE FROM attendance")

    c.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")

    conn.commit()
    conn.close()
    print("✅ Table 'attendance' vidée avec succès.")

if __name__ == "__main__":
    clear_attendance()

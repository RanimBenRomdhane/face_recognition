import sqlite3

def create_tables():
    conn = sqlite3.connect("employees.db")
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        cin TEXT UNIQUE,
        encoding BLOB,
        image_path TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cin TEXT,
        date TEXT,
        time_in TEXT,
        time_out TEXT

    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Tables créées avec succès.")

if __name__ == "__main__":
    create_tables()
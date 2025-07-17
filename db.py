# create_tables.py

import sqlite3

def create_tables():
    conn = sqlite3.connect("employees.db")
    c = conn.cursor()

    # Table des employés
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

    # Table des présences
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cin TEXT,
        date TEXT,
        time_in TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Tables créées avec succès.")

# Crée les tables si le fichier est lancé directement
if __name__ == "__main__":
    create_tables()

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
        cin TEXT UNIQUE
    )
    ''')

    # Table des photos (plusieurs images par employé)
    c.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cin TEXT,
        image_path TEXT,
        encoding BLOB,
        FOREIGN KEY (cin) REFERENCES employees(cin) ON DELETE CASCADE
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

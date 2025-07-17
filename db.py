import sqlite3

def create_tables():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            cin TEXT UNIQUE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS employee_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            photo_path TEXT,
            encoding BLOB,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')
    
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
    print("Tables créées avec succès.")

if __name__ == "__main__":
    create_tables()

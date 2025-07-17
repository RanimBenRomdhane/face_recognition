import cv2
import face_recognition
import sqlite3
import pickle
import os

DB_PATH = 'employees.db'
ENCODINGS_FILE = 'encodings.pickle'

def create_tables():
    conn = sqlite3.connect(DB_PATH)
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

def add_employee(nom, prenom, cin, photo_path):
    # Insérer dans la table employees
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO employees (nom, prenom, cin) VALUES (?, ?, ?)", (nom, prenom, cin))
        employee_id = c.lastrowid
    except sqlite3.IntegrityError:
        print(f"Erreur : un employé avec CIN {cin} existe déjà.")
        conn.close()
        return False
    conn.commit()

    # Charger la photo et calculer encodage
    image = face_recognition.load_image_file(photo_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        print("Aucun visage détecté sur la photo.")
        conn.close()
        return False
    encoding = encodings[0]

    # Stocker photo et encodage dans employee_photos
    c.execute("INSERT INTO employee_photos (employee_id, photo_path, encoding) VALUES (?, ?, ?)",
              (employee_id, photo_path, encoding.tobytes()))
    conn.commit()
    conn.close()

    # Mettre à jour le fichier encodings.pickle
    update_encodings_file()
    print(f"Employé {nom} {prenom} ajouté avec succès.")
    return True

def update_encodings_file():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT employees.cin, employee_photos.encoding
        FROM employees
        JOIN employee_photos ON employees.id = employee_photos.employee_id
    ''')
    results = c.fetchall()
    conn.close()

    all_encodings = []
    all_cins = []
    for cin, encoding_blob in results:
        encoding = pickle.loads(pickle.dumps(encoding_blob))  # convert BLOB bytes to numpy array
        import numpy as np
        encoding_np = np.frombuffer(encoding_blob, dtype=np.float64)  # float64 used by face_recognition
        encoding_np = encoding_np.reshape((128,))
        all_encodings.append(encoding_np)
        all_cins.append(cin)

    data = {"encodings": all_encodings, "cins": all_cins}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

if __name__ == "__main__":
    create_tables()
    print("Ajout d'un employé (exemple):")
    nom = input("Nom : ")
    prenom = input("Prénom : ")
    cin = input("CIN : ")
    photo_path = input("Chemin de la photo (ex: photos/monimage.jpg) : ")
    if not os.path.exists(photo_path):
        print("Erreur : Le fichier photo n'existe pas.")
    else:
        add_employee(nom, prenom, cin, photo_path)

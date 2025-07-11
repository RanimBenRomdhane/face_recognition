import sqlite3
import os
import face_recognition
import cv2
import pickle

conn = sqlite3.connect('employees.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    cin TEXT UNIQUE,
    encoding BLOB,
    image_path TEXT
)''')
conn.commit()

nom = input("Nom : ")
prenom = input("Prénom : ")
cin = input("CIN : ")

image_path = f"photos/{cin}.png"
print("📸 Sélectionne une image de l'employé (format PNG)...")

file_path = input("Chemin vers l'image : ")
image = face_recognition.load_image_file(file_path)
face_encodings = face_recognition.face_encodings(image)

if not face_encodings:
    print("❌ Aucun visage détecté dans l'image.")
    exit()

cv2.imwrite(image_path, cv2.imread(file_path))

encoding_pickle = pickle.dumps(face_encodings[0])
try:
    c.execute("INSERT INTO employees (nom, prenom, cin, encoding, image_path) VALUES (?, ?, ?, ?, ?)", 
              (nom, prenom, cin, encoding_pickle, image_path))
    conn.commit()
    print("✅ Employé ajouté avec succès.")
except sqlite3.IntegrityError:
    print("❌ CIN existe déjà dans la base.")
finally:
    conn.close()
    
    
    "C:\Users\EXOAIKO\Pictures\Camera Roll\WIN_20250711_14_36_52_Pro.jpg"
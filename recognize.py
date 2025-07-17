import cv2
import face_recognition
import pickle
import sqlite3
from datetime import datetime
from db import create_tables  # ✅ import de la fonction de création des tables

def load_known_faces():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT nom, prenom, cin, encoding FROM employees")
    rows = c.fetchall()
    conn.close()
    known_encodings = []
    known_cins = []
    known_names = []
    for row in rows:
        nom, prenom, cin, encoding_blob = row
        encoding = pickle.loads(encoding_blob)
        known_encodings.append(encoding)
        known_names.append(f"{nom} {prenom}")
        known_cins.append(cin)
    return known_encodings, known_names, known_cins

def log_attendance(cin):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    # ✅ Suppression de la ligne CREATE TABLE IF NOT EXISTS (car déjà créée dans create_tables.py)
    c.execute("INSERT INTO attendance (cin, date, time_in) VALUES (?, ?, ?)", (cin, date, time))
    conn.commit()
    conn.close()

def main():
    create_tables()  # ✅ Crée les tables si elles n'existent pas
    known_encodings, known_names, known_cins = load_known_faces()
    video_capture = cv2.VideoCapture(0)
    print("✅ Démarrage reconnaissance faciale. Appuyez sur 'q' pour quitter.")

    while True:
        ret, frame = video_capture.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Inconnu"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                cin = known_cins[first_match_index]
                log_attendance(cin)
            else:
                name = "Inconnu"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow("Reconnaissance faciale", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

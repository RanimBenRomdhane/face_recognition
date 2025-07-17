import cv2
import face_recognition
import sqlite3
import pickle
from datetime import datetime
import numpy as np

# Charger les encodages connus depuis la base de données
def load_known_encodings():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
        SELECT employees.cin, employee_photos.encoding
        FROM employees
        JOIN employee_photos ON employees.id = employee_photos.employee_id
    ''')
    rows = c.fetchall()
    conn.close()

    encodings = []
    cins = []

    for cin, encoding_blob in rows:
        encoding = pickle.loads(encoding_blob)  # Dé-sérialiser avec pickle
        encodings.append(encoding)
        cins.append(cin)

    return encodings, cins

# Créer la table attendance si elle n'existe pas
def create_table():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
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

# Enregistrer une nouvelle présence
def log_attendance(cin):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_in = now.strftime("%H:%M:%S")

    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("INSERT INTO attendance (cin, date, time_in) VALUES (?, ?, ?)", (cin, date, time_in))
    conn.commit()
    conn.close()
    print(f"Présence enregistrée pour CIN: {cin} à {date} {time_in}")

def main():
    print("✅ Démarrage reconnaissance faciale. Appuyez sur 'q' pour quitter.")
    video_capture = cv2.VideoCapture(0)

    create_table()
    known_encodings, known_cins = load_known_encodings()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Inconnu"

            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    cin = known_cins[i]
                    counts[cin] = counts.get(cin, 0) + 1

                cin = max(counts, key=counts.get)
                name = cin
                log_attendance(cin)

            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow("Reconnaissance Faciale", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

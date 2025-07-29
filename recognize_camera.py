import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import pickle
import sqlite3
import json
import os
from datetime import datetime
from threading import Thread

from db import create_tables  # Assure-toi que ce module existe et crée bien les tables nécessaires

CONFIG_FILE = "camera_config.json"

def load_known_faces():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
        SELECT e.nom, e.prenom, p.cin, p.encoding
        FROM photos p
        INNER JOIN employees e ON p.cin = e.cin
    ''')
    rows = c.fetchall()
    conn.close()

    known_encodings = []
    known_names = []
    known_cins = []

    for nom, prenom, cin, encoding_blob in rows:
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

    # Vérifier si une entrée pour ce cin et cette date existe déjà pour éviter les doublons
    c.execute("SELECT * FROM attendance WHERE cin = ? AND date = ?", (cin, date))
    exists = c.fetchone()
    if not exists:
        c.execute("INSERT INTO attendance (cin, date, time_in) VALUES (?, ?, ?)", (cin, date, time))
        conn.commit()
    conn.close()

def load_camera_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("Fichier de configuration caméra introuvable.")
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        ip = config.get("ip")
        username = config.get("username", "")
        password = config.get("password", "")
        if not ip:
            raise ValueError("Adresse IP non spécifiée dans le fichier de configuration.")
        # Attention aux caractères spéciaux dans username/password qui pourraient nécessiter un encodage URL
        return f"rtsp://{username}:{password}@{ip}:554/"

def run_recognition(cam_source, window, btn_start):
    create_tables()  # Assure que les tables sont là avant de lancer la détection
    known_encodings, known_names, known_cins = load_known_faces()

    video_capture = cv2.VideoCapture(cam_source)
    if not video_capture.isOpened():
        messagebox.showerror("Erreur", f"Impossible d’ouvrir la caméra : {cam_source}")
        btn_start.config(state='normal')
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

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

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow("Reconnaissance faciale", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    btn_start.config(state='normal')

def open_camera_window(master):
    window = tk.Toplevel(master)
    window.title("Choix de la caméra")
    window.geometry("420x220")
    window.configure(bg="#f2f2f2")
    window.resizable(False, False)

    tk.Label(window, text="🎥 Sélection de la caméra :", font=("Segoe UI", 13), bg="#f2f2f2").pack(pady=10)

    cam_choice = tk.StringVar(value="default")

    tk.Radiobutton(window, text="Caméra par défaut (PC)", variable=cam_choice, value="default", bg="#f2f2f2",
                   font=("Segoe UI", 11)).pack(anchor="w", padx=30)
    tk.Radiobutton(window, text="Caméra IP (via configuration enregistrée)", variable=cam_choice, value="ip", bg="#f2f2f2",
                   font=("Segoe UI", 11)).pack(anchor="w", padx=30)

    def start_recognition_gui():
        choice = cam_choice.get()
        if choice == "default":
            cam_source = 0
        elif choice == "ip":
            try:
                cam_source = load_camera_config()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                return
        else:
            messagebox.showerror("Erreur", "Choix de caméra invalide.")
            return

        btn_start.config(state='disabled')
        Thread(target=run_recognition, args=(cam_source, window, btn_start), daemon=True).start()

    btn_start = tk.Button(window, text="Démarrer la reconnaissance", command=start_recognition_gui,
                          bg="#4CAF50", fg="white", font=("Segoe UI", 12), width=30)
    btn_start.pack(pady=30)

    btn_return = tk.Button(window, text="← Retour au menu", command=window.destroy,
                           font=("Segoe UI", 11), bg="#6c757d", fg="white", padx=30, pady=10,
                           bd=0, relief="ridge", cursor="hand2")
    btn_return.pack(pady=5)

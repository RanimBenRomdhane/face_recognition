import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import cv2
import face_recognition
import pickle
import os
import shutil
from databse import create_tables  

create_tables() 


def insert_employee(nom, prenom, cin, img_path):
    try:
        image = face_recognition.load_image_file(img_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            messagebox.showerror("Erreur", "Aucun visage détecté dans l'image.")
            return

        os.makedirs("photos", exist_ok=True)
        saved_path = f"photos/{cin}.png"
        shutil.copy(img_path, saved_path)

        encoding_pickle = pickle.dumps(face_encodings[0])

        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute("INSERT INTO employees (nom, prenom, cin, encoding, image_path) VALUES (?, ?, ?, ?, ?)",
                  (nom, prenom, cin, encoding_pickle, saved_path))
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "✅ Employé ajouté avec succès.")

    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "❌ CIN déjà existant.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def choose_image():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers image", "*.png *.jpg *.jpeg")])
    image_path_var.set(file_path)

def submit_form():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    cin = entry_cin.get()
    img_path = image_path_var.get()

    if not (nom and prenom and cin and img_path):
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
        return

    insert_employee(nom, prenom, cin, img_path)

root = tk.Tk()
root.title("👤 Ajouter un employé")
root.geometry("500x250")
root.resizable(False, False)

tk.Label(root, text="Nom:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_nom = tk.Entry(root, width=30)
entry_nom.grid(row=0, column=1)

tk.Label(root, text="Prénom:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_prenom = tk.Entry(root, width=30)
entry_prenom.grid(row=1, column=1)

tk.Label(root, text="CIN:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_cin = tk.Entry(root, width=30)
entry_cin.grid(row=2, column=1)

tk.Label(root, text="Image:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
image_path_var = tk.StringVar()
tk.Entry(root, textvariable=image_path_var, width=30).grid(row=3, column=1)
tk.Button(root, text="Choisir une image", command=choose_image).grid(row=3, column=2, padx=5)

tk.Button(root, text="Ajouter l'employé", command=submit_form, bg="#4CAF50", fg="white").grid(row=4, column=1, pady=20)

root.mainloop()

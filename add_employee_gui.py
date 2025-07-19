import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import face_recognition
import pickle
import os
import shutil



def insert_employee(nom, prenom, cin, img_paths):
    if not img_paths:
        messagebox.showerror("Erreur", "Aucune image sélectionnée.")
        return

    conn = sqlite3.connect('employees.db')
    c = conn.cursor()

    try:
        # Ajouter l'employé
        c.execute("INSERT INTO employees (nom, prenom, cin) VALUES (?, ?, ?)", (nom, prenom, cin))

        # Créer dossier photos/CIN/
        img_dir = os.path.join("photos", cin)
        os.makedirs(img_dir, exist_ok=True)

        images_added = 0
        for i, img_path in enumerate(img_paths):
            image = face_recognition.load_image_file(img_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                messagebox.showwarning("Attention", f"Aucun visage détecté dans l'image {os.path.basename(img_path)}")
                continue

            encoding = pickle.dumps(face_encodings[0])
            ext = os.path.splitext(img_path)[1]
            dest_path = os.path.join(img_dir, f"{cin}_{i+1}{ext}")
            shutil.copy(img_path, dest_path)

            c.execute("INSERT INTO photos (cin, image_path, encoding) VALUES (?, ?, ?)", (cin, dest_path, encoding))
            images_added += 1

        if images_added == 0:
            messagebox.showerror("Erreur", "❌ Aucun visage détecté dans toutes les images.")
            conn.rollback()
            return

        conn.commit()
        messagebox.showinfo("Succès", f"Employé ajouté avec {images_added} photo(s).")

    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erreur", "❌ Le CIN existe déjà.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Erreur", f"Erreur : {str(e)}")
    finally:
        conn.close()

def choose_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    if file_paths:
        image_paths_var.set(";".join(file_paths))

def submit_form():
    nom = entry_nom.get().strip()
    prenom = entry_prenom.get().strip()
    cin = entry_cin.get().strip()
    img_paths_str = image_paths_var.get().strip()

    if not (nom and prenom and cin and img_paths_str):
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
        return

    img_paths = img_paths_str.split(";")
    insert_employee(nom, prenom, cin, img_paths)



# Interface Tkinter
root = tk.Tk()
root.title("👥 Ajouter un employé avec plusieurs photos")
root.geometry("600x300")
root.resizable(False, False)

tk.Label(root, text="Nom:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_nom = tk.Entry(root, width=40)
entry_nom.grid(row=0, column=1)

tk.Label(root, text="Prénom:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_prenom = tk.Entry(root, width=40)
entry_prenom.grid(row=1, column=1)

tk.Label(root, text="CIN:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_cin = tk.Entry(root, width=40)
entry_cin.grid(row=2, column=1)

tk.Label(root, text="Images:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
image_paths_var = tk.StringVar()
tk.Entry(root, textvariable=image_paths_var, width=40).grid(row=3, column=1)
tk.Button(root, text="Choisir des images", command=choose_images).grid(row=3, column=2, padx=5)

tk.Button(root, text="Ajouter l'employé", command=submit_form, bg="#4CAF50", fg="white").grid(row=4, column=1, pady=20)

root.mainloop()

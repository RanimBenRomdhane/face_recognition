import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import shutil
import pickle
import face_recognition
from db import create_tables

create_tables()

class AddEmployeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("👤 Ajouter un employé avec plusieurs photos")
        self.root.geometry("600x350")
        self.root.resizable(False, False)

        tk.Label(root, text="Nom:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_nom = tk.Entry(root, width=30)
        self.entry_nom.grid(row=0, column=1)

        tk.Label(root, text="Prénom:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_prenom = tk.Entry(root, width=30)
        self.entry_prenom.grid(row=1, column=1)

        tk.Label(root, text="CIN:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.entry_cin = tk.Entry(root, width=30)
        self.entry_cin.grid(row=2, column=1)

        self.photos_list = []
        self.photos_var = tk.StringVar(value=[])

        tk.Label(root, text="Photos:").grid(row=3, column=0, padx=10, pady=10, sticky="ne")
        self.photos_listbox = tk.Listbox(root, listvariable=self.photos_var, height=6, width=40)
        self.photos_listbox.grid(row=3, column=1, sticky="w")

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=3, column=2, padx=5, sticky="n")

        tk.Button(btn_frame, text="Ajouter photos", command=self.add_photos).pack(pady=2)
        tk.Button(btn_frame, text="Supprimer sélection", command=self.remove_selected).pack(pady=2)

        tk.Button(root, text="Ajouter l'employé", command=self.submit_form, bg="#4CAF50", fg="white").grid(row=4, column=1, pady=20)

    def add_photos(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if files:
            self.photos_list.extend(files)
            self.photos_var.set(self.photos_list)

    def remove_selected(self):
        selected = list(self.photos_listbox.curselection())
        if not selected:
            return
        for i in reversed(selected):
            del self.photos_list[i]
        self.photos_var.set(self.photos_list)

    def submit_form(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        cin = self.entry_cin.get().strip()
        photos = self.photos_list

        if not (nom and prenom and cin and photos):
            messagebox.showerror("Erreur", "Tous les champs et au moins une photo sont obligatoires.")
            return

        try:
            self.insert_employee_with_photos(nom, prenom, cin, photos)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def insert_employee_with_photos(self, nom, prenom, cin, list_img_paths):
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO employees (nom, prenom, cin) VALUES (?, ?, ?)", (nom, prenom, cin))
            employee_id = c.lastrowid

            os.makedirs("photos", exist_ok=True)

            for idx, img_path in enumerate(list_img_paths):
                image = face_recognition.load_image_file(img_path)
                face_encodings = face_recognition.face_encodings(image)
                if not face_encodings:
                    raise Exception(f"Aucun visage détecté dans l'image {img_path}")

                encoding_pickle = pickle.dumps(face_encodings[0])
                saved_path = f"photos/{cin}_{idx}.png"
                shutil.copy(img_path, saved_path)

                c.execute(
                    "INSERT INTO employee_photos (employee_id, photo_path, encoding) VALUES (?, ?, ?)",
                    (employee_id, saved_path, encoding_pickle)
                )

            conn.commit()
            messagebox.showinfo("Succès", "✅ Employé et photos ajoutés avec succès.")
            self.entry_nom.delete(0, tk.END)
            self.entry_prenom.delete(0, tk.END)
            self.entry_cin.delete(0, tk.END)
            self.photos_list = []
            self.photos_var.set([])

        except sqlite3.IntegrityError:
            conn.rollback()
            messagebox.showerror("Erreur", "❌ CIN déjà existant.")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AddEmployeeApp(root)
    root.mainloop()

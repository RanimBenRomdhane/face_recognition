import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import face_recognition
import pickle
import os
import shutil

DB_PATH = 'employees.db'

def insert_employee(nom, prenom, cin, img_paths, clear_form):
    if not img_paths:
        messagebox.showerror("Erreur", "Aucune image sélectionnée.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO employees (nom, prenom, cin) VALUES (?, ?, ?)", (nom, prenom, cin))
        img_dir = os.path.join("photos", cin)
        os.makedirs(img_dir, exist_ok=True)

        images_added = 0
        for i, img_path in enumerate(img_paths):
            image = face_recognition.load_image_file(img_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                messagebox.showwarning("⚠️ Avertissement", f"Aucun visage détecté dans : {os.path.basename(img_path)}")
                continue

            encoding = pickle.dumps(face_encodings[0])
            ext = os.path.splitext(img_path)[1]
            dest_path = os.path.join(img_dir, f"{cin}_{i+1}{ext}")
            shutil.copy(img_path, dest_path)

            c.execute("INSERT INTO photos (cin, image_path, encoding) VALUES (?, ?, ?)", (cin, dest_path, encoding))
            images_added += 1

        if images_added == 0:
            conn.rollback()
            messagebox.showerror("Erreur", "Aucun visage détecté dans les images sélectionnées.")
            return

        conn.commit()
        messagebox.showinfo("✅ Succès", f"Employé ajouté avec {images_added} photo(s).")
        clear_form()

    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erreur", "Le CIN existe déjà dans la base de données.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Erreur", f"Erreur inattendue : {str(e)}")
    finally:
        conn.close()


def open_add_employee_window(master):
    window = tk.Toplevel(master)
    window.title("➕ Ajouter un Employé")
    window.state("zoomed")
    window.configure(bg="#f1f3f6")

    tk.Label(
        window,
        text="👤 Ajouter un nouvel employé",
        font=("Segoe UI", 26, "bold"),
        bg="#f1f3f6",
        fg="#2c3e50"
    ).pack(pady=30)

    form_frame = tk.Frame(window, bg="white", bd=2, relief="groove")
    form_frame.pack(padx=300, pady=10, fill="both", expand=False)

    label_font = ("Segoe UI", 13)
    entry_font = ("Segoe UI", 12)

    def add_form_row(label, entry_widget, row):
        tk.Label(form_frame, text=label, font=label_font, bg="white").grid(row=row, column=0, sticky="e", pady=12, padx=(20, 10))
        entry_widget.grid(row=row, column=1, pady=12, padx=(0, 20), sticky="we")

    form_frame.columnconfigure(1, weight=1)

    entry_nom = tk.Entry(form_frame, font=entry_font)
    add_form_row("Nom :", entry_nom, 0)

    entry_prenom = tk.Entry(form_frame, font=entry_font)
    add_form_row("Prénom :", entry_prenom, 1)

    entry_cin = tk.Entry(form_frame, font=entry_font)
    add_form_row("CIN :", entry_cin, 2)

    image_paths_var = tk.StringVar()
    entry_images = tk.Entry(form_frame, textvariable=image_paths_var, font=entry_font)
    add_form_row("Images :", entry_images, 3)

    def choose_images():
        file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_paths:
            image_paths_var.set(";".join(file_paths))

    def clear_form():
        entry_nom.delete(0, tk.END)
        entry_prenom.delete(0, tk.END)
        entry_cin.delete(0, tk.END)
        image_paths_var.set("")

    def submit_form():
        nom = entry_nom.get().strip()
        prenom = entry_prenom.get().strip()
        cin = entry_cin.get().strip()
        img_paths_str = image_paths_var.get().strip()

        if not (nom and prenom and cin and img_paths_str):
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
            return

        img_paths = img_paths_str.split(";")
        insert_employee(nom, prenom, cin, img_paths, clear_form)

    tk.Button(
        form_frame,
        text="📂 Parcourir",
        command=choose_images,
        font=("Segoe UI", 11),
        bg="#007bff",
        fg="white",
        relief="flat",
        padx=12,
        pady=6,
        cursor="hand2"
    ).grid(row=3, column=2, padx=10)

    tk.Button(
        window,
        text="✅ Enregistrer l'employé",
        command=submit_form,
        font=("Segoe UI", 14, "bold"),
        bg="#28a745",
        fg="white",
        relief="flat",
        padx=20,
        pady=10,
        cursor="hand2"
    ).pack(pady=30)

    tk.Button(
        window,
        text="↩ Retour au menu",
        command=window.destroy,
        font=("Segoe UI", 12),
        bg="#6c757d",
        fg="white",
        relief="flat",
        padx=20,
        pady=8,
        cursor="hand2"
    ).pack(pady=10)

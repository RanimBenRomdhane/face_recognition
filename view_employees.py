import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import shutil
import os
import face_recognition
import pickle
import subprocess
from PIL import Image, ImageTk

DB_PATH = 'employees.db'

def open_view_employees_window(parent=None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("👥 Liste des employés")
    window.state('zoomed')
    window.configure(bg="#f8f9fa")

    # Variables globales locales pour le treeview et images
    # (nécessaires pour fonctions internes)
    tree = None

    # --- Création Widgets ---

    # Titre
    title_frame = tk.Frame(window, bg="#f8f9fa")
    title_frame.pack(pady=10)
    tk.Label(title_frame, text="👥 Liste des employés enregistrés",
             font=("Segoe UI", 20, "bold"), bg="#f8f9fa", fg="#333").pack()

    # Tableau + Scrollbar
    table_frame = tk.Frame(window, bg="white", bd=2, relief="groove")
    table_frame.pack(padx=20, pady=10, fill="both", expand=True)

    columns = ("ID", "Nom", "Prénom", "CIN")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=140)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    tree.pack(fill="both", expand=True)

    # --- Fonctions locales ---

    def load_employees():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT id, nom, prenom, cin FROM employees ORDER BY nom")
                rows = c.fetchall()

            for row in tree.get_children():
                tree.delete(row)

            for row in rows:
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les employés : {str(e)}")

    def delete_employee():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un employé à supprimer.")
            return

        values = tree.item(selected, 'values')
        emp_id, nom, prenom, cin = values

        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer l'employé {nom} {prenom} ?"):
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()

                    c.execute("SELECT image_path FROM photos WHERE cin = ?", (cin,))
                    photos = c.fetchall()
                    for (photo_path,) in photos:
                        if os.path.exists(photo_path):
                            os.remove(photo_path)
                    c.execute("DELETE FROM photos WHERE cin = ?", (cin,))

                    c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))

                dossier_emp = os.path.join("photos", cin)
                if os.path.exists(dossier_emp) and not os.listdir(dossier_emp):
                    os.rmdir(dossier_emp)

                load_employees()
                messagebox.showinfo("Succès", "Employé supprimé avec succès.")

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")

    def update_employee():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un employé à modifier.")
            return

        values = tree.item(selected, 'values')
        emp_id, nom, prenom, cin = values

        update_win = tk.Toplevel(window)
        update_win.title("Modifier l'employé")
        update_win.geometry("700x700")
        update_win.grab_set()

        tk.Label(update_win, text="Nom").pack(pady=(10, 0))
        entry_nom = tk.Entry(update_win)
        entry_nom.insert(0, nom)
        entry_nom.pack(pady=(0, 10), fill="x", padx=20)

        tk.Label(update_win, text="Prénom").pack(pady=(10, 0))
        entry_prenom = tk.Entry(update_win)
        entry_prenom.insert(0, prenom)
        entry_prenom.pack(pady=(0, 10), fill="x", padx=20)

        tk.Label(update_win, text="CIN").pack(pady=(10, 0))
        entry_cin = tk.Entry(update_win)
        entry_cin.insert(0, cin)
        entry_cin.pack(pady=(0, 10), fill="x", padx=20)

        photos_selected = []

        def browse_images():
            file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if file_paths:
                photos_selected.clear()
                photos_selected.extend(file_paths)
                label_photos.config(text=f"{len(photos_selected)} photo(s) sélectionnée(s)")

        tk.Button(update_win, text="📸 Ajouter / Changer photos", command=browse_images).pack(pady=5)
        label_photos = tk.Label(update_win, text="Aucune photo sélectionnée")
        label_photos.pack()

        frame_photos = tk.Frame(update_win)
        frame_photos.pack(pady=10, fill="both", expand=True)

        images_tk = []

        def refresh_photos():
            for widget in frame_photos.winfo_children():
                widget.destroy()
            images_tk.clear()

            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT id, image_path FROM photos WHERE cin = ?", (entry_cin.get(),))
                current_photos = c.fetchall()

            for i, (photo_id, img_path) in enumerate(current_photos):
                if not os.path.exists(img_path):
                    continue
                pil_img = Image.open(img_path)
                pil_img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(pil_img)
                images_tk.append(img_tk)

                frame = tk.Frame(frame_photos, bd=2, relief="groove")
                frame.grid(row=i // 4, column=i % 4, padx=5, pady=5)

                lbl_img = tk.Label(frame, image=img_tk)
                lbl_img.pack()

                def make_delete_func(pid=photo_id, path=img_path):
                    def delete_photo():
                        if messagebox.askyesno("Confirmation", "Supprimer cette photo ?"):
                            try:
                                with sqlite3.connect(DB_PATH) as conn:
                                    c = conn.cursor()
                                    c.execute("DELETE FROM photos WHERE id = ?", (pid,))
                                if os.path.exists(path):
                                    os.remove(path)
                                refresh_photos()
                            except Exception as e:
                                messagebox.showerror("Erreur", f"Erreur suppression photo : {str(e)}")
                    return delete_photo

                btn_del = tk.Button(frame, text="❌ Supprimer", fg="red", command=make_delete_func())
                btn_del.pack()

        refresh_photos()

        def save_changes():
            new_nom = entry_nom.get().strip()
            new_prenom = entry_prenom.get().strip()
            new_cin = entry_cin.get().strip()

            try:
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()
                    c.execute("""UPDATE employees SET nom = ?, prenom = ?, cin = ? WHERE id = ?""",
                              (new_nom, new_prenom, new_cin, emp_id))

                    if photos_selected:
                        dossier_emp = os.path.join("photos", new_cin)
                        os.makedirs(dossier_emp, exist_ok=True)

                        c.execute("SELECT COUNT(*) FROM photos WHERE cin = ?", (new_cin,))
                        count_existing = c.fetchone()[0]

                        for i, img_path in enumerate(photos_selected, start=count_existing + 1):
                            ext = os.path.splitext(img_path)[1]
                            new_filename = f"{new_cin}_{i}{ext}"
                            new_path = os.path.join(dossier_emp, new_filename)
                            shutil.copy(img_path, new_path)

                            image = face_recognition.load_image_file(new_path)
                            encodings = face_recognition.face_encodings(image)

                            if not encodings:
                                messagebox.showwarning("Avertissement", f"Aucun visage détecté dans {os.path.basename(new_path)}")
                                continue

                            encoding_pickle = pickle.dumps(encodings[0])

                            c.execute("INSERT INTO photos (cin, image_path, encoding) VALUES (?, ?, ?)",
                                      (new_cin, new_path, encoding_pickle))

                load_employees()
                messagebox.showinfo("Succès", "Employé mis à jour avec succès.")
                update_win.destroy()

            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "CIN déjà existant ou conflit de données.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la mise à jour : {str(e)}")

        tk.Button(update_win, text="💾 Enregistrer", command=save_changes,
                  bg="#007BFF", fg="white", font=("Segoe UI", 11)).pack(pady=20)

    def add_employee():
        try:
            subprocess.Popen(["python", "add_employee_gui.py"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer l'ajout d'employé.\n{e}")

    def return_to_menu():
        window.destroy()
        try:
            subprocess.Popen(["python", "main.py"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer le menu principal.\n{e}")

    # --- Boutons ---
    button_frame = tk.Frame(window, bg="#f8f9fa")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="➕ Ajouter", command=add_employee, bg="#007BFF", fg="white",
              width=15, font=("Segoe UI", 11), bd=0).grid(row=0, column=0, padx=10)

    tk.Button(button_frame, text="✏️ Modifier", command=update_employee, bg="#2196F3", fg="white",
              width=15, font=("Segoe UI", 11), bd=0).grid(row=0, column=1, padx=10)

    tk.Button(button_frame, text="🗑 Supprimer", command=delete_employee, bg="#f44336", fg="white",
              width=15, font=("Segoe UI", 11), bd=0).grid(row=0, column=2, padx=10)

    tk.Button(button_frame, text="🔄 Rafraîchir", command=load_employees, bg="#4CAF50", fg="white",
              width=15, font=("Segoe UI", 11), bd=0).grid(row=0, column=3, padx=10)

    # Bouton retour menu
    bottom_frame = tk.Frame(window, bg="#f8f9fa")
    bottom_frame.pack(pady=20)

    tk.Button(bottom_frame, text="← Retour au menu", command=return_to_menu,
              font=("Segoe UI", 11), bg="#6c757d", fg="white", padx=30, pady=10).pack()

    load_employees()

    if not parent:
        window.mainloop()

    return window


# --- Exemple d'utilisation dans un menu principal ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Menu Principal")
    root.geometry("400x200")

    tk.Label(root, text="Menu principal", font=("Segoe UI", 16)).pack(pady=20)

    def open_employees():
        open_view_employees_window(root)

    tk.Button(root, text="Ouvrir liste des employés", command=open_employees).pack()

    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import shutil
import os
import face_recognition
import pickle
from PIL import Image, ImageTk

DB_PATH = 'employees.db'

def load_employees():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, nom, prenom, cin FROM employees ORDER BY nom")
        rows = c.fetchall()
        conn.close()

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
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            # Supprimer les photos en base et fichiers
            c.execute("SELECT image_path FROM photos WHERE cin = ?", (cin,))
            photos = c.fetchall()
            for (photo_path,) in photos:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            c.execute("DELETE FROM photos WHERE cin = ?", (cin,))

            # Supprimer l'employé
            c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
            conn.commit()
            conn.close()

            # Supprimer le dossier photos/<cin> s’il existe et est vide
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

    update_win = tk.Toplevel(root)
    update_win.title("Modifier l'employé")
    update_win.geometry("700x700")

    tk.Label(update_win, text="Nom").pack()
    entry_nom = tk.Entry(update_win)
    entry_nom.insert(0, nom)
    entry_nom.pack()

    tk.Label(update_win, text="Prénom").pack()
    entry_prenom = tk.Entry(update_win)
    entry_prenom.insert(0, prenom)
    entry_prenom.pack()

    tk.Label(update_win, text="CIN").pack()
    entry_cin = tk.Entry(update_win)
    entry_cin.insert(0, cin)
    entry_cin.pack()

    photos_selected = []

    def browse_images():
        file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_paths:
            photos_selected.clear()
            photos_selected.extend(file_paths)
            label_photos.config(text=f"{len(photos_selected)} photo(s) sélectionnée(s)")

    tk.Button(update_win, text="Ajouter / Changer photos", command=browse_images).pack(pady=5)
    label_photos = tk.Label(update_win, text="Aucune photo sélectionnée")
    label_photos.pack()

    frame_photos = tk.Frame(update_win)
    frame_photos.pack(pady=10, fill="both", expand=True)

    images_tk = []

    def refresh_photos():
        for widget in frame_photos.winfo_children():
            widget.destroy()
        images_tk.clear()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, image_path FROM photos WHERE cin = ?", (entry_cin.get(),))
        current_photos = c.fetchall()
        conn.close()

        for i, (photo_id, img_path) in enumerate(current_photos):
            if not os.path.exists(img_path):
                continue
            pil_img = Image.open(img_path)
            pil_img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(pil_img)
            images_tk.append(img_tk)

            frame = tk.Frame(frame_photos, bd=2, relief="groove")
            frame.grid(row=i//4, column=i%4, padx=5, pady=5)

            lbl_img = tk.Label(frame, image=img_tk)
            lbl_img.pack()

            def make_delete_func(pid=photo_id, path=img_path):
                def delete_photo():
                    if messagebox.askyesno("Confirmation", "Supprimer cette photo ?"):
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("DELETE FROM photos WHERE id = ?", (pid,))
                            conn.commit()
                            conn.close()
                            if os.path.exists(path):
                                os.remove(path)
                            refresh_photos()
                        except Exception as e:
                            messagebox.showerror("Erreur", f"Erreur suppression photo : {str(e)}")
                return delete_photo

            btn_del = tk.Button(frame, text="Supprimer", fg="red", command=make_delete_func())
            btn_del.pack()

    refresh_photos()

    def save_changes():
        new_nom = entry_nom.get()
        new_prenom = entry_prenom.get()
        new_cin = entry_cin.get()

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("""
                UPDATE employees 
                SET nom = ?, prenom = ?, cin = ?
                WHERE id = ?
            """, (new_nom, new_prenom, new_cin, emp_id))

            if photos_selected:
                dossier_emp = os.path.join("photos", new_cin)
                os.makedirs(dossier_emp, exist_ok=True)

                c.execute("SELECT COUNT(*) FROM photos WHERE cin = ?", (new_cin,))
                count_existing = c.fetchone()[0]

                for i, img_path in enumerate(photos_selected, start=count_existing+1):
                    ext = os.path.splitext(img_path)[1]
                    new_filename = f"{new_cin}_{i}{ext}"
                    new_path = os.path.join(dossier_emp, new_filename)
                    shutil.copy(img_path, new_path)

                    image = face_recognition.load_image_file(new_path)
                    encodings = face_recognition.face_encodings(image)

                    if not encodings:
                        messagebox.showwarning("Avertissement", f"Aucun visage détecté dans : {os.path.basename(new_path)}")
                        continue

                    encoding_pickle = pickle.dumps(encodings[0])

                    c.execute("""
                        INSERT INTO photos (cin, image_path, encoding)
                        VALUES (?, ?, ?)
                    """, (new_cin, new_path, encoding_pickle))

            conn.commit()
            conn.close()
            load_employees()
            messagebox.showinfo("Succès", "Employé mis à jour avec succès.")
            update_win.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "CIN déjà existant ou conflit de données.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la mise à jour : {str(e)}")

    tk.Button(update_win, text="💾 Enregistrer", command=save_changes, bg="#2196F3", fg="white").pack(pady=10)

# Interface principale
root = tk.Tk()
root.title("👥 Liste des employés")
root.geometry("800x550")
root.resizable(False, False)

tk.Label(root, text="Liste des employés enregistrés", font=("Arial", 16, "bold")).pack(pady=10)

columns = ("ID", "Nom", "Prénom", "CIN")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)

tree.pack(expand=True, fill="both", padx=10, pady=10)

frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

tk.Button(frame_btn, text="🔄 Rafraîchir", command=load_employees, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=10)
tk.Button(frame_btn, text="✏️ Modifier", command=update_employee, bg="#2196F3", fg="white", width=15).grid(row=0, column=1, padx=10)
tk.Button(frame_btn, text="🗑 Supprimer", command=delete_employee, bg="#f44336", fg="white", width=15).grid(row=0, column=2, padx=10)

load_employees()
root.mainloop()

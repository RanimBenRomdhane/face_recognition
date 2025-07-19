import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import shutil
import os

def load_employees():
    try:
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute("SELECT id, nom, prenom, cin, image_path FROM employees ORDER BY nom")
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
    emp_id = values[0]

    if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer l'employé {values[1]} {values[2]} ?"):
        try:
            conn = sqlite3.connect('employees.db')
            c = conn.cursor()
            c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
            conn.commit()
            conn.close()
            load_employees()
            messagebox.showinfo("Succès", "Employé supprimé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la suppression : {str(e)}")

def update_employee():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Attention", "Veuillez sélectionner un employé à modifier.")
        return

    values = tree.item(selected, 'values')
    emp_id, nom, prenom, cin, image_path = values

    update_win = tk.Toplevel(root)
    update_win.title("Modifier l'employé")
    update_win.geometry("400x400")

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

    image_label = tk.Label(update_win, text=f"Image actuelle : {os.path.basename(image_path)}")
    image_label.pack()

    def browse_image():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            new_path = os.path.join("photos", os.path.basename(file_path))
            shutil.copy(file_path, new_path)
            image_label.config(text=f"Image sélectionnée : {os.path.basename(new_path)}")
            image_label.image_path = new_path

    tk.Button(update_win, text="Changer photo", command=browse_image).pack(pady=5)

    def save_changes():
        new_nom = entry_nom.get()
        new_prenom = entry_prenom.get()
        new_cin = entry_cin.get()
        new_image_path = getattr(image_label, "image_path", image_path)

        try:
            conn = sqlite3.connect('employees.db')
            c = conn.cursor()
            c.execute("""
                UPDATE employees 
                SET nom = ?, prenom = ?, cin = ?, image_path = ?
                WHERE id = ?
            """, (new_nom, new_prenom, new_cin, new_image_path, emp_id))
            conn.commit()
            conn.close()
            load_employees()
            messagebox.showinfo("Succès", "Employé mis à jour avec succès.")
            update_win.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la mise à jour : {str(e)}")

    tk.Button(update_win, text="💾 Enregistrer", command=save_changes, bg="#2196F3", fg="white").pack(pady=10)

# Interface principale
root = tk.Tk()
root.title("👥 Liste des employés")
root.geometry("800x500")
root.resizable(False, False)

tk.Label(root, text="Liste des employés enregistrés", font=("Arial", 16, "bold")).pack(pady=10)

columns = ("ID", "Nom", "Prénom", "CIN", "Image")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140 if col != "Image" else 200)

tree.pack(expand=True, fill="both", padx=10, pady=10)

frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

tk.Button(frame_btn, text="🔄 Rafraîchir", command=load_employees, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=10)
tk.Button(frame_btn, text="✏️ Modifier", command=update_employee, bg="#2196F3", fg="white", width=15).grid(row=0, column=1, padx=10)
tk.Button(frame_btn, text="🗑 Supprimer", command=delete_employee, bg="#f44336", fg="white", width=15).grid(row=0, column=2, padx=10)

load_employees()
root.mainloop()

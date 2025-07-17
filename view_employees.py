import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

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

root = tk.Tk()
root.title("👥 Liste des employés")
root.geometry("750x400")
root.resizable(False, False)

tk.Label(root, text="Liste des employés enregistrés", font=("Arial", 16, "bold")).pack(pady=10)

columns = ("ID", "Nom", "Prénom", "CIN", "Image")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140 if col != "Image" else 200)

tree.pack(expand=True, fill="both", padx=10, pady=10)

tk.Button(root, text="🔄 Rafraîchir", command=load_employees, bg="#4CAF50", fg="white").pack(pady=10)

load_employees()

root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def load_attendance():
    try:
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute("SELECT * FROM attendance ORDER BY date DESC, time_in DESC")
        rows = c.fetchall()
        conn.close()

        for row in tree.get_children():
            tree.delete(row)

        for row in rows:
            tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger les présences : {str(e)}")

root = tk.Tk()
root.title("🕒 Liste des présences")
root.geometry("700x400")
root.resizable(False, False)

tk.Label(root, text="Historique de présence", font=("Arial", 16, "bold")).pack(pady=10)

columns = ("ID", "CIN", "Date", "Heure d'entrée", "Heure de sortie")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150 if col in ("Heure d'entrée", "Heure de sortie") else 100)

tree.pack(expand=True, fill="both", padx=10, pady=10)

tk.Button(root, text="🔄 Rafraîchir", command=load_attendance, bg="#2196F3", fg="white").pack(pady=10)

load_attendance()

root.mainloop()

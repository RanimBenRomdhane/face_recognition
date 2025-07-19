import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess

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

def return_to_menu():
    root.destroy()  # ferme la fenêtre actuelle
    try:
        subprocess.Popen(["python", "main.py"])  # adapte le nom du script menu principal ici
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer le menu principal.\n{e}")

root = tk.Tk()
root.title("🕒 Liste des présences")

# Maximiser la fenêtre au lancement (Windows)
root.state('zoomed')  

root.configure(bg="#f8f9fa")
root.resizable(True, True)

# Titre principal
title_frame = tk.Frame(root, bg="#f8f9fa")
title_frame.pack(pady=10)

tk.Label(title_frame, text="📆 Historique de présence", 
         font=("Segoe UI", 20, "bold"), bg="#f8f9fa", fg="#333").pack()

# Frame tableau avec bordure
table_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
table_frame.pack(padx=20, pady=10, fill="both", expand=True)

columns = ("ID", "CIN", "Date", "Heure d'entrée")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150 if col == "Heure d'entrée" else 120)

tree.pack(fill="both", expand=True)

# Frame bouton rafraîchir
button_frame = tk.Frame(root, bg="#f8f9fa")
button_frame.pack(pady=10)

tk.Button(button_frame, text="🔄 Rafraîchir les données", command=load_attendance,
          font=("Segoe UI", 11), bg="#007BFF", fg="white", padx=20, pady=8, bd=0, relief="ridge", cursor="hand2").pack()

# Bouton retour au menu en bas, centré
bottom_frame = tk.Frame(root, bg="#f8f9fa")
bottom_frame.pack(pady=20)

btn_return = tk.Button(bottom_frame, text="← Retour au menu", command=return_to_menu,
                       font=("Segoe UI", 11), bg="#6c757d", fg="white", padx=30, pady=10,
                       bd=0, relief="ridge", cursor="hand2")
btn_return.pack()

# Chargement initial
load_attendance()

root.mainloop()

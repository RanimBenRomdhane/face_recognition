import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def open_script(script_name):
    root.destroy()  # Fermer le menu actuel
    script_path = os.path.join(os.getcwd(), script_name)
    os.system(f'python "{script_path}"')  # Ouvrir le script suivant

# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("🎯 Tableau de bord - Reconnaissance Faciale")
root.state('zoomed')  # Plein écran
root.configure(bg="#eef2f7")  # Couleur de fond douce

# Conteneur central
main_frame = tk.Frame(root, bg="#ffffff", bd=4, relief="ridge")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=600)

# Logo ou titre
logo = tk.Label(root, text="🤖 Reconnaissance Faciale", font=("Segoe UI", 20, "bold"), bg="#eef2f7", fg="#34495e")
logo.pack(pady=(20, 10))

# Titre
title = tk.Label(main_frame, text="📌 Menu Principal", font=("Segoe UI", 24, "bold"), bg="#ffffff", fg="#2c3e50")
title.pack(pady=(30, 10))

# Liste des fonctionnalités
buttons = [
    ("👁️  Lancer reconnaissance faciale", "recognize_camera.py"),
    ("➕  Ajouter un employé", "add_employee_gui.py"),
    ("📋  Voir les employés", "view_employees.py"),
    ("📆  Consulter les présences", "view_attendance.py"),
    ("📷  Configurer une caméra IP", "config_camera.py"),
]

# Fonction pour créer les boutons
def create_button(text, script, color="#3498db"):
    return tk.Button(
        main_frame,
        text=text,
        font=("Segoe UI", 13),
        width=40,
        pady=10,
        bg=color,
        fg="white",
        activebackground="#2980b9",
        relief="flat",
        command=lambda: open_script(script)
    )

# Création des boutons de fonctionnalité
for text, script in buttons:
    btn = create_button(text, script)
    btn.pack(pady=10)

# Bouton Quitter
quit_button = tk.Button(
    root,
    text="🚪 Quitter l'application",
    font=("Segoe UI", 12),
    bg="#e74c3c",
    fg="white",
    activebackground="#c0392b",
    relief="flat",
    padx=20,
    pady=10,
    command=root.quit
)
quit_button.pack(side="bottom", pady=20)

# Pied de page
footer = tk.Label(root, text="WIC-MIC", bg="#eef2f7", fg="#7f8c8d", font=("Segoe UI", 9))
footer.pack(side="bottom")

root.mainloop()

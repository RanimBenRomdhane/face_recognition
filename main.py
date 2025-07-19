import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
from add_employee_gui import open_add_employee_window 
from view_attendance import open_view_attendance_window
from view_employees import open_view_employees_window
from recognize_camera import open_camera_window
from config_camera import open_camera_config_window

def open_script(script_name):
    # Ouvre un autre script python dans un nouveau processus et ferme la fenêtre actuelle
    root.destroy()  # Fermer le menu actuel
    script_path = os.path.join(os.getcwd(), script_name)
    os.system(f'python "{script_path}"')

def open_window_or_script(target):
    if callable(target):
        # C'est une fonction : on l'appelle directement sans fermer root
        target()
    elif isinstance(target, str):
        # C'est un chemin vers un script
        open_script(target)
    else:
        messagebox.showerror("Erreur", "Commande non reconnue.")

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
    ("👁️  Lancer reconnaissance faciale", lambda: open_camera_window(root)),
    ("➕  Ajouter un employé", lambda: open_add_employee_window(root)),
    ("📋  Voir les employés", lambda: open_view_employees_window(root)),
    ("📆  Consulter les présences", lambda: open_view_attendance_window(root)),
    ("📷  Configurer une caméra IP", lambda: open_camera_config_window(root)),
]

# Fonction pour créer les boutons
def create_button(text, target, color="#3498db"):
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
        command=lambda: open_window_or_script(target)
    )

# Création des boutons de fonctionnalité
for text, target in buttons:
    btn = create_button(text, target)
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

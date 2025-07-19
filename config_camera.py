import tkinter as tk
from tkinter import messagebox
import json
import os

CONFIG_FILE = "camera_config.json"

def save_config():
    config = {
        "ip": ip_entry.get(),
        "username": username_entry.get(),
        "password": password_entry.get()
    }

    if not config["ip"]:
        messagebox.showwarning("Champ requis", "L'adresse IP est obligatoire.")
        return

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        messagebox.showinfo("Succès", "Configuration enregistrée avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'enregistrer : {e}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                ip_entry.insert(0, config.get("ip", ""))
                username_entry.insert(0, config.get("username", ""))
                password_entry.insert(0, config.get("password", ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger la configuration : {e}")

# Interface graphique
root = tk.Tk()
root.title("Configuration Caméra IP")
root.geometry("400x300")
root.configure(bg="#f0f2f5")

tk.Label(root, text="Adresse IP :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
ip_entry = tk.Entry(root, width=40, font=("Segoe UI", 11))
ip_entry.pack(pady=5)

tk.Label(root, text="Nom d'utilisateur :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
username_entry = tk.Entry(root, width=40, font=("Segoe UI", 11))
username_entry.pack(pady=5)

tk.Label(root, text="Mot de passe :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
password_entry = tk.Entry(root, width=40, show="*", font=("Segoe UI", 11))
password_entry.pack(pady=5)

tk.Button(root, text="💾 Enregistrer", command=save_config,
          font=("Segoe UI", 12), bg="#007bff", fg="white", width=20).pack(pady=20)

load_config()
root.mainloop()

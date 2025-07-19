import tkinter as tk
from tkinter import messagebox
import json
import os

CONFIG_FILE = "camera_config.json"

def open_camera_config_window(master):
    window = tk.Toplevel(master)
    window.title("Configuration Caméra IP")
    window.geometry("400x300")
    window.configure(bg="#f0f2f5")
    window.resizable(False, False)

    tk.Label(window, text="Adresse IP :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
    ip_entry = tk.Entry(window, width=40, font=("Segoe UI", 11))
    ip_entry.pack(pady=5)

    tk.Label(window, text="Nom d'utilisateur :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
    username_entry = tk.Entry(window, width=40, font=("Segoe UI", 11))
    username_entry.pack(pady=5)

    tk.Label(window, text="Mot de passe :", bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
    password_entry = tk.Entry(window, width=40, show="*", font=("Segoe UI", 11))
    password_entry.pack(pady=5)

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

    tk.Button(window, text="💾 Enregistrer", command=save_config,
              font=("Segoe UI", 12), bg="#007bff", fg="white", width=20).pack(pady=20)

    btn_return = tk.Button(window, text="← Retour au menu", command=window.destroy,
                           font=("Segoe UI", 11), bg="#6c757d", fg="white", padx=20, pady=8,
                           bd=0, relief="ridge", cursor="hand2")
    btn_return.pack(pady=5)

    load_config()


# Exemple d'utilisation autonome:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Menu principal")
    root.geometry("400x200")

    btn_open_config = tk.Button(root, text="Configurer caméra IP", 
                                command=lambda: open_camera_config_window(root),
                                bg="#007BFF", fg="white", font=("Segoe UI", 12), width=25)
    btn_open_config.pack(pady=50)

    root.mainloop()

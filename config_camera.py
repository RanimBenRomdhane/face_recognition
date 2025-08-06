import tkinter as tk
from tkinter import messagebox
import json
import os

CONFIG_FILE = "camera_config.json"

def open_camera_config_window(master, button=None):
    if button:
        button.config(state="disabled")

    window = tk.Toplevel(master)
    window.title("Configuration Caméra IP")
    window.geometry("400x450")
    window.configure(bg="#f0f2f5")
    window.resizable(False, False)

    window.transient(master)
    window.grab_set()  
    window.focus_set()

    def on_close():
        if button:
            button.config(state="normal")
        window.grab_release()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    labels_and_entries = [
        ("Adresse IP :", "ip_entry"),
        ("Port :", "port_entry"),
        ("Chemin (ex: /video) :", "path_entry"),
        ("Nom d'utilisateur :", "username_entry"),
        ("Mot de passe :", "password_entry", "*"),
    ]

    entries = {}

    for label, var_name, *show in labels_and_entries:
        tk.Label(window, text=label, bg="#f0f2f5", font=("Segoe UI", 12)).pack(pady=5)
        entry = tk.Entry(window, width=40, font=("Segoe UI", 11), show=show[0] if show else None)
        entry.pack(pady=5)
        entries[var_name] = entry

    def save_config():
        config = {
            "ip": entries["ip_entry"].get(),
            "port": entries["port_entry"].get(),
            "path": entries["path_entry"].get(),
            "username": entries["username_entry"].get(),
            "password": entries["password_entry"].get()
        }

        if not config["ip"]:
            messagebox.showwarning("Champ requis", "L'adresse IP est obligatoire.")
            return

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Succès", "Configuration enregistrée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")

    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    entries["ip_entry"].insert(0, config.get("ip", ""))
                    entries["port_entry"].insert(0, config.get("port", ""))
                    entries["path_entry"].insert(0, config.get("path", ""))
                    entries["username_entry"].insert(0, config.get("username", ""))
                    entries["password_entry"].insert(0, config.get("password", ""))
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de chargement : {e}")

    tk.Button(window, text="💾 Enregistrer", command=save_config,
              font=("Segoe UI", 12), bg="#007bff", fg="white", width=20).pack(pady=20)

    btn_return = tk.Button(window, text="← Fermer", command=on_close,
                           font=("Segoe UI", 11), bg="#6c757d", fg="white", padx=10, pady=2,
                           bd=0, relief="ridge", cursor="hand2")
    btn_return.pack(pady=1)

    load_config()

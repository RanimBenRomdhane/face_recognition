import sqlite3
import pickle

# Connexion à la base de données
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

# Requête pour récupérer les noms, prénoms et encodages depuis la base
cursor.execute("""
    SELECT e.nom, e.prenom, ep.encoding
    FROM employees e
    JOIN employee_photos ep ON e.id = ep.employee_id
""")
rows = cursor.fetchall()

# Listes pour les encodages et noms
known_encodings = []
known_names = []

# Parcours des résultats
for nom, prenom, encoding_blob in rows:
    try:
        encoding = pickle.loads(encoding_blob)
        known_encodings.append(encoding)
        known_names.append(f"{nom} {prenom}")
    except Exception as e:
        print(f"Erreur lors du décodage d'un encodage pour {nom} {prenom} :", e)

# Dictionnaire à enregistrer
data = {"encodings": known_encodings, "names": known_names}

# Sauvegarde dans le fichier encodings.pickle
with open("encodings.pickle", "wb") as f:
    pickle.dump(data, f)

print("✅ Fichier 'encodings.pickle' généré avec succès.")
conn.close()

import os
import shutil

TEMP_PHOTO_DIR = "temp_photos"

def clear_temp_photos():
    if os.path.exists(TEMP_PHOTO_DIR):
        for filename in os.listdir(TEMP_PHOTO_DIR):
            file_path = os.path.join(TEMP_PHOTO_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # supprime le fichier ou le lien symbolique
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # supprime un dossier s'il y en a
            except Exception as e:
                print(f"Erreur lors de la suppression de {file_path} : {e}")
        print(f"Le dossier '{TEMP_PHOTO_DIR}' a été vidé.")
    else:
        print(f"Le dossier '{TEMP_PHOTO_DIR}' n'existe pas.")

if __name__ == "__main__":
    clear_temp_photos()

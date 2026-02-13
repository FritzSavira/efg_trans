import os
from huggingface_hub import hf_hub_download

# ---------------- KONFIGURATION ----------------
# Wir nutzen das Repository von "bartowski", da es sehr zuverlässig ist.
repo_id = "bartowski/Qwen2.5-7B-Instruct-GGUF"

# WICHTIG: Der Dateiname muss exakt stimmen (Groß-/Kleinschreibung!)
filename = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"

# Ihr Zielverzeichnis
local_dir = "C:/Users/Fried/OneDrive/Dokumente/PycharmProjects_sync/efg_trans/models"
# -----------------------------------------------

# Verzeichnis erstellen, falls nötig
if not os.path.exists(local_dir):
    os.makedirs(local_dir)
    print(f"Zielverzeichnis erstellt: {local_dir}")

print(f"Starte Download von '{filename}' aus '{repo_id}'...")
print(f"Ziel: {local_dir}\n")

try:
    # Der Download
    file_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir
        # 'local_dir_use_symlinks' wurde entfernt, da nicht mehr benötigt
    )
    print("-" * 50)
    print(f"ERFOLG! Datei erfolgreich heruntergeladen:")
    print(f"{file_path}")
    print("-" * 50)

except Exception as e:
    print("\nFEHLER beim Download:")
    print("-" * 50)
    print(e)
    print("-" * 50)
    print("Möglicher Grund: Dateiname falsch geschrieben oder Internetverbindung unterbrochen.")

#!/usr/bin/env python3
"""
Script de lancement rapide pour REMOTE
Usage: python start.py
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Lance le serveur de développement"""
    
    project_root = Path(__file__).parent
    scripts_dir = project_root / "scripts"
    dev_server_script = scripts_dir / "dev_server.py"
    
    if not dev_server_script.exists():
        print("❌ Script dev_server.py non trouvé")
        print("Assurez-vous d'être dans le répertoire racine du projet")
        sys.exit(1)
    
    # Lancer le serveur de développement
    try:
        subprocess.run([sys.executable, str(dev_server_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé par l'utilisateur")
        sys.exit(0)

if __name__ == "__main__":
    main()

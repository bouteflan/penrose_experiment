"""
Script de lancement principal pour REMOTE Backend
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire de l'application au path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import start_server
from app.config import settings
from app.utils.logging import setup_dev_logging, setup_prod_logging


def main():
    """
    Point d'entrée principal de l'application
    """
    print("🎮 REMOTE - Thriller Psychologique")
    print("=" * 50)
    
    # Configuration du logging selon l'environnement
    if settings.environment == "production":
        setup_prod_logging()
        print("📊 Logging configuré pour la production")
    else:
        setup_dev_logging()
        print("🔧 Logging configuré pour le développement")
    
    # Vérifications préalables
    print("\n🔍 Vérifications préalables...")
    
    # Vérifier la clé OpenAI
    if not settings.openai_api_key:
        print("⚠️  ATTENTION: Clé API OpenAI non configurée")
        print("   Le jeu fonctionnera en mode dégradé sans Tom IA")
        print("   Ajoutez OPENAI_API_KEY dans votre fichier .env")
    else:
        print("✅ Clé OpenAI configurée")
    
    # Vérifier le dossier de base de données
    db_dir = Path("database")
    if not db_dir.exists():
        print(f"📁 Création du dossier database: {db_dir.absolute()}")
        db_dir.mkdir(parents=True, exist_ok=True)
    else:
        print("✅ Dossier database présent")
    
    # Vérifier les dossiers de logs
    if settings.environment == "production":
        log_dir = Path("logs")
        if not log_dir.exists():
            print(f"📁 Création du dossier logs: {log_dir.absolute()}")
            log_dir.mkdir(parents=True, exist_ok=True)
        else:
            print("✅ Dossier logs présent")
    
    print("\n🚀 Démarrage du serveur...")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🔧 Debug: {settings.debug}")
    print(f"🤖 Condition Tom: {settings.tom_personality_condition}")
    print(f"📊 Collecte données: {settings.collect_experiment_data}")
    
    # Démarrer le serveur
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
        print("👋 À bientôt !")
    except Exception as e:
        print(f"\n❌ Erreur de démarrage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

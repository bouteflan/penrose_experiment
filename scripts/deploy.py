"""
Script de déploiement pour REMOTE
Prépare l'application pour la production
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime


class RemoteDeployer:
    """Déployeur pour REMOTE"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.deploy_dir = self.project_root / "deploy"
        self.version = self._get_version()
    
    def _get_version(self):
        """Récupère la version du projet"""
        try:
            with open(self.frontend_dir / "package.json") as f:
                package_json = json.load(f)
                return package_json.get("version", "1.0.0")
        except:
            return "1.0.0"
    
    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 60)
        print("🚀 REMOTE - Déploiement Production")
        print(f"   Version: {self.version}")
        print("=" * 60)
        print()
    
    def clean_deploy_directory(self):
        """Nettoie le répertoire de déploiement"""
        print("🧹 Nettoyage du répertoire de déploiement...")
        
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        
        self.deploy_dir.mkdir(parents=True)
        print("✅ Répertoire de déploiement nettoyé")
    
    def build_frontend(self):
        """Build le frontend pour la production"""
        print("⚛️ Build du frontend React...")
        
        os.chdir(self.frontend_dir)
        
        # Installer les dépendances si nécessaire
        if not (self.frontend_dir / "node_modules").exists():
            print("   Installation des dépendances...")
            result = subprocess.run(["npm", "install"])
            if result.returncode != 0:
                print("❌ Erreur installation dépendances frontend")
                return False
        
        # Build de production
        print("   Build de production...")
        result = subprocess.run(["npm", "run", "build"])
        if result.returncode != 0:
            print("❌ Erreur build frontend")
            return False
        
        # Vérifier que le build existe
        dist_dir = self.frontend_dir / "dist"
        if not dist_dir.exists():
            print("❌ Dossier dist non créé")
            return False
        
        print("✅ Frontend buildé avec succès")
        return True
    
    def prepare_backend(self):
        """Prépare le backend pour la production"""
        print("🐍 Préparation du backend...")
        
        backend_deploy = self.deploy_dir / "backend"
        backend_deploy.mkdir(parents=True)
        
        # Copier les fichiers source
        print("   Copie des fichiers source...")
        
        # Copier le code
        shutil.copytree(
            self.backend_dir / "app",
            backend_deploy / "app"
        )
        
        # Copier les fichiers de configuration
        files_to_copy = [
            "requirements.txt",
            "run.py",
            ".env.example"
        ]
        
        for file_name in files_to_copy:
            src = self.backend_dir / file_name
            if src.exists():
                shutil.copy(src, backend_deploy / file_name)
        
        # Copier les données
        shutil.copytree(
            self.project_root / "data",
            backend_deploy / "data"
        )
        
        print("✅ Backend préparé")
        return True
    
    def prepare_frontend(self):
        """Prépare le frontend pour la production"""
        print("📦 Préparation du frontend...")
        
        frontend_deploy = self.deploy_dir / "frontend"
        frontend_deploy.mkdir(parents=True)
        
        # Copier le build
        dist_src = self.frontend_dir / "dist"
        if not dist_src.exists():
            print("❌ Build frontend non trouvé")
            return False
        
        shutil.copytree(dist_src, frontend_deploy / "dist")
        
        # Copier package.json pour info
        shutil.copy(
            self.frontend_dir / "package.json",
            frontend_deploy / "package.json"
        )
        
        print("✅ Frontend préparé")
        return True
    
    def create_deployment_scripts(self):
        """Crée les scripts de déploiement"""
        print("📝 Création des scripts de déploiement...")
        
        # Script de démarrage backend
        start_script = '''#!/bin/bash
# Script de démarrage pour REMOTE Backend

echo "🎮 Démarrage REMOTE Backend..."

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer les dossiers nécessaires
mkdir -p database logs

# Initialiser la base de données
python -c "
import sys
sys.path.insert(0, '.')
from app.database import create_tables
create_tables()
print('Base de données initialisée')
"

# Démarrer le serveur
echo "Démarrage du serveur sur le port 8000..."
python run.py
'''
        
        with open(self.deploy_dir / "start_backend.sh", "w") as f:
            f.write(start_script)
        
        # Script Windows
        start_script_win = '''@echo off
REM Script de démarrage pour REMOTE Backend (Windows)

echo 🎮 Démarrage REMOTE Backend...

REM Créer l'environnement virtuel
python -m venv venv
call venv\\Scripts\\activate.bat

REM Installer les dépendances
pip install -r requirements.txt

REM Créer les dossiers nécessaires
if not exist "database" mkdir database
if not exist "logs" mkdir logs

REM Initialiser la base de données
python -c "import sys; sys.path.insert(0, '.'); from app.database import create_tables; create_tables(); print('Base de données initialisée')"

REM Démarrer le serveur
echo Démarrage du serveur sur le port 8000...
python run.py

pause
'''
        
        with open(self.deploy_dir / "start_backend.bat", "w") as f:
            f.write(start_script_win)
        
        # Rendre les scripts exécutables
        try:
            os.chmod(self.deploy_dir / "start_backend.sh", 0o755)
        except:
            pass  # Peut échouer sur Windows
        
        print("✅ Scripts de déploiement créés")
        return True
    
    def create_production_config(self):
        """Crée la configuration de production"""
        print("⚙️ Création de la configuration de production...")
        
        prod_env = '''# Configuration de production pour REMOTE
# IMPORTANT: Configurez ces valeurs avant le déploiement

# Configuration de base
APP_NAME="REMOTE Psychological Thriller Game"
ENVIRONMENT=production
DEBUG=false

# Configuration serveur
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Configuration base de données
DATABASE_URL=sqlite:///./database/game_production.db

# Configuration OpenAI (OBLIGATOIRE)
OPENAI_API_KEY=your_production_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Configuration sécurité (CHANGEZ CES VALEURS)
SECRET_KEY=your-very-secret-production-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration expérimentale
COLLECT_EXPERIMENT_DATA=true
ANONYMIZE_DATA=true

# Configuration Tom AI
TOM_PERSONALITY_CONDITION=confident
TOM_RESPONSE_DELAY_MIN=0.5
TOM_RESPONSE_DELAY_MAX=2.0
TOM_TYPING_SPEED=0.05

# Configuration du jeu
GAME_DURATION_MINUTES=10
CORRUPTION_INTENSITY_MAX=1.0
BIAS_MEASUREMENT_INTERVAL=5

# Configuration CORS (ajustez selon votre domaine)
ALLOWED_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]

# Configuration WebSocket
WEBSOCKET_PING_INTERVAL=20
WEBSOCKET_PING_TIMEOUT=10
'''
        
        with open(self.deploy_dir / "backend" / ".env.production", "w") as f:
            f.write(prod_env)
        
        print("✅ Configuration de production créée")
        return True
    
    def create_documentation(self):
        """Crée la documentation de déploiement"""
        print("📚 Création de la documentation...")
        
        docs_dir = self.deploy_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        deployment_guide = f'''# Guide de Déploiement REMOTE v{self.version}

## Prérequis

- Python 3.9+
- Node.js 18+ (pour build frontend)
- Clé API OpenAI
- Serveur avec accès Internet

## Installation

### 1. Décompression

```bash
tar -xzf remote-v{self.version}.tar.gz
cd remote-v{self.version}
```

### 2. Configuration Backend

```bash
cd backend
cp .env.production .env
```

**IMPORTANT:** Éditez le fichier `.env` et configurez :
- `OPENAI_API_KEY` : Votre clé API OpenAI
- `SECRET_KEY` : Une clé secrète unique pour votre déploiement
- `ALLOWED_ORIGINS` : Les domaines autorisés pour CORS

### 3. Démarrage

#### Linux/Mac :
```bash
chmod +x start_backend.sh
./start_backend.sh
```

#### Windows :
```cmd
start_backend.bat
```

### 4. Serveur Frontend (Optionnel)

Si vous voulez servir le frontend séparément :

```bash
cd frontend
# Servir avec un serveur web statique
python -m http.server 3000 -d dist
# ou
npx serve dist -p 3000
```

## Configuration Nginx (Recommandé)

```nginx
server {{
    listen 80;
    server_name your-domain.com;
    
    # Frontend statique
    location / {{
        root /path/to/remote/frontend/dist;
        try_files $uri $uri/ /index.html;
    }}
    
    # API Backend
    location /api {{
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
    
    # WebSocket
    location /ws {{
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
```

## Surveillance

### Logs
- Backend : `backend/logs/remote_YYYYMMDD.log`
- Vérifiez régulièrement les erreurs

### Base de données
- Fichier : `backend/database/game_production.db`
- Sauvegardez régulièrement

### Monitoring
- Health check : `http://your-domain.com/health`
- API docs : `http://your-domain.com/docs`

## Sécurité

1. Changez `SECRET_KEY` en production
2. Utilisez HTTPS en production  
3. Limitez l'accès à la base de données
4. Surveillez les logs d'erreur
5. Mettez à jour régulièrement les dépendances

## Support

Pour obtenir de l'aide :
1. Vérifiez les logs d'erreur
2. Consultez la documentation API : `/docs`
3. Vérifiez la configuration `.env`

Version: {self.version}
Date de build: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
        
        with open(docs_dir / "DEPLOYMENT.md", "w") as f:
            f.write(deployment_guide)
        
        print("✅ Documentation créée")
        return True
    
    def create_package(self):
        """Crée le package de déploiement"""
        print("📦 Création du package de déploiement...")
        
        package_name = f"remote-v{self.version}"
        
        # Créer l'archive
        os.chdir(self.project_root)
        
        shutil.make_archive(
            package_name,
            'zip',
            self.deploy_dir
        )
        
        package_path = self.project_root / f"{package_name}.zip"
        package_size = package_path.stat().st_size / (1024 * 1024)  # MB
        
        print(f"✅ Package créé: {package_name}.zip ({package_size:.1f} MB)")
        return True
    
    def run(self):
        """Lance le processus de déploiement"""
        self.print_header()
        
        steps = [
            ("Nettoyage du répertoire de déploiement", self.clean_deploy_directory),
            ("Build du frontend", self.build_frontend),
            ("Préparation du backend", self.prepare_backend), 
            ("Préparation du frontend", self.prepare_frontend),
            ("Création des scripts de déploiement", self.create_deployment_scripts),
            ("Création de la configuration de production", self.create_production_config),
            ("Création de la documentation", self.create_documentation),
            ("Création du package", self.create_package)
        ]
        
        success_count = 0
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                if step_func():
                    success_count += 1
                else:
                    print(f"❌ Échec: {step_name}")
                    break
            except Exception as e:
                print(f"❌ Erreur lors de {step_name}: {e}")
                break
        
        # Résultats
        print("\n" + "=" * 60)
        if success_count == len(steps):
            print("🎉 Déploiement préparé avec succès !")
            print(f"📦 Package: remote-v{self.version}.zip")
            print(f"📁 Dossier: {self.deploy_dir}")
            print("\n📚 Consultez deploy/docs/DEPLOYMENT.md pour les instructions")
        else:
            print(f"⚠️ Déploiement partiel: {success_count}/{len(steps)} étapes réussies")
        
        print("=" * 60)
        return success_count == len(steps)


def main():
    """Point d'entrée principal"""
    deployer = RemoteDeployer()
    success = deployer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

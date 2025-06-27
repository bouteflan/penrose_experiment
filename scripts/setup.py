"""
Script d'installation et de configuration pour REMOTE
Automatise l'installation des dépendances et la configuration initiale
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import json


class RemoteInstaller:
    """Installateur pour le projet REMOTE"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.success_count = 0
        self.total_steps = 10
    
    def print_header(self):
        """Affiche l'en-tête du script"""
        print("=" * 60)
        print("🎮 REMOTE - Script d'Installation")
        print("   Thriller Psychologique avec IA")
        print("=" * 60)
        print()
    
    def check_prerequisites(self):
        """Vérifie les prérequis système"""
        print("🔍 Vérification des prérequis...")
        
        # Vérifier Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or python_version.minor < 9:
                print("❌ Python 3.9+ requis")
                return False
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        except Exception as e:
            print(f"❌ Erreur Python: {e}")
            return False
        
        # Vérifier Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"✅ Node.js {node_version}")
            else:
                print("❌ Node.js non trouvé - Installez Node.js 18+")
                return False
        except FileNotFoundError:
            print("❌ Node.js non trouvé - Installez Node.js 18+")
            return False
        
        # Vérifier npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"✅ npm {npm_version}")
            else:
                print("❌ npm non trouvé")
                return False
        except FileNotFoundError:
            print("❌ npm non trouvé")
            return False
        
        self.success_count += 1
        return True
    
    def create_directories(self):
        """Crée les dossiers nécessaires"""
        print("\n📁 Création des dossiers...")
        
        directories = [
            self.project_root / "database",
            self.project_root / "logs",
            self.backend_dir / "app" / "static",
            self.frontend_dir / "dist"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   📁 {directory.relative_to(self.project_root)}")
        
        self.success_count += 1
        print("✅ Dossiers créés")
    
    def setup_backend_environment(self):
        """Configure l'environnement backend Python"""
        print("\n🐍 Configuration de l'environnement Python...")
        
        os.chdir(self.backend_dir)
        
        # Créer l'environnement virtuel
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print("   Création de l'environnement virtuel...")
            result = subprocess.run([sys.executable, "-m", "venv", "venv"])
            if result.returncode != 0:
                print("❌ Erreur création environnement virtuel")
                return False
        
        # Déterminer le chemin de l'exécutable Python dans le venv
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Installer les dépendances
        print("   Installation des dépendances Python...")
        result = subprocess.run([
            str(pip_exe), "install", "-r", "requirements.txt"
        ])
        if result.returncode != 0:
            print("❌ Erreur installation dépendances Python")
            return False
        
        self.success_count += 1
        print("✅ Environnement Python configuré")
        return True
    
    def setup_frontend_environment(self):
        """Configure l'environnement frontend Node.js"""
        print("\n📦 Configuration de l'environnement Node.js...")
        
        os.chdir(self.frontend_dir)
        
        # Installer les dépendances
        print("   Installation des dépendances Node.js...")
        result = subprocess.run(["npm", "install"])
        if result.returncode != 0:
            print("❌ Erreur installation dépendances Node.js")
            return False
        
        self.success_count += 1
        print("✅ Environnement Node.js configuré")
        return True
    
    def create_env_file(self):
        """Crée le fichier .env à partir du template"""
        print("\n⚙️ Configuration du fichier .env...")
        
        env_example = self.backend_dir / ".env.example"
        env_file = self.backend_dir / ".env"
        
        if env_example.exists() and not env_file.exists():
            shutil.copy(env_example, env_file)
            print("   📝 Fichier .env créé depuis .env.example")
            print("   ⚠️  IMPORTANT: Configurez votre clé API OpenAI dans .env")
            print("   ⚠️  Changez SECRET_KEY en production")
        elif env_file.exists():
            print("   ✅ Fichier .env existe déjà")
        else:
            print("   ❌ Template .env.example non trouvé")
            return False
        
        self.success_count += 1
        return True
    
    def initialize_database(self):
        """Initialise la base de données"""
        print("\n🗄️ Initialisation de la base de données...")
        
        os.chdir(self.backend_dir)
        
        # Utiliser Python dans le venv pour initialiser la DB
        venv_path = self.backend_dir / "venv"
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/Mac
            python_exe = venv_path / "bin" / "python"
        
        # Script d'initialisation simple
        init_script = '''
import sys
sys.path.insert(0, ".")
from app.database import create_tables
try:
    create_tables()
    print("✅ Base de données initialisée")
except Exception as e:
    print(f"❌ Erreur initialisation DB: {e}")
    sys.exit(1)
'''
        
        result = subprocess.run([
            str(python_exe), "-c", init_script
        ])
        
        if result.returncode == 0:
            self.success_count += 1
            return True
        else:
            print("❌ Erreur initialisation base de données")
            return False
    
    def verify_installation(self):
        """Vérifie que l'installation est correcte"""
        print("\n✅ Vérification de l'installation...")
        
        # Vérifier les fichiers critiques
        critical_files = [
            self.backend_dir / "app" / "main.py",
            self.backend_dir / ".env",
            self.frontend_dir / "package.json",
            self.project_root / "database",
        ]
        
        all_good = True
        for file_path in critical_files:
            if file_path.exists():
                print(f"   ✅ {file_path.relative_to(self.project_root)}")
            else:
                print(f"   ❌ {file_path.relative_to(self.project_root)} manquant")
                all_good = False
        
        if all_good:
            self.success_count += 1
            return True
        return False
    
    def show_next_steps(self):
        """Affiche les prochaines étapes"""
        print("\n🎯 Prochaines étapes:")
        print()
        print("1. Configurez votre clé API OpenAI dans backend/.env :")
        print("   OPENAI_API_KEY=votre_clé_ici")
        print()
        print("2. Lancez le backend :")
        print("   cd backend")
        print("   venv\\Scripts\\activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   python run.py")
        print()
        print("3. Dans un autre terminal, lancez le frontend :")
        print("   cd frontend")
        print("   npm run dev")
        print()
        print("4. Ouvrez http://localhost:5173 dans votre navigateur")
        print()
        print("📚 Documentation complète dans docs/")
        print()
    
    def run(self):
        """Lance l'installation complète"""
        self.print_header()
        
        steps = [
            ("Vérification des prérequis", self.check_prerequisites),
            ("Création des dossiers", self.create_directories),
            ("Configuration environnement Python", self.setup_backend_environment),
            ("Configuration environnement Node.js", self.setup_frontend_environment),
            ("Configuration fichier .env", self.create_env_file),
            ("Initialisation base de données", self.initialize_database),
            ("Vérification installation", self.verify_installation)
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ Échec: {step_name}")
                    print("Installation interrompue.")
                    return False
            except Exception as e:
                print(f"\n❌ Erreur lors de {step_name}: {e}")
                return False
        
        # Résultats
        print("\n" + "=" * 60)
        if self.success_count == len(steps):
            print("🎉 Installation terminée avec succès !")
            print(f"✅ {self.success_count}/{len(steps)} étapes réussies")
            self.show_next_steps()
        else:
            print(f"⚠️ Installation partielle: {self.success_count}/{len(steps)} étapes réussies")
            print("Vérifiez les erreurs ci-dessus et relancez le script.")
        
        print("=" * 60)
        return self.success_count == len(steps)


def main():
    """Point d'entrée principal"""
    installer = RemoteInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

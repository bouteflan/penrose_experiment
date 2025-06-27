"""
Script de serveur de développement pour REMOTE
Lance automatiquement le backend et le frontend en parallèle
"""
import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path
import psutil


class DevServer:
    """Serveur de développement pour REMOTE"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.running = True
    
    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 60)
        print("🎮 REMOTE - Serveur de Développement")
        print("   Backend FastAPI + Frontend React")
        print("=" * 60)
        print()
    
    def check_ports(self):
        """Vérifie que les ports sont disponibles"""
        print("🔍 Vérification des ports...")
        
        ports_to_check = [8000, 5173]  # Backend et Frontend
        busy_ports = []
        
        for port in ports_to_check:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    busy_ports.append(port)
                    break
        
        if busy_ports:
            print(f"⚠️  Ports occupés: {busy_ports}")
            print("   Arrêtez les processus utilisant ces ports ou changez la configuration")
            return False
        
        print("✅ Ports 8000 et 5173 disponibles")
        return True
    
    def start_backend(self):
        """Lance le serveur backend FastAPI"""
        print("🐍 Démarrage du backend FastAPI...")
        
        os.chdir(self.backend_dir)
        
        # Utiliser Python dans le venv
        venv_path = self.backend_dir / "venv"
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/Mac  
            python_exe = venv_path / "bin" / "python"
        
        if not python_exe.exists():
            print("❌ Environnement virtuel Python non trouvé")
            print("   Lancez d'abord: python scripts/setup.py")
            return False
        
        try:
            self.backend_process = subprocess.Popen(
                [str(python_exe), "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                shell=True  # <--- AJOUTEZ CETTE LIGNE
            )
            
            # Thread pour afficher les logs backend
            threading.Thread(
                target=self._log_output,
                args=(self.backend_process, "🐍 BACKEND"),
                daemon=True
            ).start()
            
            print("✅ Backend FastAPI démarré (port 8000)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage backend: {e}")
            return False
    
    def start_frontend(self):
        """Lance le serveur frontend React"""
        print("⚛️  Démarrage du frontend React...")
        
        os.chdir(self.frontend_dir)
        
        # Vérifier que node_modules existe
        if not (self.frontend_dir / "node_modules").exists():
            print("❌ node_modules non trouvé")
            print("   Lancez d'abord: npm install")
            return False
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Thread pour afficher les logs frontend
            threading.Thread(
                target=self._log_output,
                args=(self.frontend_process, "⚛️  FRONTEND"),
                daemon=True
            ).start()
            
            print("✅ Frontend React démarré (port 5173)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage frontend: {e}")
            return False
    
    def _log_output(self, process, prefix):
        """Affiche les logs d'un processus avec un préfixe"""
        for line in iter(process.stdout.readline, ''):
            if line:
                # Filtrer les logs trop verbeux
                if any(skip in line.lower() for skip in ['static', 'favicon', 'hot update']):
                    continue
                print(f"{prefix}: {line.strip()}")
    
    def wait_for_startup(self):
        """Attend que les serveurs soient prêts"""
        print("\n⏳ Démarrage des serveurs...")
        
        max_wait = 30  # 30 secondes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            backend_ready = self._check_backend_health()
            frontend_ready = self._check_frontend_health()
            
            if backend_ready and frontend_ready:
                print("\n🎉 Serveurs prêts !")
                return True
            
            time.sleep(2)
        
        print("\n⚠️  Timeout - Les serveurs mettent du temps à démarrer")
        return False
    
    def _check_backend_health(self):
        """Vérifie si le backend répond"""
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _check_frontend_health(self):
        """Vérifie si le frontend répond"""
        try:
            import requests
            response = requests.get("http://localhost:5173", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def show_urls(self):
        """Affiche les URLs d'accès"""
        print("\n" + "=" * 60)
        print("🌍 SERVEURS ACTIFS")
        print("=" * 60)
        print()
        print("🎮 Application principale:")
        print("   http://localhost:5173")
        print()
        print("🔧 API Backend:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs (Documentation Swagger)")
        print("   http://localhost:8000/health (Health Check)")
        print()
        print("💡 Conseils:")
        print("   - Ouvrez http://localhost:5173 pour jouer")
        print("   - Utilisez Ctrl+C pour arrêter les serveurs")
        print("   - Les modifications sont rechargées automatiquement")
        print()
        print("=" * 60)
    
    def cleanup(self):
        """Nettoie les processus en cours"""
        print("\n🛑 Arrêt des serveurs...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Backend arrêté")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("⚠️  Backend forcé à s'arrêter")
            except Exception as e:
                print(f"❌ Erreur arrêt backend: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend arrêté")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("⚠️  Frontend forcé à s'arrêter")
            except Exception as e:
                print(f"❌ Erreur arrêt frontend: {e}")
        
        print("👋 Serveurs arrêtés")
    
    def run(self):
        """Lance le serveur de développement"""
        self.print_header()
        
        # Configuration du signal handler pour Ctrl+C
        def signal_handler(sig, frame):
            self.running = False
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # Vérifications préalables
            if not self.check_ports():
                return False
            
            # Démarrage des serveurs
            if not self.start_backend():
                return False
            
            time.sleep(3)  # Laisser le backend démarrer
            
            if not self.start_frontend():
                self.cleanup()
                return False
            
            # Attendre que tout soit prêt
            self.wait_for_startup()
            
            # Afficher les informations d'accès
            self.show_urls()
            
            # Boucle principale
            try:
                while self.running:
                    # Vérifier que les processus sont toujours vivants
                    if self.backend_process and self.backend_process.poll() is not None:
                        print("❌ Le backend s'est arrêté de manière inattendue")
                        break
                    
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print("❌ Le frontend s'est arrêté de manière inattendue")
                        break
                    
                    time.sleep(1)
            
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
        
        finally:
            self.cleanup()
        
        return True


def main():
    """Point d'entrée principal"""
    
    # Vérifier que le script setup a été lancé
    project_root = Path(__file__).parent.parent
    env_file = project_root / "backend" / ".env"
    
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        print("   Lancez d'abord: python scripts/setup.py")
        sys.exit(1)
    
    # Lancer le serveur
    server = DevServer()
    success = server.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

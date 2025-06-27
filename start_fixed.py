#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démarrage amélioré pour REMOTE
Teste les corrections avant de lancer les serveurs
"""
import sys
import subprocess
import time
import asyncio
from pathlib import Path
import webbrowser

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def run_command(cmd, cwd=None, description=""):
    """Exécute une commande et retourne le résultat"""
    try:
        print(f"Execution: {description}...")
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            shell=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"   OK: {description}")
            return True
        else:
            print(f"   ERREUR: {description}")
            if result.stderr:
                print(f"   Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ERREUR: {description} - Exception: {e}")
        return False

async def test_backend():
    """Teste le backend"""
    print("\nTest du backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERREUR: Dossier backend non trouve")
        return False
    
    # Test avec le script de test
    test_script = backend_dir / "test_fixes.py"
    if test_script.exists():
        cmd = f"{sys.executable} test_fixes.py"
        return run_command(cmd, cwd=backend_dir, description="Tests backend")
    else:
        print("WARNING: Script de test backend non trouve, test basique...")
        # Test basique
        cmd = f"{sys.executable} -c \"import app.config; print('Backend OK')\""
        return run_command(cmd, cwd=backend_dir, description="Import backend")

def test_frontend():
    """Teste le frontend"""
    print("\nTest du frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("ERREUR: Dossier frontend non trouve")
        return False
    
    # Vérifier si node_modules existe
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("Installation des dependances frontend...")
        if not run_command("npm install", cwd=frontend_dir, description="npm install"):
            return False
    
    # Test avec le script de vérification
    check_script = frontend_dir / "check-frontend.cjs"
    if check_script.exists():
        cmd = "node check-frontend.cjs"
        return run_command(cmd, cwd=frontend_dir, description="Verification frontend")
    else:
        print("WARNING: Script de verification frontend non trouve")
        return True

def start_backend():
    """Lance le serveur backend"""
    print("\nLancement du serveur backend...")
    
    backend_dir = Path("backend")
    cmd = f"{sys.executable} run.py"
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )
        
        print(f"   Backend demarre (PID: {process.pid})")
        print("   Logs:")
        
        # Lire quelques lignes de logs pour confirmer le démarrage
        lines_read = 0
        for line in process.stdout:
            if lines_read < 10:  # Afficher les premiers logs
                print(f"   {line.strip()}")
                lines_read += 1
                
                # Vérifier si le serveur a démarré avec succès
                if "Application startup complete" in line or "Uvicorn running" in line:
                    print("   OK: Backend demarre avec succes")
                    break
        
        return process
        
    except Exception as e:
        print(f"   ERREUR demarrage backend: {e}")
        return None

def start_frontend():
    """Lance le serveur frontend"""
    print("\nLancement du serveur frontend...")
    
    frontend_dir = Path("frontend")
    cmd = "npm run dev"
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )
        
        print(f"   Frontend demarre (PID: {process.pid})")
        print("   Logs:")
        
        # Lire quelques lignes de logs
        lines_read = 0
        for line in process.stdout:
            if lines_read < 15:  # Afficher plus de logs pour Vite
                print(f"   {line.strip()}")
                lines_read += 1
                
                # Vérifier si Vite a démarré
                if "Local:" in line and "localhost:5173" in line:
                    print("   OK: Frontend demarre avec succes")
                    break
        
        return process
        
    except Exception as e:
        print(f"   ERREUR demarrage frontend: {e}")
        return None

def main():
    """Fonction principale"""
    print("REMOTE - Script de demarrage ameliore")
    print("=" * 60)
    
    try:
        # Vérifier qu'on est dans le bon répertoire
        if not Path("backend").exists() or not Path("frontend").exists():
            print("ERREUR: Ce script doit etre execute depuis le repertoire racine du projet")
            print("   Structure attendue: remote-game/")
            print("   |-- backend/")
            print("   |-- frontend/")
            sys.exit(1)
        
        # Phase 1: Tests
        print("Phase 1: Tests de verification")
        
        backend_ok = asyncio.run(test_backend())
        frontend_ok = test_frontend()
        
        if not backend_ok:
            print("\nERREUR: Le backend a des problemes. Correction necessaire.")
            sys.exit(1)
        
        if not frontend_ok:
            print("\nERREUR: Le frontend a des problemes. Correction necessaire.")
            sys.exit(1)
        
        print("\nTous les tests passent !")
        
        # Phase 2: Démarrage
        print("\n" + "=" * 60)
        print("Phase 2: Demarrage des serveurs")
        
        # Démarrer le backend
        backend_process = start_backend()
        if not backend_process:
            print("ERREUR: Impossible de demarrer le backend")
            sys.exit(1)
        
        # Attendre un peu que le backend soit stable
        print("\nAttente stabilisation backend...")
        time.sleep(3)
        
        # Démarrer le frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("ERREUR: Impossible de demarrer le frontend")
            backend_process.terminate()
            sys.exit(1)
        
        # Attendre que tout soit prêt
        print("\nAttente stabilisation frontend...")
        time.sleep(5)
        
        # Ouvrir le navigateur
        print("\nOuverture du navigateur...")
        try:
            webbrowser.open("http://localhost:5173")
        except:
            print("   WARNING: Impossible d'ouvrir automatiquement le navigateur")
        
        print("\n" + "=" * 60)
        print("REMOTE demarre avec succes !")
        print("\nURLs disponibles:")
        print("   Jeu:     http://localhost:5173")
        print("   API:     http://localhost:8000")
        print("   Docs:    http://localhost:8000/docs")
        
        print("\nInstructions:")
        print("   - Le jeu est accessible sur http://localhost:5173")
        print("   - Appuyez Ctrl+C pour arreter les serveurs")
        print("   - Les logs s'affichent ci-dessous")
        
        print("\nLogs en temps reel:")
        print("-" * 40)
        
        # Afficher les logs en continu
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nArret demande...")
            print("Fermeture des serveurs...")
            
            try:
                frontend_process.terminate()
                backend_process.terminate()
                
                # Attendre un peu pour la fermeture propre
                time.sleep(2)
                
                # Forcer la fermeture si nécessaire
                try:
                    frontend_process.kill()
                    backend_process.kill()
                except:
                    pass
                    
            except:
                pass
            
            print("A bientot !")
    
    except Exception as e:
        print(f"\nErreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic REMOTE
Aide à identifier et résoudre les problèmes de démarrage
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path

def print_status(message, status="info"):
    """Affiche un message avec un statut coloré"""
    colors = {
        "info": "\033[94m",     # Bleu
        "success": "\033[92m",  # Vert
        "warning": "\033[93m",  # Jaune
        "error": "\033[91m",    # Rouge
        "reset": "\033[0m"      # Reset
    }
    
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    print(f"{colors[status]}{icons[status]} {message}{colors['reset']}")

def check_node_npm():
    """Vérifie que Node.js et npm sont installés"""
    try:
        # Vérifier Node.js
        node_result = subprocess.run(['node', '--version'], 
                                   capture_output=True, text=True, check=True)
        node_version = node_result.stdout.strip()
        print_status(f"Node.js: {node_version}", "success")
        
        # Vérifier npm
        npm_result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, check=True)
        npm_version = npm_result.stdout.strip()
        print_status(f"npm: {npm_version}", "success")
        
        return True
    except subprocess.CalledProcessError:
        print_status("Node.js ou npm non trouvé", "error")
        return False
    except FileNotFoundError:
        print_status("Node.js non installé", "error")
        return False

def check_backend():
    """Vérifie si le backend est démarré"""
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print_status("Backend accessible sur http://localhost:8000", "success")
            return True
        else:
            print_status(f"Backend répond avec le code {response.status_code}", "warning")
            return False
    except Exception as e:
        print_status("Backend non accessible sur http://localhost:8000", "warning")
        print_status("Démarrez le backend avec: cd backend && python run.py", "info")
        return False

def install_dependencies():
    """Installe les dépendances npm"""
    print_status("Installation des dépendances npm...", "info")
    try:
        result = subprocess.run(['npm', 'install'], cwd='frontend', check=True)
        print_status("Dépendances installées avec succès", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Erreur installation dépendances: {e}", "error")
        return False

def check_frontend_files():
    """Vérifie que les fichiers frontend essentiels existent"""
    frontend_path = Path("frontend")
    required_files = [
        "package.json",
        "vite.config.js",
        "src/index-debug.jsx",
        "src/App-debug.jsx",
        "src/stores/gameStore.js",
        "src/stores/osStore.js",
        "src/stores/tomStore.js",
        "src/services/websocketService.js",
        "src/services/audioService.js"
    ]
    
    missing_files = []
    for file in required_files:
        if not (frontend_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_status("Fichiers manquants:", "error")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print_status("Tous les fichiers essentiels sont présents", "success")
        return True

def start_dev_server():
    """Démarre le serveur de développement"""
    print_status("Démarrage du serveur de développement...", "info")
    print_status("Ouvrez http://localhost:5173 dans votre navigateur", "info")
    print_status("Ouvrez la console (F12) pour voir les logs de diagnostic", "info")
    print()
    
    try:
        # Démarrer le serveur de développement
        process = subprocess.Popen(['npm', 'run', 'dev'], cwd='frontend')
        
        print_status("Serveur démarré. Appuyez sur Ctrl+C pour arrêter.", "success")
        process.wait()
        
    except KeyboardInterrupt:
        print_status("Arrêt du serveur de développement", "info")
        process.terminate()
    except Exception as e:
        print_status(f"Erreur démarrage serveur: {e}", "error")

def main():
    """Fonction principale de diagnostic"""
    print("🔍 REMOTE - Diagnostic de démarrage")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path("frontend").exists() or not Path("backend").exists():
        print_status("Erreur: Vous devez être dans le répertoire remote-game", "error")
        sys.exit(1)
    
    # 1. Vérifier Node.js et npm
    print_status("Vérification des prérequis...", "info")
    if not check_node_npm():
        print_status("Installez Node.js depuis https://nodejs.org/", "error")
        sys.exit(1)
    
    # 2. Vérifier les fichiers frontend
    if not check_frontend_files():
        print_status("Certains fichiers sont manquants", "error")
        sys.exit(1)
    
    # 3. Vérifier le backend (optionnel)
    check_backend()
    
    # 4. Installer les dépendances
    if not Path("frontend/node_modules").exists():
        if not install_dependencies():
            sys.exit(1)
    else:
        print_status("Dépendances déjà installées", "success")
    
    print()
    print_status("Diagnostic terminé - Prêt à démarrer", "success")
    print()
    
    # 5. Proposer de démarrer le serveur
    choice = input("Démarrer le serveur de développement ? (o/n): ")
    if choice.lower() in ['o', 'oui', 'y', 'yes']:
        start_dev_server()
    else:
        print()
        print_status("Pour démarrer manuellement:", "info")
        print("  cd frontend")
        print("  npm run dev")
        print()
        print_status("Puis ouvrez http://localhost:5173", "info")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide des corrections REMOTE
"""
import sys
import subprocess
from pathlib import Path

def main():
    print("Test Rapide des Corrections REMOTE")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    
    # Test 1: Structure
    print("\n1. Structure projet...")
    required_paths = [
        "backend/app/services/tom_ai_service.py",
        "frontend/src/index.jsx", 
        "frontend/.env",
        "backend/.env"
    ]
    
    for path in required_paths:
        full_path = project_root / path
        status = "OK" if full_path.exists() else "MANQUANT"
        print(f"   {status}: {path}")
    
    # Test 2: Configuration WebSocket
    print("\n2. Configuration WebSocket...")
    
    frontend_env = project_root / "frontend" / ".env"
    if frontend_env.exists():
        try:
            content = frontend_env.read_text(encoding='utf-8')
            if "VITE_WS_URL=ws://localhost:5173" in content:
                print("   OK: URL WebSocket corrigee")
            else:
                print("   ERREUR: URL WebSocket incorrecte")
        except Exception as e:
            print(f"   ERREUR lecture .env: {e}")
    else:
        print("   ERREUR: .env frontend manquant")
    
    # Test 3: Tom Service
    print("\n3. Service Tom...")
    tom_service = project_root / "backend" / "app" / "services" / "tom_ai_service.py"
    if tom_service.exists():
        try:
            content = tom_service.read_text(encoding='utf-8')
            if "_safe_json_parse" in content:
                print("   OK: Gestion robuste JSON ajoutee")
            else:
                print("   ERREUR: Gestion JSON manquante")
        except Exception as e:
            print(f"   ERREUR lecture Tom service: {e}")
    
    # Test 4: Fichiers dupliqués
    print("\n4. Fichiers dupliques...")
    index_js = project_root / "frontend" / "src" / "index.js"
    index_jsx = project_root / "frontend" / "src" / "index.jsx"
    
    if not index_js.exists() and index_jsx.exists():
        print("   OK: Duplication index.js supprimee")
    else:
        print("   ERREUR: Duplication index.js toujours presente")
    
    print("\n" + "=" * 40)
    print("Pour demarrer le jeu:")
    print("   python start_fixed.py")
    print("\nPour tests detailles:")
    print("   Backend: cd backend && python test_fixes.py")
    print("   Frontend: cd frontend && node check-frontend.cjs")

if __name__ == "__main__":
    main()

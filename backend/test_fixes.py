#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier les corrections REMOTE
"""
import sys
import asyncio
import json
import os
from pathlib import Path

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Ajouter le chemin backend
sys.path.insert(0, str(Path(__file__).parent))

from app.database import check_database_connection, create_tables
from app.services.os_simulator import OSSimulator
from app.services.tom_ai_service import get_tom_service
from app.config import settings, validate_openai_config

async def test_basic_functionality():
    """Teste les fonctionnalités de base"""
    
    print("Test des corrections REMOTE...")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Test configuration...")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")
    print(f"   Host: {settings.host}:{settings.port}")
    print(f"   Database: {settings.database_url}")
    
    openai_ok = validate_openai_config()
    if openai_ok:
        print("   OK: OpenAI configure")
    else:
        print("   WARNING: OpenAI non configure (mode fallback)")
    
    # Test 2: Base de données
    print("\n2. Test base de donnees...")
    try:
        create_tables()
        db_ok = await check_database_connection()
        if db_ok:
            print("   OK: Base de donnees")
        else:
            print("   ERREUR: Probleme base de donnees")
            return False
    except Exception as e:
        print(f"   ERREUR DB: {e}")
        return False
    
    # Test 3: OS Simulator
    print("\n3. Test OS Simulator...")
    try:
        os_sim = OSSimulator()
        test_session_id = "test_session_123"
        os_state = await os_sim.generate_initial_os(test_session_id, "TestPlayer")
        
        if "theme" in os_state and "file_system" in os_state:
            print("   OK: OS Simulator")
            print(f"   - Theme: {os_state['theme']['name']}")
            print(f"   - Fichiers: {len(os_state['file_system']['documents'])}")
        else:
            print("   ERREUR: Structure OS incorrecte")
            return False
            
    except Exception as e:
        print(f"   ERREUR OS Simulator: {e}")
        return False
    
    # Test 4: Tom Service
    print("\n4. Test Tom Service...")
    try:
        tom_service = await get_tom_service()
        
        # Test d'initialisation
        result = await tom_service.initialize_session("test_tom_123", "TestPlayer")
        
        if "introduction" in result and "personality" in result:
            print("   OK: Tom Service")
            intro_msg = result["introduction"]["message"]
            print(f"   - Message d'intro: {intro_msg[:50]}...")
        else:
            print("   ERREUR: Initialisation Tom echouee")
            return False
            
    except Exception as e:
        print(f"   ERREUR Tom Service: {e}")
        return False
    
    # Test 5: Format JSON
    print("\n5. Test parsing JSON...")
    try:
        test_json = {"test": "value", "nested": {"key": "data"}}
        json_str = json.dumps(test_json)
        parsed = json.loads(json_str)
        
        if parsed == test_json:
            print("   OK: JSON parsing")
        else:
            print("   ERREUR: JSON parsing KO")
            return False
            
    except Exception as e:
        print(f"   ERREUR JSON: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Tous les tests passent !")
    print("\nProchaines etapes :")
    print("   1. Lancer le backend : cd backend && python run.py")
    print("   2. Lancer le frontend : cd frontend && npm run dev")
    print("   3. Aller a http://localhost:5173")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_basic_functionality())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrompu")
        sys.exit(0)
    except Exception as e:
        print(f"\nErreur fatale: {e}")
        sys.exit(1)

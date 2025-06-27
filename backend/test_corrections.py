"""
Script de test rapide pour vérifier les corrections
"""
import asyncio
import sys
import os
sys.path.insert(0, ".")

from app.database import check_database_connection, create_tables
from app.services.os_simulator import OSSimulator
from app.services.tom_ai_service import get_tom_service

async def test_corrections():
    """Teste les corrections apportées"""
    
    print("🧪 Test des corrections...")
    
    # Test 1: Base de données
    print("\n1. Test base de données...")
    db_ok = await check_database_connection()
    if db_ok:
        print("✅ Base de données OK")
    else:
        print("❌ Problème base de données")
        return False
    
    # Test 2: OS Simulator
    print("\n2. Test OS Simulator...")
    try:
        os_sim = OSSimulator()
        test_session_id = "test_session_123"
        os_state = await os_sim.generate_initial_os(test_session_id, "TestPlayer")
        print(f"✅ OS Simulator OK - {len(os_state)} clés générées")
        
        # Test get_os_state
        retrieved_state = await os_sim.get_os_state(test_session_id)
        if retrieved_state:
            print("✅ get_os_state OK")
        else:
            print("❌ get_os_state KO")
            
    except Exception as e:
        print(f"❌ Erreur OS Simulator: {e}")
        return False
    
    # Test 3: Tom Service
    print("\n3. Test Tom Service...")
    try:
        tom_service = await get_tom_service()
        print("✅ Tom Service OK")
    except Exception as e:
        print(f"❌ Erreur Tom Service: {e}")
        return False
    
    print("\n🎉 Tous les tests passent !")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_corrections())
    sys.exit(0 if success else 1)

"""
Routes API pour les endpoints WebSocket
Gestion des connexions temps réel
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import uuid
from datetime import datetime

from ..services.game_orchestrator import get_game_orchestrator
from ..services.tom_ai_service import get_tom_service

router = APIRouter()

# Stockage temporaire des connexions actives
# (Sera géré par le ConnectionManager dans main.py)
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/connect/{connection_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    connection_id: str,
    orchestrator = Depends(get_game_orchestrator),
    tom_service = Depends(get_tom_service)
):
    """
    Point d'entrée WebSocket principal pour une connexion
    """
    await websocket.accept()
    active_connections[connection_id] = websocket
    
    print(f"🔗 Connexion WebSocket établie: {connection_id}")
    
    try:
        while True:
            # Recevoir les messages du client
            data = await websocket.receive_json()
            
            # Router le message selon son type
            response = await route_websocket_message(
                data, connection_id, orchestrator, tom_service
            )
            
            # Envoyer la réponse
            if response:
                await websocket.send_json(response)
    
    except WebSocketDisconnect:
        print(f"🔌 Connexion WebSocket fermée: {connection_id}")
        if connection_id in active_connections:
            del active_connections[connection_id]
    
    except Exception as e:
        print(f"❌ Erreur WebSocket {connection_id}: {e}")
        if connection_id in active_connections:
            del active_connections[connection_id]


async def route_websocket_message(
    data: Dict[str, Any], 
    connection_id: str,
    orchestrator,
    tom_service
) -> Dict[str, Any]:
    """
    Route les messages WebSocket selon leur type
    """
    message_type = data.get("type")
    
    try:
        if message_type == "session_init":
            return await handle_session_init(data, connection_id, orchestrator, tom_service)
        
        elif message_type == "player_action":
            return await handle_player_action(data, connection_id, orchestrator)
        
        elif message_type == "player_hesitation":
            return await handle_player_hesitation(data, connection_id, orchestrator)
        
        elif message_type == "tom_message_request":
            return await handle_tom_message_request(data, connection_id, tom_service)
        
        elif message_type == "game_state_request":
            return await handle_game_state_request(data, connection_id, orchestrator)
        
        elif message_type == "ping":
            return {"type": "pong", "timestamp": datetime.now().isoformat()}
        
        else:
            return {
                "type": "error",
                "message": f"Type de message non reconnu: {message_type}",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        print(f"❌ Erreur traitement message {message_type}: {e}")
        return {
            "type": "error", 
            "message": f"Erreur interne: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def handle_session_init(
    data: Dict[str, Any], 
    connection_id: str, 
    orchestrator,
    tom_service
) -> Dict[str, Any]:
    """
    Gère l'initialisation d'une nouvelle session de jeu
    """
    session_id = data.get("session_id") or str(uuid.uuid4())
    player_name = data.get("player_name", "Joueur")
    
    print(f"🎯 Initialisation session: {session_id} pour {player_name}")
    
    try:
        # Démarrer la session dans l'orchestrateur
        session_data = await orchestrator.start_new_session(
            session_id=session_id,
            player_name=player_name,
            websocket_manager=None  # Sera implémenté plus tard
        )
        
        return {
            "type": "session_ready",
            "session_id": session_id,
            "session_data": session_data,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "type": "session_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_player_action(
    data: Dict[str, Any], 
    connection_id: str, 
    orchestrator
) -> Dict[str, Any]:
    """
    Gère une action du joueur
    """
    session_id = data.get("session_id")
    action_data = data.get("action_data")
    
    if not session_id or not action_data:
        return {
            "type": "action_error",
            "message": "session_id et action_data requis",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Traiter l'action avec l'orchestrateur
        result = await orchestrator.process_player_action(
            session_id=session_id,
            action_data=action_data,
            websocket_manager=None
        )
        
        return {
            "type": "action_processed",
            "session_id": session_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "type": "action_error",
            "session_id": session_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_player_hesitation(
    data: Dict[str, Any], 
    connection_id: str, 
    orchestrator
) -> Dict[str, Any]:
    """
    Gère l'hésitation du joueur
    """
    session_id = data.get("session_id")
    hesitation_data = data.get("hesitation_data")
    
    if not session_id or not hesitation_data:
        return {
            "type": "hesitation_error",
            "message": "session_id et hesitation_data requis",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        result = await orchestrator.handle_player_hesitation(
            session_id=session_id,
            hesitation_data=hesitation_data,
            websocket_manager=None
        )
        
        return {
            "type": "hesitation_processed",
            "session_id": session_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "type": "hesitation_error",
            "session_id": session_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_tom_message_request(
    data: Dict[str, Any], 
    connection_id: str, 
    tom_service
) -> Dict[str, Any]:
    """
    Gère une demande de message de Tom
    """
    session_id = data.get("session_id")
    trigger_type = data.get("trigger_type")
    context_data = data.get("context_data", {})
    
    if not session_id or not trigger_type:
        return {
            "type": "tom_error",
            "message": "session_id et trigger_type requis",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        response = await tom_service.generate_response(
            session_id=session_id,
            trigger_type=trigger_type,
            context_data=context_data
        )
        
        return {
            "type": "tom_message",
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "type": "tom_error",
            "session_id": session_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_game_state_request(
    data: Dict[str, Any], 
    connection_id: str, 
    orchestrator
) -> Dict[str, Any]:
    """
    Gère une demande d'état du jeu
    """
    session_id = data.get("session_id")
    
    if not session_id:
        return {
            "type": "state_error",
            "message": "session_id requis",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        game_status = orchestrator.get_session_status(session_id)
        
        return {
            "type": "game_state",
            "session_id": session_id,
            "state": game_status,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "type": "state_error",
            "session_id": session_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

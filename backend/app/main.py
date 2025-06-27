"""
Application principale FastAPI pour REMOTE
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from typing import Dict, List

from .config import settings, print_startup_info, validate_openai_config
from .database import create_tables, check_database_connection
from .models import GameSession
from .services.tom_ai_service import get_tom_service
from .api import game, experiment


# Gestionnaire de cycle de vie de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    
    # Démarrage
    print("🚀 Démarrage de REMOTE...")
    print_startup_info()
    
    # Vérification des prérequis
    if not validate_openai_config():
        print("⚠️  L'application peut fonctionner en mode dégradé sans OpenAI")
    
    # Initialisation de la base de données
    print("🗄️ Initialisation de la base de données...")
    create_tables()
    
    if await check_database_connection():
        print("✅ Base de données prête")
    else:
        print("❌ Problème de connexion à la base de données")
    
    # Initialisation des services
    tom_service = await get_tom_service()
    print("🤖 Service Tom initialisé")
    
    print("🎮 REMOTE est prêt à jouer !")
    print(f"📍 Interface disponible sur: http://{settings.host}:{settings.port}")
    
    yield
    
    # Arrêt
    print("🛑 Arrêt de REMOTE...")
    print("👋 À bientôt !")


# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Thriller psychologique explorant les biais cognitifs dans l'interaction humain-IA",
    lifespan=lifespan
)

# Configuration CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Gestionnaire de connexions WebSocket
class ConnectionManager:
    """Gestionnaire des connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}  # session_id -> connection_id
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accepte une nouvelle connexion"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        print(f"🔗 Connexion WebSocket établie: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Déconnecte un client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Nettoyer l'association session
        session_to_remove = None
        for session_id, conn_id in self.session_connections.items():
            if conn_id == connection_id:
                session_to_remove = session_id
                break
        
        if session_to_remove:
            del self.session_connections[session_to_remove]
        
        print(f"🔌 Connexion WebSocket fermée: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Envoie un message à une connexion spécifique"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"❌ Erreur envoi message WebSocket: {e}")
                self.disconnect(connection_id)
    
    async def send_to_session(self, message: dict, session_id: str):
        """Envoie un message à une session spécifique"""
        if session_id in self.session_connections:
            connection_id = self.session_connections[session_id]
            await self.send_personal_message(message, connection_id)
    
    def link_session(self, session_id: str, connection_id: str):
        """Lie une session à une connexion"""
        self.session_connections[session_id] = connection_id
        print(f"🔗 Session {session_id} liée à la connexion {connection_id}")


# Instance globale du gestionnaire de connexions
manager = ConnectionManager()


# Routes de base
@app.get("/")
async def root():
    """Route racine avec informations sur l'API"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "endpoints": {
            "websocket": "/ws/{connection_id}",
            "api": "/api",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de l'application"""
    db_status = await check_database_connection()
    openai_status = validate_openai_config()
    
    return {
        "status": "healthy" if db_status and openai_status else "degraded",
        "database": "connected" if db_status else "error",
        "openai": "configured" if openai_status else "missing",
        "active_connections": len(manager.active_connections),
        "active_sessions": len(manager.session_connections),
        "timestamp": "2025-01-27T20:00:00Z"  # Placeholder
    }


# WebSocket principal
@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """Point d'entrée WebSocket principal"""
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Recevoir un message du client
            data = await websocket.receive_json()
            
            # Router le message selon son type
            message_type = data.get("type")
            
            if message_type == "session_init":
                # Initialisation d'une nouvelle session
                session_id = data.get("session_id")
                player_name = data.get("player_name")
                
                if session_id:
                    manager.link_session(session_id, connection_id)
                    
                    # Initialiser Tom pour cette session
                    tom_service = await get_tom_service()
                    tom_init = await tom_service.initialize_session(session_id, player_name)
                    
                    response = {
                        "type": "session_ready",
                        "session_id": session_id,
                        "tom_introduction": tom_init["introduction"],
                        "tom_personality": tom_init["personality"]
                    }
                    
                    await manager.send_personal_message(response, connection_id)
            
            elif message_type == "player_action":
                # Action du joueur
                session_id = data.get("session_id")
                action_data = data.get("action_data")
                
                if session_id and action_data:
                    # Traiter l'action (sera implémenté dans game_orchestrator)
                    response = {
                        "type": "action_acknowledged",
                        "session_id": session_id,
                        "action_id": action_data.get("id")
                    }
                    
                    await manager.send_personal_message(response, connection_id)
            
            elif message_type == "generate_tom_message":
                # Génération de message Tom
                session_id = data.get("session_id")
                context = data.get("context", {})
                
                if session_id:
                    tom_service = await get_tom_service()
                    try:
                        message_data = await tom_service.generate_response(
                            session_id=session_id,
                            trigger_type=context.get("trigger_type", "general"),
                            context_data=context.get("action", {})
                        )
                        
                        response = {
                            "type": "tom_message_generated",
                            "session_id": session_id,
                            "message_data": message_data
                        }
                        
                        await manager.send_personal_message(response, connection_id)
                        
                    except Exception as e:
                        print(f"❌ Erreur génération Tom: {e}")
                        error_response = {
                            "type": "error",
                            "message": f"Erreur génération Tom: {str(e)}"
                        }
                        await manager.send_personal_message(error_response, connection_id)
            
            elif message_type == "ping":
                # Ping/Pong pour maintenir la connexion
                await manager.send_personal_message({"type": "pong"}, connection_id)
            
            else:
                # Message non reconnu
                error_response = {
                    "type": "error",
                    "message": f"Type de message non reconnu: {message_type}"
                }
                await manager.send_personal_message(error_response, connection_id)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        manager.disconnect(connection_id)


# Inclusion des routes API
app.include_router(game.router, prefix="/api/game", tags=["game"])
app.include_router(experiment.router, prefix="/api/experiment", tags=["experiment"])

# Route pour servir les fichiers statiques (en production)
if not settings.debug:
    app.mount("/static", StaticFiles(directory="static"), name="static")


# Fonction de lancement pour le développement
def start_server():
    """Lance le serveur de développement"""
    print("🔧 Mode développement - Lancement avec Uvicorn")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug
    )


if __name__ == "__main__":
    start_server()

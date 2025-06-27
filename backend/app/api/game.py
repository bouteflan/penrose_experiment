"""
Routes API REST pour le jeu REMOTE
Endpoints pour la gestion des sessions et des données de jeu
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models import GameSession, PlayerAction, TomInteraction
from ..services.game_orchestrator import get_game_orchestrator
from ..services.tom_ai_service import get_tom_service
from ..services.os_simulator import OSSimulator
from ..core.corruption_system import CorruptionSystem

router = APIRouter()

# Services
os_simulator = OSSimulator()
corruption_system = CorruptionSystem()


@router.post("/sessions/create")
async def create_game_session(
    player_name: Optional[str] = None,
    orchestrator = Depends(get_game_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle session de jeu
    """
    session_id = str(uuid.uuid4())
    
    try:
        # Créer la session avec l'orchestrateur
        session_data = await orchestrator.start_new_session(
            session_id=session_id,
            player_name=player_name
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "session_data": session_data,
            "created_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur création session: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    orchestrator = Depends(get_game_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Récupère les informations d'une session
    """
    try:
        # Récupérer le statut de l'orchestrateur
        session_status = orchestrator.get_session_status(session_id)
        
        if not session_status["exists"]:
            # Tenter de récupérer depuis la base de données
            db_session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not db_session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session non trouvée"
                )
            
            return {
                "session_id": session_id,
                "from_database": True,
                "session_data": db_session.to_dict()
            }
        
        return {
            "session_id": session_id,
            "from_memory": True,
            "session_data": session_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération session: {str(e)}"
        )


@router.post("/sessions/{session_id}/end")
async def end_game_session(
    session_id: str,
    ending_type: str = "manual",
    orchestrator = Depends(get_game_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Termine une session de jeu
    """
    try:
        await orchestrator.end_session(session_id, ending_type)
        
        return {
            "success": True,
            "session_id": session_id,
            "ending_type": ending_type,
            "ended_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur fin session: {str(e)}"
        )


@router.get("/sessions/{session_id}/actions")
async def get_session_actions(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Récupère les actions d'une session
    """
    try:
        actions = db.query(PlayerAction)\
            .filter(PlayerAction.session_id == session_id)\
            .order_by(PlayerAction.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return {
            "session_id": session_id,
            "actions": [action.to_dict() for action in actions],
            "total_actions": len(actions)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération actions: {str(e)}"
        )


@router.get("/sessions/{session_id}/tom-interactions")
async def get_tom_interactions(
    session_id: str,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    Récupère les interactions avec Tom pour une session
    """
    try:
        interactions = db.query(TomInteraction)\
            .filter(TomInteraction.session_id == session_id)\
            .order_by(TomInteraction.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return {
            "session_id": session_id,
            "interactions": [interaction.to_dict() for interaction in interactions],
            "total_interactions": len(interactions)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération interactions Tom: {str(e)}"
        )


@router.get("/sessions/{session_id}/os-state")
async def get_os_state(session_id: str):
    """
    Récupère l'état actuel de l'OS simulé
    """
    try:
        os_state = await os_simulator.get_os_state(session_id)
        
        if not os_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="État OS non trouvé pour cette session"
            )
        
        return {
            "session_id": session_id,
            "os_state": os_state
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération état OS: {str(e)}"
        )


@router.get("/sessions/{session_id}/corruption")
async def get_corruption_state(session_id: str):
    """
    Récupère l'état de corruption pour une session
    """
    try:
        corruption_data = await corruption_system.get_corruption_data_for_frontend(session_id)
        
        return {
            "session_id": session_id,
            "corruption_data": corruption_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération corruption: {str(e)}"
        )


@router.post("/sessions/{session_id}/tom/generate-message")
async def generate_tom_message(
    session_id: str,
    trigger_type: str,
    context_data: Dict[str, Any] = {},
    tom_service = Depends(get_tom_service)
):
    """
    Génère un message de Tom pour une situation spécifique
    """
    try:
        response = await tom_service.generate_response(
            session_id=session_id,
            trigger_type=trigger_type,
            context_data=context_data
        )
        
        return {
            "session_id": session_id,
            "trigger_type": trigger_type,
            "tom_response": response,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération message Tom: {str(e)}"
        )


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques d'une session
    """
    try:
        # Récupérer la session
        session = db.query(GameSession).filter(GameSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
        
        # Compter les actions
        total_actions = db.query(PlayerAction)\
            .filter(PlayerAction.session_id == session_id)\
            .count()
        
        obedient_actions = db.query(PlayerAction)\
            .filter(PlayerAction.session_id == session_id)\
            .filter(PlayerAction.was_obedient == True)\
            .count()
        
        meta_actions = db.query(PlayerAction)\
            .filter(PlayerAction.session_id == session_id)\
            .filter(PlayerAction.action_type.like("meta_%"))\
            .count()
        
        # Compter les interactions Tom
        tom_interactions = db.query(TomInteraction)\
            .filter(TomInteraction.session_id == session_id)\
            .count()
        
        obedience_rate = (obedient_actions / total_actions) if total_actions > 0 else 0.0
        
        return {
            "session_id": session_id,
            "session_info": session.to_dict(),
            "stats": {
                "total_actions": total_actions,
                "obedient_actions": obedient_actions,
                "meta_actions": meta_actions,
                "tom_interactions": tom_interactions,
                "obedience_rate": obedience_rate,
                "session_completed": session.is_completed,
                "ending_type": session.ending_type,
                "corruption_level": session.corruption_level,
                "duration_minutes": session.duration_minutes
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération statistiques: {str(e)}"
        )


@router.get("/sessions")
async def list_sessions(
    limit: int = 20,
    completed_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Liste les sessions de jeu
    """
    try:
        query = db.query(GameSession)
        
        if completed_only:
            query = query.filter(GameSession.is_completed == True)
        
        sessions = query.order_by(GameSession.created_at.desc()).limit(limit).all()
        
        return {
            "sessions": [session.to_dict() for session in sessions],
            "total_found": len(sessions),
            "filters": {
                "limit": limit,
                "completed_only": completed_only
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur liste sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    orchestrator = Depends(get_game_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Supprime une session et toutes ses données associées
    """
    try:
        # Terminer la session si elle est active
        try:
            await orchestrator.end_session(session_id, "deleted")
        except:
            pass  # La session n'était peut-être pas active
        
        # Supprimer de la base de données
        session = db.query(GameSession).filter(GameSession.id == session_id).first()
        if session:
            # Supprimer les actions associées
            db.query(PlayerAction).filter(PlayerAction.session_id == session_id).delete()
            
            # Supprimer les interactions Tom
            db.query(TomInteraction).filter(TomInteraction.session_id == session_id).delete()
            
            # Supprimer la session
            db.delete(session)
            db.commit()
        
        # Nettoyer les services
        os_simulator.cleanup_session(session_id)
        corruption_system.cleanup_session(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "deleted_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur suppression session: {str(e)}"
        )

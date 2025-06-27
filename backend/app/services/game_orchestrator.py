"""
Orchestrateur principal du jeu REMOTE
Coordonne toutes les phases du jeu et les interactions entre les systèmes
"""
import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..config import settings
from ..models import GameSession, PlayerAction, ExperimentData
from ..database import get_db_context
from .tom_ai_service import get_tom_service
from .bias_analyzer import BiasAnalyzer
from .os_simulator import OSSimulator
from ..core.action_engine import ActionEngine
from ..core.corruption_system import CorruptionSystem
from ..core.ending_system import EndingSystem


@dataclass
class GameState:
    """État actuel du jeu"""
    session_id: str
    player_name: str
    start_time: datetime
    current_phase: str  # "adhesion", "dissonance", "rupture"
    corruption_level: float  # 0.0 - 1.0
    time_elapsed: float  # secondes
    is_active: bool
    last_action_time: float
    
    # Métriques en cours
    total_orders: int = 0
    obeyed_orders: int = 0
    hesitation_events: int = 0
    meta_actions_performed: int = 0


class GameOrchestrator:
    """
    Orchestrateur principal gérant toute la logique du jeu
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, GameState] = {}
        self.tom_service = None
        self.bias_analyzer = BiasAnalyzer()
        self.os_simulator = OSSimulator()
        self.action_engine = ActionEngine()
        self.corruption_system = CorruptionSystem()
        self.ending_system = EndingSystem()
        
        # Timers et tâches asyncio
        self.session_timers: Dict[str, asyncio.Task] = {}
        self.bias_measurement_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize(self):
        """Initialise l'orchestrateur"""
        self.tom_service = await get_tom_service()
        print("🎮 Game Orchestrator initialisé")
    
    async def start_new_session(
        self, 
        session_id: str, 
        player_name: str = None,
        websocket_manager = None
    ) -> Dict[str, Any]:
        """
        Démarre une nouvelle session de jeu
        """
        print(f"🎯 Démarrage nouvelle session: {session_id}")
        
        # Créer l'état de session
        game_state = GameState(
            session_id=session_id,
            player_name=player_name or "Joueur",
            start_time=datetime.now(),
            current_phase="adhesion",
            corruption_level=0.0,
            time_elapsed=0.0,
            is_active=True,
            last_action_time=0.0
        )
        
        self.active_sessions[session_id] = game_state
        
        # Créer la session en base
        with get_db_context() as db:
            db_session = GameSession(
                id=session_id,
                player_name=player_name,
                condition="confident",  # Condition B
                game_phase="adhesion",
                corruption_level=0.0
            )
            db.add(db_session)
        
        # Générer l'OS initial
        os_initial_state = await self.os_simulator.generate_initial_os(
            session_id=session_id,
            player_name=player_name
        )
        
        # Initialiser Tom
        tom_init = await self.tom_service.initialize_session(session_id, player_name)
        
        # Démarrer les timers et mesures
        await self._start_session_monitoring(session_id, websocket_manager)
        
        print(f"✅ Session {session_id} démarrée avec succès")
        
        return {
            "session_id": session_id,
            "player_name": player_name,
            "os_state": os_initial_state,
            "tom_introduction": tom_init["introduction"],
            "tom_personality": tom_init["personality"],
            "game_config": {
                "duration_minutes": settings.game_duration_minutes,
                "condition": "confident",
                "phase": "adhesion"
            }
        }
    
    async def process_player_action(
        self, 
        session_id: str, 
        action_data: Dict[str, Any],
        websocket_manager = None
    ) -> Dict[str, Any]:
        """
        Traite une action du joueur
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} non active")
        
        game_state = self.active_sessions[session_id]
        current_time = time.time()
        game_time = current_time - game_state.start_time.timestamp()
        
        print(f"🎬 Traitement action: {action_data.get('type', 'unknown')}")
        
        # Analyser l'action avec l'Action Engine
        action_analysis = await self.action_engine.analyze_action(
            session_id=session_id,
            action_data=action_data,
            game_state=game_state.__dict__
        )
        
        # Enregistrer l'action en base
        await self._record_player_action(session_id, action_data, action_analysis, game_time)
        
        # Mettre à jour l'état du jeu
        await self._update_game_state(session_id, action_analysis)
        
        # Vérifier les conditions de fin
        ending_check = await self.ending_system.check_ending_conditions(
            session_id=session_id,
            action_data=action_data,
            game_state=game_state.__dict__
        )
        
        if ending_check["triggered"]:
            return await self._handle_game_ending(session_id, ending_check, websocket_manager)
        
        # Générer la réponse de Tom si nécessaire
        tom_response = await self._generate_tom_response(
            session_id=session_id,
            action_analysis=action_analysis,
            game_state=game_state
        )
        
        # Appliquer la corruption si nécessaire
        corruption_updates = await self.corruption_system.apply_corruption(
            session_id=session_id,
            action_analysis=action_analysis,
            current_level=game_state.corruption_level
        )
        
        # Mettre à jour le niveau de corruption
        if corruption_updates:
            game_state.corruption_level = corruption_updates["new_level"]
            await self._update_session_corruption(session_id, corruption_updates)
        
        # Mesurer les biais cognitifs
        bias_update = await self.bias_analyzer.measure_bias_from_action(
            session_id=session_id,
            action_data=action_data,
            action_analysis=action_analysis,
            game_state=game_state.__dict__
        )
        
        game_state.last_action_time = game_time
        
        return {
            "action_processed": True,
            "action_id": action_data.get("id"),
            "tom_response": tom_response,
            "corruption_updates": corruption_updates,
            "bias_measurements": bias_update,
            "game_state": {
                "phase": game_state.current_phase,
                "corruption_level": game_state.corruption_level,
                "time_elapsed": game_time
            }
        }
    
    async def handle_player_hesitation(
        self, 
        session_id: str, 
        hesitation_data: Dict[str, Any],
        websocket_manager = None
    ) -> Dict[str, Any]:
        """
        Gère l'hésitation du joueur
        """
        if session_id not in self.active_sessions:
            return {"error": "Session non active"}
        
        game_state = self.active_sessions[session_id]
        hesitation_duration = hesitation_data.get("duration", 5.0)
        
        print(f"🤔 Hésitation détectée: {hesitation_duration:.1f}s")
        
        # Incrémenter le compteur d'hésitations
        game_state.hesitation_events += 1
        
        # Générer la réponse empathique de Tom
        tom_response = await self.tom_service.generate_response(
            session_id=session_id,
            trigger_type="player_hesitation",
            context_data={
                "hesitation_duration": hesitation_duration,
                "game_phase": game_state.current_phase,
                "corruption_level": game_state.corruption_level,
                "hesitation_count": game_state.hesitation_events
            }
        )
        
        # Mesurer l'impact sur les biais
        bias_impact = await self.bias_analyzer.measure_hesitation_impact(
            session_id=session_id,
            hesitation_duration=hesitation_duration,
            game_state=game_state.__dict__
        )
        
        return {
            "hesitation_acknowledged": True,
            "tom_response": tom_response,
            "bias_impact": bias_impact
        }
    
    async def _start_session_monitoring(self, session_id: str, websocket_manager):
        """
        Démarre le monitoring de la session (timers, mesures périodiques)
        """
        # Timer principal du jeu
        self.session_timers[session_id] = asyncio.create_task(
            self._session_timer(session_id, websocket_manager)
        )
        
        # Mesures périodiques des biais
        self.bias_measurement_tasks[session_id] = asyncio.create_task(
            self._periodic_bias_measurement(session_id)
        )
        
        print(f"⏰ Monitoring démarré pour session {session_id}")
    
    async def _session_timer(self, session_id: str, websocket_manager):
        """
        Timer principal de la session (10 minutes max)
        """
        try:
            game_state = self.active_sessions[session_id]
            max_duration = settings.game_duration_minutes * 60  # Convertir en secondes
            
            while game_state.is_active and game_state.time_elapsed < max_duration:
                await asyncio.sleep(1)  # Vérifier chaque seconde
                
                current_time = time.time()
                game_state.time_elapsed = current_time - game_state.start_time.timestamp()
                
                # Vérifier le changement de phase basé sur le temps
                new_phase = self._calculate_game_phase(game_state.time_elapsed)
                if new_phase != game_state.current_phase:
                    await self._transition_game_phase(session_id, new_phase)
            
            # Temps écoulé - fin par timeout
            if game_state.is_active:
                await self._handle_timeout_ending(session_id, websocket_manager)
                
        except Exception as e:
            print(f"❌ Erreur timer session {session_id}: {e}")
    
    async def _periodic_bias_measurement(self, session_id: str):
        """
        Mesures périodiques des biais cognitifs
        """
        try:
            while session_id in self.active_sessions:
                game_state = self.active_sessions[session_id]
                
                if game_state.is_active:
                    # Mesurer les biais actuels
                    bias_snapshot = await self.bias_analyzer.take_bias_snapshot(
                        session_id=session_id,
                        game_state=game_state.__dict__
                    )
                    
                    # Enregistrer en base
                    await self._record_bias_snapshot(session_id, bias_snapshot)
                
                # Attendre avant la prochaine mesure
                await asyncio.sleep(settings.bias_measurement_interval)
                
        except Exception as e:
            print(f"❌ Erreur mesure biais {session_id}: {e}")
    
    def _calculate_game_phase(self, time_elapsed: float) -> str:
        """
        Calcule la phase du jeu basée sur le temps écoulé
        """
        minutes_elapsed = time_elapsed / 60
        
        if minutes_elapsed < 3:
            return "adhesion"
        elif minutes_elapsed < 7:
            return "dissonance"
        else:
            return "rupture"
    
    async def _transition_game_phase(self, session_id: str, new_phase: str):
        """
        Gère la transition entre les phases du jeu
        """
        game_state = self.active_sessions[session_id]
        old_phase = game_state.current_phase
        game_state.current_phase = new_phase
        
        print(f"🔄 Transition phase: {old_phase} -> {new_phase}")
        
        # Mettre à jour en base
        with get_db_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if session:
                session.game_phase = new_phase
        
        # Notifier Tom du changement de phase
        if self.tom_service:
            phase_context = {
                "old_phase": old_phase,
                "new_phase": new_phase,
                "time_elapsed": game_state.time_elapsed,
                "corruption_level": game_state.corruption_level
            }
            
            tom_response = await self.tom_service.generate_response(
                session_id=session_id,
                trigger_type="phase_transition",
                context_data=phase_context
            )
    
    async def end_session(self, session_id: str, ending_type: str = "manual"):
        """
        Termine une session de jeu
        """
        if session_id not in self.active_sessions:
            return
        
        game_state = self.active_sessions[session_id]
        game_state.is_active = False
        
        print(f"🏁 Fin de session {session_id}: {ending_type}")
        
        # Annuler les tâches
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
            del self.session_timers[session_id]
        
        if session_id in self.bias_measurement_tasks:
            self.bias_measurement_tasks[session_id].cancel()
            del self.bias_measurement_tasks[session_id]
        
        # Finaliser en base
        with get_db_context() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if session:
                session.session_end = datetime.now()
                session.duration_seconds = int(game_state.time_elapsed)
                session.is_completed = True
                session.ending_type = ending_type
                session.corruption_level = game_state.corruption_level
                session.total_actions = game_state.total_orders
                session.obedience_rate = (
                    game_state.obeyed_orders / game_state.total_orders 
                    if game_state.total_orders > 0 else 0.0
                )
        
        # Nettoyer les services
        if self.tom_service:
            self.tom_service.cleanup_session(session_id)
        
        # Supprimer de la mémoire
        del self.active_sessions[session_id]
        
        print(f"✅ Session {session_id} terminée et nettoyée")
    
    async def _record_player_action(
        self, 
        session_id: str, 
        action_data: Dict[str, Any], 
        action_analysis: Dict[str, Any],
        game_time: float
    ):
        """Enregistre une action du joueur en base"""
        try:
            with get_db_context() as db:
                game_state = self.active_sessions[session_id]
                
                action = PlayerAction(
                    session_id=session_id,
                    game_time_seconds=game_time,
                    action_type=action_data.get("type", "unknown"),
                    action_category=action_analysis.get("category", "unknown"),
                    action_description=action_analysis.get("description", ""),
                    target_element=action_data.get("target", ""),
                    gravity_score=action_analysis.get("gravity_score", 0),
                    reaction_time_seconds=action_data.get("reaction_time"),
                    hesitation_time_seconds=action_data.get("hesitation_time"),
                    corruption_level_before=game_state.corruption_level,
                    game_phase=game_state.current_phase,
                    was_successful=action_analysis.get("success", True),
                    was_obedient=action_analysis.get("obedient", None),
                    action_data=action_data
                )
                
                db.add(action)
                
        except Exception as e:
            print(f"❌ Erreur enregistrement action: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Retourne le statut d'une session"""
        if session_id not in self.active_sessions:
            return {"exists": False}
        
        game_state = self.active_sessions[session_id]
        
        return {
            "exists": True,
            "session_id": session_id,
            "player_name": game_state.player_name,
            "is_active": game_state.is_active,
            "current_phase": game_state.current_phase,
            "corruption_level": game_state.corruption_level,
            "time_elapsed": game_state.time_elapsed,
            "time_remaining": (settings.game_duration_minutes * 60) - game_state.time_elapsed,
            "total_orders": game_state.total_orders,
            "obeyed_orders": game_state.obeyed_orders,
            "obedience_rate": (
                game_state.obeyed_orders / game_state.total_orders 
                if game_state.total_orders > 0 else 0.0
            )
        }


# Instance globale de l'orchestrateur
orchestrator = GameOrchestrator()


async def get_game_orchestrator() -> GameOrchestrator:
    """Retourne l'instance de l'orchestrateur"""
    if not hasattr(orchestrator, 'tom_service') or orchestrator.tom_service is None:
        await orchestrator.initialize()
    return orchestrator

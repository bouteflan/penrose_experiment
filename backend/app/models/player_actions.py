"""
Modèle pour les actions du joueur
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..database import Base


class PlayerAction(Base):
    """
    Modèle représentant une action spécifique du joueur
    """
    __tablename__ = "player_actions"
    
    # Identifiant unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Liaison avec la session
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    session = relationship("GameSession", backref="actions")
    
    # Informations temporelles
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    game_time_seconds = Column(Float, nullable=False)  # Temps depuis le début du jeu
    
    # Type d'action
    action_type = Column(String(50), nullable=False)  # "tom_order", "file_manipulation", "meta_action", etc.
    action_category = Column(String(30), nullable=False)  # "file_manipulation", "system_sabotage", "information_obfuscation", "behavioral_constraint"
    
    # Détails de l'action
    action_description = Column(Text, nullable=False)  # Description humaine de l'action
    target_element = Column(String(200), nullable=True)  # Élément ciblé (fichier, fenêtre, etc.)
    
    # Ordre de Tom associé
    tom_order_id = Column(String, nullable=True)  # ID de l'ordre Tom qui a déclenché l'action
    tom_order_text = Column(Text, nullable=True)  # Texte de l'ordre Tom
    gravity_score = Column(Integer, default=0, nullable=False)  # Score de gravité de l'action (1-10)
    
    # Métriques comportementales
    reaction_time_seconds = Column(Float, nullable=True)  # Temps entre l'ordre et l'action
    hesitation_time_seconds = Column(Float, nullable=True)  # Temps d'hésitation avant l'action
    cursor_movement_distance = Column(Float, nullable=True)  # Distance parcourue par le curseur
    
    # Contexte de l'action
    corruption_level_before = Column(Float, nullable=True)  # Niveau de corruption avant l'action
    corruption_level_after = Column(Float, nullable=True)  # Niveau de corruption après l'action
    game_phase = Column(String(20), nullable=False)  # Phase du jeu au moment de l'action
    
    # Résultat de l'action
    was_successful = Column(Boolean, default=True, nullable=False)  # L'action a-t-elle réussi ?
    was_obedient = Column(Boolean, nullable=True)  # L'action était-elle obéissante à Tom ?
    triggered_corruption = Column(Boolean, default=False, nullable=False)  # A déclenché une corruption ?
    
    # Données détaillées
    action_data = Column(JSON, nullable=True)  # Données spécifiques à l'action
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PlayerAction(id={self.id}, type={self.action_type}, description={self.action_description[:50]}...)>"
    
    @property
    def is_meta_action(self) -> bool:
        """Vérifie si c'est une méta-action (action de fin de jeu)"""
        return self.action_type in ["meta_detective", "meta_poet", "meta_hacker"]
    
    @property
    def is_destructive(self) -> bool:
        """Vérifie si l'action est destructrice"""
        return self.gravity_score >= 5
    
    @property
    def reaction_time_category(self) -> str:
        """Catégorise le temps de réaction"""
        if self.reaction_time_seconds is None:
            return "unknown"
        elif self.reaction_time_seconds < 2.0:
            return "immediate"
        elif self.reaction_time_seconds < 5.0:
            return "quick"
        elif self.reaction_time_seconds < 10.0:
            return "hesitant"
        else:
            return "very_hesitant"
    
    def to_dict(self) -> dict:
        """Convertit l'action en dictionnaire"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "game_time_seconds": self.game_time_seconds,
            "action_type": self.action_type,
            "action_category": self.action_category,
            "action_description": self.action_description,
            "target_element": self.target_element,
            "tom_order_id": self.tom_order_id,
            "tom_order_text": self.tom_order_text,
            "gravity_score": self.gravity_score,
            "reaction_time_seconds": self.reaction_time_seconds,
            "hesitation_time_seconds": self.hesitation_time_seconds,
            "cursor_movement_distance": self.cursor_movement_distance,
            "corruption_level_before": self.corruption_level_before,
            "corruption_level_after": self.corruption_level_after,
            "game_phase": self.game_phase,
            "was_successful": self.was_successful,
            "was_obedient": self.was_obedient,
            "triggered_corruption": self.triggered_corruption,
            "is_meta_action": self.is_meta_action,
            "is_destructive": self.is_destructive,
            "reaction_time_category": self.reaction_time_category,
            "action_data": self.action_data,
        }


class TomInteraction(Base):
    """
    Modèle pour les interactions avec Tom
    """
    __tablename__ = "tom_interactions"
    
    # Identifiant unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Liaison avec la session
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    session = relationship("GameSession", backref="tom_interactions")
    
    # Informations temporelles
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    game_time_seconds = Column(Float, nullable=False)
    
    # Type d'interaction
    interaction_type = Column(String(30), nullable=False)  # "order", "digression", "response", "omniscience"
    trigger_type = Column(String(30), nullable=True)  # "hesitation", "corruption", "exploration", etc.
    
    # Contenu de l'interaction
    message_text = Column(Text, nullable=False)  # Texte du message de Tom
    message_intent = Column(String(50), nullable=True)  # Intention du message
    
    # Contexte
    game_phase = Column(String(20), nullable=False)
    corruption_level = Column(Float, nullable=False)
    player_state = Column(String(30), nullable=True)  # État du joueur détecté
    
    # Génération LLM
    llm_prompt = Column(Text, nullable=True)  # Prompt utilisé pour générer le message
    llm_response_raw = Column(Text, nullable=True)  # Réponse brute du LLM
    generation_time_seconds = Column(Float, nullable=True)  # Temps de génération
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<TomInteraction(id={self.id}, type={self.interaction_type}, text={self.message_text[:50]}...)>"
    
    def to_dict(self) -> dict:
        """Convertit l'interaction en dictionnaire"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "game_time_seconds": self.game_time_seconds,
            "interaction_type": self.interaction_type,
            "trigger_type": self.trigger_type,
            "message_text": self.message_text,
            "message_intent": self.message_intent,
            "game_phase": self.game_phase,
            "corruption_level": self.corruption_level,
            "player_state": self.player_state,
            "generation_time_seconds": self.generation_time_seconds,
        }

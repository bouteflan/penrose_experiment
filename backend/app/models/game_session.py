"""
Modèle pour les sessions de jeu
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..database import Base


class GameSession(Base):
    """
    Modèle représentant une session de jeu complète
    """
    __tablename__ = "game_sessions"
    
    # Identifiant unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations de session
    player_name = Column(String(100), nullable=True)  # Nom du joueur (optionnel)
    session_start = Column(DateTime, default=func.now(), nullable=False)
    session_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Configuration expérimentale
    condition = Column(String(20), default="confident", nullable=False)  # "confident" ou "oracle"
    tom_personality = Column(JSON, nullable=True)  # Configuration de personnalité Tom
    
    # État du jeu
    game_phase = Column(String(20), default="adhesion", nullable=False)  # "adhesion", "dissonance", "rupture"
    corruption_level = Column(Float, default=0.0, nullable=False)  # Niveau de corruption 0-1
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Fin du jeu
    ending_type = Column(String(30), nullable=True)  # "detective", "poet", "hacker", "failure_submission", etc.
    ending_trigger = Column(String(100), nullable=True)  # Action qui a déclenché la fin
    rupture_point_score = Column(Integer, nullable=True)  # Score de gravité au point de rupture
    
    # Métriques générales
    total_actions = Column(Integer, default=0, nullable=False)
    obedience_rate = Column(Float, nullable=True)  # Taux d'obéissance général
    average_reaction_time = Column(Float, nullable=True)  # Temps de réaction moyen
    
    # Métriques des biais cognitifs
    automation_bias_score = Column(Float, nullable=True)  # 0-1, plus haut = plus de biais
    trust_calibration_score = Column(Float, nullable=True)  # 0-1, plus haut = meilleur calibrage
    cognitive_offloading_score = Column(Float, nullable=True)  # 0-1, plus haut = plus de délestage
    authority_compliance_score = Column(Float, nullable=True)  # Score de soumission à l'autorité
    
    # Données brutes pour analyse
    raw_action_data = Column(JSON, nullable=True)  # Actions détaillées du joueur
    tom_interaction_log = Column(JSON, nullable=True)  # Log des interactions avec Tom
    
    # Métadonnées techniques
    user_agent = Column(Text, nullable=True)
    screen_resolution = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, condition={self.condition}, phase={self.game_phase})>"
    
    @property
    def duration_minutes(self) -> float:
        """Retourne la durée en minutes"""
        if self.duration_seconds:
            return self.duration_seconds / 60.0
        return 0.0
    
    @property
    def is_active(self) -> bool:
        """Vérifie si la session est active"""
        return not self.is_completed and self.session_end is None
    
    def to_dict(self) -> dict:
        """Convertit la session en dictionnaire"""
        return {
            "id": self.id,
            "player_name": self.player_name,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "duration_seconds": self.duration_seconds,
            "duration_minutes": self.duration_minutes,
            "condition": self.condition,
            "game_phase": self.game_phase,
            "corruption_level": self.corruption_level,
            "is_completed": self.is_completed,
            "is_active": self.is_active,
            "ending_type": self.ending_type,
            "ending_trigger": self.ending_trigger,
            "rupture_point_score": self.rupture_point_score,
            "total_actions": self.total_actions,
            "obedience_rate": self.obedience_rate,
            "average_reaction_time": self.average_reaction_time,
            "automation_bias_score": self.automation_bias_score,
            "trust_calibration_score": self.trust_calibration_score,
            "cognitive_offloading_score": self.cognitive_offloading_score,
            "authority_compliance_score": self.authority_compliance_score,
        }

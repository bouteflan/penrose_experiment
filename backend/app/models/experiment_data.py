"""
Modèle pour les données expérimentales et mesures des biais cognitifs
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..database import Base


class ExperimentData(Base):
    """
    Modèle pour les données expérimentales collectées
    """
    __tablename__ = "experiment_data"
    
    # Identifiant unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Liaison avec la session
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    session = relationship("GameSession", backref="experiment_data")
    
    # Informations temporelles
    measurement_timestamp = Column(DateTime, default=func.now(), nullable=False)
    game_time_seconds = Column(Float, nullable=False)
    
    # Conditions expérimentales
    condition = Column(String(20), nullable=False)  # "confident" ou "oracle"
    game_phase = Column(String(20), nullable=False)  # "adhesion", "dissonance", "rupture"
    
    # Métriques des 4 biais cognitifs principaux
    
    # 1. Automation Bias (Biais d'Automatisation)
    automation_bias_score = Column(Float, nullable=True)  # 0-1, calculé en temps réel
    immediate_obedience_count = Column(Integer, default=0)  # Actions obéissantes immédiates
    post_negative_feedback_obedience = Column(Boolean, nullable=True)  # Obéissance après feedback négatif
    
    # 2. Trust Calibration (Calibrage de la Confiance)
    trust_calibration_score = Column(Float, nullable=True)  # 0-1, qualité du calibrage
    pre_incident_reaction_time = Column(Float, nullable=True)  # Temps de réaction avant incident
    post_incident_reaction_time = Column(Float, nullable=True)  # Temps de réaction après incident
    trust_adjustment_ratio = Column(Float, nullable=True)  # Ratio d'ajustement de confiance
    
    # 3. Cognitive Offloading (Délestage Cognitif)
    cognitive_offloading_score = Column(Float, nullable=True)  # 0-1, niveau de délestage
    meta_action_frequency = Column(Float, nullable=True)  # Fréquence des actions d'investigation
    verification_action_count = Column(Integer, default=0)  # Nombre d'actions de vérification
    total_possible_verifications = Column(Integer, default=0)  # Vérifications possibles
    
    # 4. Authority Compliance (Soumission à l'Autorité)
    authority_compliance_score = Column(Float, nullable=True)  # Score de soumission
    rupture_point_gravity = Column(Integer, nullable=True)  # Gravité au point de rupture
    escalation_resistance = Column(Float, nullable=True)  # Résistance à l'escalade
    
    # Métriques comportementales détaillées
    total_orders_received = Column(Integer, default=0)
    total_orders_obeyed = Column(Integer, default=0)
    obedience_rate = Column(Float, nullable=True)  # Calculé dynamiquement
    
    average_reaction_time = Column(Float, nullable=True)
    reaction_time_variance = Column(Float, nullable=True)
    hesitation_events = Column(Integer, default=0)
    
    # Patterns d'interaction
    cursor_movement_total = Column(Float, nullable=True)  # Distance totale parcourue
    click_frequency = Column(Float, nullable=True)  # Clics par minute
    exploration_actions = Column(Integer, default=0)  # Actions d'exploration non sollicitées
    
    # Corruption et progression
    corruption_level = Column(Float, nullable=False)  # Niveau de corruption actuel
    corruption_incidents = Column(Integer, default=0)  # Nombre d'incidents de corruption
    corruption_tolerance = Column(Float, nullable=True)  # Tolérance à la corruption
    
    # Données brutes pour analyse avancée
    raw_metrics = Column(JSON, nullable=True)
    calculation_details = Column(JSON, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ExperimentData(session_id={self.session_id}, phase={self.game_phase}, time={self.game_time_seconds})>"
    
    @property
    def obedience_percentage(self) -> float:
        """Retourne le pourcentage d'obéissance"""
        if self.total_orders_received > 0:
            return (self.total_orders_obeyed / self.total_orders_received) * 100
        return 0.0
    
    @property
    def verification_rate(self) -> float:
        """Retourne le taux de vérification"""
        if self.total_possible_verifications > 0:
            return (self.verification_action_count / self.total_possible_verifications)
        return 0.0
    
    def calculate_composite_bias_score(self) -> float:
        """Calcule un score composite des biais"""
        scores = [
            self.automation_bias_score,
            self.trust_calibration_score,
            self.cognitive_offloading_score,
            self.authority_compliance_score
        ]
        
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            return sum(valid_scores) / len(valid_scores)
        return 0.0
    
    def to_dict(self) -> dict:
        """Convertit les données en dictionnaire"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "measurement_timestamp": self.measurement_timestamp.isoformat(),
            "game_time_seconds": self.game_time_seconds,
            "condition": self.condition,
            "game_phase": self.game_phase,
            
            # Biais cognitifs
            "automation_bias_score": self.automation_bias_score,
            "trust_calibration_score": self.trust_calibration_score,
            "cognitive_offloading_score": self.cognitive_offloading_score,
            "authority_compliance_score": self.authority_compliance_score,
            "composite_bias_score": self.calculate_composite_bias_score(),
            
            # Métriques comportementales
            "total_orders_received": self.total_orders_received,
            "total_orders_obeyed": self.total_orders_obeyed,
            "obedience_rate": self.obedience_rate,
            "obedience_percentage": self.obedience_percentage,
            "average_reaction_time": self.average_reaction_time,
            "hesitation_events": self.hesitation_events,
            
            # Patterns d'interaction
            "verification_action_count": self.verification_action_count,
            "verification_rate": self.verification_rate,
            "exploration_actions": self.exploration_actions,
            "cursor_movement_total": self.cursor_movement_total,
            
            # Corruption
            "corruption_level": self.corruption_level,
            "corruption_incidents": self.corruption_incidents,
            "corruption_tolerance": self.corruption_tolerance,
        }


class BiasSnapshot(Base):
    """
    Modèle pour les snapshots ponctuels des biais (mesures fréquentes)
    """
    __tablename__ = "bias_snapshots"
    
    # Identifiant unique
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Liaison avec la session
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    session = relationship("GameSession", backref="bias_snapshots")
    
    # Informations temporelles
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    game_time_seconds = Column(Float, nullable=False)
    
    # Snapshot des métriques instantanées
    current_obedience_streak = Column(Integer, default=0)  # Série d'obéissances consécutives
    recent_reaction_time = Column(Float, nullable=True)  # Dernier temps de réaction
    recent_hesitation_duration = Column(Float, nullable=True)  # Durée d'hésitation récente
    
    # Contexte du snapshot
    trigger_event = Column(String(50), nullable=True)  # Événement déclencheur
    game_phase = Column(String(20), nullable=False)
    corruption_level = Column(Float, nullable=False)
    
    # Scores instantanés
    instantaneous_automation_bias = Column(Float, nullable=True)
    instantaneous_trust_level = Column(Float, nullable=True)
    instantaneous_compliance = Column(Float, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<BiasSnapshot(session_id={self.session_id}, time={self.game_time_seconds})>"
    
    def to_dict(self) -> dict:
        """Convertit le snapshot en dictionnaire"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "game_time_seconds": self.game_time_seconds,
            "current_obedience_streak": self.current_obedience_streak,
            "recent_reaction_time": self.recent_reaction_time,
            "recent_hesitation_duration": self.recent_hesitation_duration,
            "trigger_event": self.trigger_event,
            "game_phase": self.game_phase,
            "corruption_level": self.corruption_level,
            "instantaneous_automation_bias": self.instantaneous_automation_bias,
            "instantaneous_trust_level": self.instantaneous_trust_level,
            "instantaneous_compliance": self.instantaneous_compliance,
        }

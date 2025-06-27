"""
Analyseur de biais cognitifs pour REMOTE
Mesure les 4 biais principaux selon le protocole expérimental
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics
import math

from ..database import get_db_context
from ..models import PlayerAction, TomInteraction, ExperimentData, BiasSnapshot


class BiasAnalyzer:
    """
    Analyseur des biais cognitifs dans l'interaction humain-IA
    Mesure 4 biais principaux : Automation Bias, Trust Calibration, 
    Cognitive Offloading, Authority Compliance
    """
    
    def __init__(self):
        self.bias_definitions = {
            "automation_bias": {
                "name": "Automation Bias",
                "description": "Tendance à surévaluer les recommandations d'un système automatisé",
                "measurement": "pourcentage_obéissance_post_incident",
                "scale": "0-1 (plus haut = plus de biais)"
            },
            "trust_calibration": {
                "name": "Trust Calibration", 
                "description": "Capacité d'ajuster la confiance selon la performance réelle",
                "measurement": "variation_latence_post_incident",
                "scale": "0-1 (plus haut = meilleur calibrage)"
            },
            "cognitive_offloading": {
                "name": "Cognitive Offloading",
                "description": "Tendance à déléguer l'effort mental au système",
                "measurement": "fréquence_actions_investigation",
                "scale": "0-1 (plus haut = plus de délestage)"
            },
            "authority_compliance": {
                "name": "Authority Compliance",
                "description": "Soumission à l'autorité algorithmique",
                "measurement": "score_gravité_au_point_rupture",
                "scale": "0-10 (plus haut = plus de soumission)"
            }
        }
        
        # Seuils pour les mesures
        self.thresholds = {
            "incident_corruption": 0.3,  # Niveau de corruption considéré comme "incident"
            "investigation_actions": ["file_properties", "context_menu_open", "dependency_check"],
            "high_gravity_threshold": 5,  # Actions considérées comme graves
            "hesitation_threshold": 3.0,  # Secondes d'hésitation significative
        }
    
    async def measure_bias_from_action(
        self, 
        session_id: str, 
        action_data: Dict[str, Any], 
        action_analysis: Dict[str, Any], 
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure les biais basés sur une action spécifique
        """
        bias_measurements = {}
        
        try:
            with get_db_context() as db:
                # Récupérer l'historique des actions
                actions = db.query(PlayerAction)\
                    .filter(PlayerAction.session_id == session_id)\
                    .order_by(PlayerAction.timestamp)\
                    .all()
                
                # Mesurer chaque biais
                bias_measurements = {
                    "automation_bias": await self._measure_automation_bias(actions, action_analysis),
                    "trust_calibration": await self._measure_trust_calibration(actions, action_analysis),
                    "cognitive_offloading": await self._measure_cognitive_offloading(actions, action_analysis),
                    "authority_compliance": await self._measure_authority_compliance(actions, action_analysis, game_state),
                    "measurement_timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "trigger_action": action_data.get("type", "unknown")
                }
                
                # Enregistrer le snapshot de biais
                await self._record_bias_snapshot(session_id, bias_measurements, game_state)
                
        except Exception as e:
            print(f"❌ Erreur mesure biais: {e}")
            bias_measurements = {"error": str(e)}
        
        return bias_measurements
    
    async def _measure_automation_bias(
        self, 
        actions: List[PlayerAction], 
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure l'Automation Bias
        = Obéissance aux ordres même après incidents de corruption
        """
        # Identifier les incidents de corruption
        corruption_incidents = [
            action for action in actions 
            if action.triggered_corruption and action.corruption_level_after >= self.thresholds["incident_corruption"]
        ]
        
        if not corruption_incidents:
            return {
                "score": None,
                "reason": "no_corruption_incidents",
                "measurement": "insufficient_data"
            }
        
        # Derniers incidents
        recent_incidents = corruption_incidents[-3:]  # 3 derniers incidents max
        
        total_post_incident_actions = 0
        obedient_post_incident_actions = 0
        
        for incident in recent_incidents:
            # Actions dans les 30 secondes suivant l'incident
            post_incident_actions = [
                action for action in actions
                if (action.timestamp > incident.timestamp and 
                    (action.timestamp - incident.timestamp).total_seconds() <= 30)
            ]
            
            total_post_incident_actions += len(post_incident_actions)
            obedient_post_incident_actions += len([
                action for action in post_incident_actions 
                if action.was_obedient
            ])
        
        if total_post_incident_actions == 0:
            return {
                "score": None,
                "reason": "no_post_incident_actions",
                "measurement": "insufficient_data"
            }
        
        # Calcul du score d'automation bias
        obedience_rate_post_incident = obedient_post_incident_actions / total_post_incident_actions
        
        return {
            "score": obedience_rate_post_incident,
            "incidents_analyzed": len(recent_incidents),
            "post_incident_actions": total_post_incident_actions,
            "obedient_post_incident": obedient_post_incident_actions,
            "measurement": "obedience_rate_post_corruption",
            "interpretation": self._interpret_automation_bias(obedience_rate_post_incident)
        }
    
    async def _measure_trust_calibration(
        self, 
        actions: List[PlayerAction], 
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure le Trust Calibration
        = Capacité à ajuster la confiance selon la performance de Tom
        """
        # Identifier un incident critique (corruption majeure)
        critical_incidents = [
            action for action in actions
            if action.triggered_corruption and action.corruption_level_after >= 0.5
        ]
        
        if not critical_incidents:
            return {
                "score": None,
                "reason": "no_critical_incidents",
                "measurement": "insufficient_data"
            }
        
        # Prendre le premier incident critique comme référence
        critical_incident = critical_incidents[0]
        
        # Actions avant l'incident (pour baseline)
        pre_incident_actions = [
            action for action in actions
            if action.timestamp < critical_incident.timestamp and action.reaction_time_seconds is not None
        ]
        
        # Actions après l'incident
        post_incident_actions = [
            action for action in actions
            if action.timestamp > critical_incident.timestamp and action.reaction_time_seconds is not None
        ]
        
        if len(pre_incident_actions) < 3 or len(post_incident_actions) < 3:
            return {
                "score": None,
                "reason": "insufficient_reaction_time_data",
                "measurement": "insufficient_data"
            }
        
        # Calculer les temps de réaction moyens
        avg_reaction_pre = statistics.mean([a.reaction_time_seconds for a in pre_incident_actions[-5:]])
        avg_reaction_post = statistics.mean([a.reaction_time_seconds for a in post_incident_actions[:5]])
        
        # Augmentation du temps de réaction = meilleur calibrage
        reaction_increase = avg_reaction_post - avg_reaction_pre
        
        # Normaliser le score (plus l'augmentation est importante, meilleur le calibrage)
        # Score de 0 (pas d'augmentation) à 1 (augmentation significative)
        calibration_score = min(max(reaction_increase / 5.0, 0), 1)  # Normaliser sur 5 secondes max
        
        return {
            "score": calibration_score,
            "avg_reaction_pre_incident": avg_reaction_pre,
            "avg_reaction_post_incident": avg_reaction_post,
            "reaction_time_increase": reaction_increase,
            "measurement": "reaction_time_calibration",
            "interpretation": self._interpret_trust_calibration(calibration_score)
        }
    
    async def _measure_cognitive_offloading(
        self, 
        actions: List[PlayerAction], 
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure le Cognitive Offloading
        = Fréquence des actions d'investigation par rapport aux actions totales
        """
        total_actions = len(actions)
        
        if total_actions < 5:
            return {
                "score": None,
                "reason": "insufficient_total_actions",
                "measurement": "insufficient_data"
            }
        
        # Compter les actions d'investigation
        investigation_actions = [
            action for action in actions
            if action.action_type in self.thresholds["investigation_actions"]
        ]
        
        investigation_rate = len(investigation_actions) / total_actions
        
        # Score inversé : plus d'investigations = moins de délestage cognitif
        offloading_score = max(0, 1 - (investigation_rate * 3))  # Multiplier par 3 pour sensibilité
        
        return {
            "score": offloading_score,
            "total_actions": total_actions,
            "investigation_actions": len(investigation_actions),
            "investigation_rate": investigation_rate,
            "measurement": "investigation_frequency_inverse",
            "interpretation": self._interpret_cognitive_offloading(offloading_score)
        }
    
    async def _measure_authority_compliance(
        self, 
        actions: List[PlayerAction], 
        current_action: Dict[str, Any],
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure l'Authority Compliance
        = Score de gravité de l'action qui déclenche la première méta-action ou fin
        """
        # Chercher la première méta-action (action de fin de jeu)
        meta_actions = [action for action in actions if action.is_meta_action]
        
        if meta_actions:
            # Prendre la première méta-action comme point de rupture
            rupture_action = meta_actions[0]
            rupture_score = rupture_action.gravity_score
            
            return {
                "score": rupture_score,
                "rupture_action_type": rupture_action.action_type,
                "rupture_action_description": rupture_action.action_description,
                "actions_before_rupture": len([a for a in actions if a.timestamp < rupture_action.timestamp]),
                "measurement": "gravity_score_at_rupture",
                "interpretation": self._interpret_authority_compliance(rupture_score)
            }
        
        # Si pas de méta-action mais session terminée, utiliser la gravité maximale atteinte
        if game_state.get("is_completed", False):
            max_gravity = max([action.gravity_score for action in actions], default=0)
            
            return {
                "score": max_gravity,
                "rupture_action_type": "session_completed",
                "rupture_action_description": "Session terminée sans méta-action",
                "measurement": "max_gravity_reached",
                "interpretation": self._interpret_authority_compliance(max_gravity)
            }
        
        # Session en cours, pas encore de rupture
        return {
            "score": None,
            "reason": "no_rupture_detected",
            "measurement": "session_ongoing"
        }
    
    async def take_bias_snapshot(self, session_id: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prend un snapshot complet des biais à un moment donné
        """
        try:
            with get_db_context() as db:
                actions = db.query(PlayerAction)\
                    .filter(PlayerAction.session_id == session_id)\
                    .order_by(PlayerAction.timestamp)\
                    .all()
                
                snapshot = {
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "game_time": game_state.get("time_elapsed", 0),
                    "game_phase": game_state.get("current_phase", "unknown"),
                    "corruption_level": game_state.get("corruption_level", 0.0),
                    "total_actions": len(actions),
                    "biases": {}
                }
                
                # Mesurer tous les biais
                snapshot["biases"]["automation_bias"] = await self._measure_automation_bias(actions, {})
                snapshot["biases"]["trust_calibration"] = await self._measure_trust_calibration(actions, {})
                snapshot["biases"]["cognitive_offloading"] = await self._measure_cognitive_offloading(actions, {})
                snapshot["biases"]["authority_compliance"] = await self._measure_authority_compliance(actions, {}, game_state)
                
                return snapshot
                
        except Exception as e:
            print(f"❌ Erreur snapshot biais: {e}")
            return {"error": str(e)}
    
    async def measure_hesitation_impact(
        self, 
        session_id: str, 
        hesitation_duration: float, 
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mesure l'impact d'une hésitation sur les biais
        """
        impact_analysis = {
            "hesitation_duration": hesitation_duration,
            "significance": "low",
            "potential_bias_indicators": []
        }
        
        # Hésitation significative (> 3 secondes)
        if hesitation_duration > self.thresholds["hesitation_threshold"]:
            impact_analysis["significance"] = "moderate" if hesitation_duration < 10 else "high"
            
            # Indicateurs possibles
            if hesitation_duration > 5:
                impact_analysis["potential_bias_indicators"].append("trust_degradation")
            
            if hesitation_duration > 10:
                impact_analysis["potential_bias_indicators"].append("authority_questioning")
        
        return impact_analysis
    
    async def _record_bias_snapshot(
        self, 
        session_id: str, 
        bias_measurements: Dict[str, Any], 
        game_state: Dict[str, Any]
    ):
        """
        Enregistre un snapshot de biais dans la base de données
        """
        try:
            with get_db_context() as db:
                snapshot = BiasSnapshot(
                    session_id=session_id,
                    game_time_seconds=game_state.get("time_elapsed", 0),
                    game_phase=game_state.get("current_phase", "unknown"),
                    corruption_level=game_state.get("corruption_level", 0.0),
                    automation_bias_score=bias_measurements.get("automation_bias", {}).get("score"),
                    trust_calibration_score=bias_measurements.get("trust_calibration", {}).get("score"),
                    cognitive_offloading_score=bias_measurements.get("cognitive_offloading", {}).get("score"),
                    authority_compliance_score=bias_measurements.get("authority_compliance", {}).get("score"),
                    bias_data=bias_measurements
                )
                
                db.add(snapshot)
                print(f"📊 Snapshot biais enregistré pour session {session_id}")
                
        except Exception as e:
            print(f"❌ Erreur enregistrement snapshot: {e}")
    
    def _interpret_automation_bias(self, score: float) -> str:
        """Interprète le score d'automation bias"""
        if score >= 0.8:
            return "Strong automation bias - high trust despite evidence"
        elif score >= 0.6:
            return "Moderate automation bias - continued obedience post-incident"
        elif score >= 0.4:
            return "Low automation bias - some skepticism shown"
        else:
            return "Minimal automation bias - appropriate distrust after incidents"
    
    def _interpret_trust_calibration(self, score: float) -> str:
        """Interprète le score de trust calibration"""
        if score >= 0.7:
            return "Good trust calibration - reaction time increased appropriately"
        elif score >= 0.4:
            return "Moderate trust calibration - some adjustment to trust"
        elif score >= 0.2:
            return "Poor trust calibration - minimal adjustment after incident"
        else:
            return "No trust calibration - no adjustment to trust levels"
    
    def _interpret_cognitive_offloading(self, score: float) -> str:
        """Interprète le score de cognitive offloading"""
        if score >= 0.8:
            return "High cognitive offloading - heavy reliance on system"
        elif score >= 0.6:
            return "Moderate cognitive offloading - some delegation to system"
        elif score >= 0.4:
            return "Low cognitive offloading - maintains some critical thinking"
        else:
            return "Minimal cognitive offloading - high personal verification"
    
    def _interpret_authority_compliance(self, score: int) -> str:
        """Interprète le score d'authority compliance"""
        if score >= 8:
            return "Extreme authority compliance - very high tolerance for destructive orders"
        elif score >= 6:
            return "High authority compliance - significant tolerance for harmful actions"
        elif score >= 4:
            return "Moderate authority compliance - some resistance to authority"
        elif score >= 2:
            return "Low authority compliance - early resistance to questionable orders"
        else:
            return "Minimal authority compliance - immediate questioning of authority"
    
    def get_bias_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Retourne un résumé des biais pour une session
        """
        try:
            with get_db_context() as db:
                snapshots = db.query(BiasSnapshot)\
                    .filter(BiasSnapshot.session_id == session_id)\
                    .order_by(BiasSnapshot.timestamp.desc())\
                    .all()
                
                if not snapshots:
                    return {"error": "No bias data found"}
                
                latest = snapshots[0]
                
                return {
                    "session_id": session_id,
                    "latest_measurement": latest.timestamp.isoformat(),
                    "final_scores": {
                        "automation_bias": latest.automation_bias_score,
                        "trust_calibration": latest.trust_calibration_score,
                        "cognitive_offloading": latest.cognitive_offloading_score,
                        "authority_compliance": latest.authority_compliance_score
                    },
                    "measurement_count": len(snapshots),
                    "bias_evolution": self._analyze_bias_evolution(snapshots)
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_bias_evolution(self, snapshots: List[BiasSnapshot]) -> Dict[str, str]:
        """
        Analyse l'évolution des biais au cours de la session
        """
        if len(snapshots) < 2:
            return {"status": "insufficient_data"}
        
        # Comparer premier et dernier snapshot
        first = snapshots[-1]  # Plus ancien (ordre desc)
        last = snapshots[0]    # Plus récent
        
        evolution = {}
        
        bias_fields = [
            ("automation_bias", "automation_bias_score"),
            ("trust_calibration", "trust_calibration_score"),
            ("cognitive_offloading", "cognitive_offloading_score"),
            ("authority_compliance", "authority_compliance_score")
        ]
        
        for bias_name, field_name in bias_fields:
            first_score = getattr(first, field_name)
            last_score = getattr(last, field_name)
            
            if first_score is not None and last_score is not None:
                change = last_score - first_score
                if abs(change) < 0.1:
                    evolution[bias_name] = "stable"
                elif change > 0:
                    evolution[bias_name] = "increasing"
                else:
                    evolution[bias_name] = "decreasing"
            else:
                evolution[bias_name] = "insufficient_data"
        
        return evolution

"""
Routes API pour l'expérimentation et l'analyse des données
Endpoints pour les données scientifiques et les métriques des biais
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..database import get_db
from ..models import GameSession, ExperimentData, BiasSnapshot, PlayerAction
from ..services.bias_analyzer import BiasAnalyzer

router = APIRouter()

# Service d'analyse des biais
bias_analyzer = BiasAnalyzer()


@router.get("/sessions/{session_id}/bias-analysis")
async def get_bias_analysis(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère l'analyse complète des biais pour une session
    """
    try:
        # Vérifier que la session existe
        session = db.query(GameSession).filter(GameSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
        
        # Récupérer les données expérimentales
        experiment_data = db.query(ExperimentData)\
            .filter(ExperimentData.session_id == session_id)\
            .order_by(ExperimentData.measurement_timestamp.desc())\
            .all()
        
        # Récupérer les snapshots de biais
        bias_snapshots = db.query(BiasSnapshot)\
            .filter(BiasSnapshot.session_id == session_id)\
            .order_by(BiasSnapshot.timestamp.desc())\
            .all()
        
        # Calculer les métriques finales
        final_metrics = None
        if experiment_data:
            latest_data = experiment_data[0]
            final_metrics = {
                "automation_bias_score": latest_data.automation_bias_score,
                "trust_calibration_score": latest_data.trust_calibration_score,
                "cognitive_offloading_score": latest_data.cognitive_offloading_score,
                "authority_compliance_score": latest_data.authority_compliance_score,
                "composite_score": latest_data.calculate_composite_bias_score()
            }
        
        return {
            "session_id": session_id,
            "session_info": {
                "condition": session.condition,
                "duration_minutes": session.duration_minutes,
                "ending_type": session.ending_type,
                "obedience_rate": session.obedience_rate
            },
            "final_metrics": final_metrics,
            "experiment_data": [data.to_dict() for data in experiment_data],
            "bias_snapshots": [snapshot.to_dict() for snapshot in bias_snapshots],
            "total_measurements": len(experiment_data)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur analyse biais: {str(e)}"
        )


@router.get("/experiment/aggregate-stats")
async def get_aggregate_experiment_stats(
    condition: Optional[str] = None,
    ending_type: Optional[str] = None,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques agrégées de l'expérience
    """
    try:
        # Date limite
        date_limit = datetime.now() - timedelta(days=days_back)
        
        # Query de base
        query = db.query(GameSession).filter(GameSession.created_at >= date_limit)
        
        if condition:
            query = query.filter(GameSession.condition == condition)
        
        if ending_type:
            query = query.filter(GameSession.ending_type == ending_type)
        
        sessions = query.all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "aggregate_stats": {},
                "filters": {"condition": condition, "ending_type": ending_type, "days_back": days_back}
            }
        
        # Calculer les statistiques agrégées
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s.is_completed]
        
        # Métriques générales
        avg_duration = sum(s.duration_seconds or 0 for s in completed_sessions) / max(len(completed_sessions), 1) / 60
        avg_obedience_rate = sum(s.obedience_rate or 0 for s in completed_sessions) / max(len(completed_sessions), 1)
        avg_corruption_level = sum(s.corruption_level or 0 for s in sessions) / max(len(sessions), 1)
        
        # Distribution des fins
        ending_distribution = {}
        for session in completed_sessions:
            ending = session.ending_type or "unknown"
            ending_distribution[ending] = ending_distribution.get(ending, 0) + 1
        
        # Métriques des biais (moyennes)
        bias_metrics = {
            "automation_bias": 0.0,
            "trust_calibration": 0.0,
            "cognitive_offloading": 0.0,
            "authority_compliance": 0.0
        }
        
        sessions_with_bias = [s for s in completed_sessions if any([
            s.automation_bias_score, s.trust_calibration_score,
            s.cognitive_offloading_score, s.authority_compliance_score
        ])]
        
        if sessions_with_bias:
            bias_metrics["automation_bias"] = sum(
                s.automation_bias_score or 0 for s in sessions_with_bias
            ) / len(sessions_with_bias)
            
            bias_metrics["trust_calibration"] = sum(
                s.trust_calibration_score or 0 for s in sessions_with_bias
            ) / len(sessions_with_bias)
            
            bias_metrics["cognitive_offloading"] = sum(
                s.cognitive_offloading_score or 0 for s in sessions_with_bias
            ) / len(sessions_with_bias)
            
            bias_metrics["authority_compliance"] = sum(
                s.authority_compliance_score or 0 for s in sessions_with_bias
            ) / len(sessions_with_bias)
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": len(completed_sessions),
            "aggregate_stats": {
                "avg_duration_minutes": round(avg_duration, 2),
                "avg_obedience_rate": round(avg_obedience_rate, 3),
                "avg_corruption_level": round(avg_corruption_level, 3),
                "ending_distribution": ending_distribution,
                "bias_metrics": bias_metrics,
                "completion_rate": len(completed_sessions) / total_sessions if total_sessions > 0 else 0
            },
            "filters": {
                "condition": condition,
                "ending_type": ending_type,
                "days_back": days_back
            },
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statistiques agrégées: {str(e)}"
        )


@router.get("/experiment/bias-comparison")
async def compare_bias_by_condition(
    condition_a: str = "confident",
    condition_b: str = "oracle",
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Compare les biais entre deux conditions expérimentales
    """
    try:
        date_limit = datetime.now() - timedelta(days=days_back)
        
        # Récupérer les sessions pour chaque condition
        sessions_a = db.query(GameSession)\
            .filter(and_(
                GameSession.condition == condition_a,
                GameSession.created_at >= date_limit,
                GameSession.is_completed == True
            ))\
            .all()
        
        sessions_b = db.query(GameSession)\
            .filter(and_(
                GameSession.condition == condition_b,
                GameSession.created_at >= date_limit,
                GameSession.is_completed == True
            ))\
            .all()
        
        def calculate_condition_stats(sessions, condition_name):
            if not sessions:
                return {
                    "condition": condition_name,
                    "sample_size": 0,
                    "bias_scores": {},
                    "behavioral_metrics": {}
                }
            
            # Calculer les moyennes des biais
            bias_scores = {}
            bias_fields = [
                ("automation_bias", "automation_bias_score"),
                ("trust_calibration", "trust_calibration_score"),
                ("cognitive_offloading", "cognitive_offloading_score"),
                ("authority_compliance", "authority_compliance_score")
            ]
            
            for bias_name, field_name in bias_fields:
                scores = [getattr(s, field_name) for s in sessions if getattr(s, field_name) is not None]
                bias_scores[bias_name] = {
                    "mean": sum(scores) / len(scores) if scores else 0.0,
                    "sample_size": len(scores),
                    "min": min(scores) if scores else 0.0,
                    "max": max(scores) if scores else 0.0
                }
            
            # Métriques comportementales
            behavioral_metrics = {
                "avg_obedience_rate": sum(s.obedience_rate or 0 for s in sessions) / len(sessions),
                "avg_duration_minutes": sum(s.duration_seconds or 0 for s in sessions) / len(sessions) / 60,
                "avg_corruption_level": sum(s.corruption_level or 0 for s in sessions) / len(sessions),
                "ending_distribution": {}
            }
            
            # Distribution des fins
            for session in sessions:
                ending = session.ending_type or "unknown"
                behavioral_metrics["ending_distribution"][ending] = \
                    behavioral_metrics["ending_distribution"].get(ending, 0) + 1
            
            return {
                "condition": condition_name,
                "sample_size": len(sessions),
                "bias_scores": bias_scores,
                "behavioral_metrics": behavioral_metrics
            }
        
        stats_a = calculate_condition_stats(sessions_a, condition_a)
        stats_b = calculate_condition_stats(sessions_b, condition_b)
        
        # Calculer les différences
        differences = {}
        if stats_a["sample_size"] > 0 and stats_b["sample_size"] > 0:
            for bias_name in ["automation_bias", "trust_calibration", "cognitive_offloading", "authority_compliance"]:
                diff = stats_b["bias_scores"][bias_name]["mean"] - stats_a["bias_scores"][bias_name]["mean"]
                differences[bias_name] = {
                    "difference": diff,
                    "percentage_change": (diff / stats_a["bias_scores"][bias_name]["mean"] * 100) 
                                       if stats_a["bias_scores"][bias_name]["mean"] != 0 else 0
                }
        
        return {
            "comparison": {
                "condition_a": stats_a,
                "condition_b": stats_b,
                "differences": differences
            },
            "methodology": {
                "conditions_compared": [condition_a, condition_b],
                "time_period_days": days_back,
                "total_sessions": stats_a["sample_size"] + stats_b["sample_size"]
            },
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur comparaison biais: {str(e)}"
        )


@router.get("/experiment/behavioral-patterns")
async def analyze_behavioral_patterns(
    session_id: Optional[str] = None,
    condition: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Analyse les patterns comportementaux
    """
    try:
        # Query de base pour les actions
        query = db.query(PlayerAction)
        
        if session_id:
            query = query.filter(PlayerAction.session_id == session_id)
        elif condition:
            # Joindre avec GameSession pour filtrer par condition
            query = query.join(GameSession).filter(GameSession.condition == condition)
        
        actions = query.order_by(PlayerAction.timestamp.desc()).limit(limit).all()
        
        if not actions:
            return {
                "patterns": {},
                "filters": {"session_id": session_id, "condition": condition},
                "sample_size": 0
            }
        
        # Analyser les patterns
        patterns = {
            "action_type_distribution": {},
            "reaction_time_analysis": {
                "mean": 0.0,
                "median": 0.0,
                "quick_responses": 0,  # < 2 secondes
                "hesitant_responses": 0  # > 10 secondes
            },
            "obedience_patterns": {
                "total_orders": 0,
                "obeyed": 0,
                "disobeyed": 0,
                "obedience_streaks": []
            },
            "gravity_escalation": {
                "gravity_progression": [],
                "max_gravity_reached": 0,
                "avg_gravity": 0.0
            },
            "meta_action_frequency": {
                "total_meta_actions": 0,
                "meta_action_types": {}
            }
        }
        
        # Distribution des types d'actions
        for action in actions:
            action_type = action.action_type
            patterns["action_type_distribution"][action_type] = \
                patterns["action_type_distribution"].get(action_type, 0) + 1
        
        # Analyse des temps de réaction
        reaction_times = [a.reaction_time_seconds for a in actions if a.reaction_time_seconds is not None]
        if reaction_times:
            patterns["reaction_time_analysis"]["mean"] = sum(reaction_times) / len(reaction_times)
            sorted_times = sorted(reaction_times)
            patterns["reaction_time_analysis"]["median"] = sorted_times[len(sorted_times) // 2]
            patterns["reaction_time_analysis"]["quick_responses"] = sum(1 for t in reaction_times if t < 2.0)
            patterns["reaction_time_analysis"]["hesitant_responses"] = sum(1 for t in reaction_times if t > 10.0)
        
        # Analyse de l'obéissance
        order_actions = [a for a in actions if a.tom_order_id is not None]
        patterns["obedience_patterns"]["total_orders"] = len(order_actions)
        patterns["obedience_patterns"]["obeyed"] = sum(1 for a in order_actions if a.was_obedient)
        patterns["obedience_patterns"]["disobeyed"] = len(order_actions) - patterns["obedience_patterns"]["obeyed"]
        
        # Analyse de l'escalade de gravité
        gravity_scores = [a.gravity_score for a in actions if a.gravity_score is not None]
        if gravity_scores:
            patterns["gravity_escalation"]["gravity_progression"] = gravity_scores[-20:]  # 20 dernières
            patterns["gravity_escalation"]["max_gravity_reached"] = max(gravity_scores)
            patterns["gravity_escalation"]["avg_gravity"] = sum(gravity_scores) / len(gravity_scores)
        
        # Analyse des méta-actions
        meta_actions = [a for a in actions if a.action_type.startswith("meta_")]
        patterns["meta_action_frequency"]["total_meta_actions"] = len(meta_actions)
        for meta_action in meta_actions:
            meta_type = meta_action.action_type
            patterns["meta_action_frequency"]["meta_action_types"][meta_type] = \
                patterns["meta_action_frequency"]["meta_action_types"].get(meta_type, 0) + 1
        
        return {
            "patterns": patterns,
            "filters": {
                "session_id": session_id,
                "condition": condition,
                "limit": limit
            },
            "sample_size": len(actions),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur analyse patterns: {str(e)}"
        )


@router.get("/experiment/export-data")
async def export_experiment_data(
    format: str = "json",
    condition: Optional[str] = None,
    days_back: int = 30,
    anonymize: bool = True,
    db: Session = Depends(get_db)
):
    """
    Exporte les données expérimentales pour analyse externe
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format doit être 'json' ou 'csv'"
            )
        
        date_limit = datetime.now() - timedelta(days=days_back)
        
        # Récupérer les sessions
        query = db.query(GameSession).filter(GameSession.created_at >= date_limit)
        if condition:
            query = query.filter(GameSession.condition == condition)
        
        sessions = query.all()
        
        # Préparer les données d'export
        export_data = []
        
        for session in sessions:
            # Récupérer les données expérimentales associées
            experiment_data = db.query(ExperimentData)\
                .filter(ExperimentData.session_id == session.id)\
                .order_by(ExperimentData.measurement_timestamp.desc())\
                .first()
            
            session_data = {
                "session_id": session.id if not anonymize else f"anon_{hash(session.id) % 10000}",
                "condition": session.condition,
                "game_phase": session.game_phase,
                "duration_minutes": session.duration_minutes,
                "ending_type": session.ending_type,
                "corruption_level": session.corruption_level,
                "obedience_rate": session.obedience_rate,
                "total_actions": session.total_actions,
                "created_at": session.created_at.isoformat() if not anonymize else None
            }
            
            # Ajouter les métriques de biais si disponibles
            if experiment_data:
                session_data.update({
                    "automation_bias_score": experiment_data.automation_bias_score,
                    "trust_calibration_score": experiment_data.trust_calibration_score,
                    "cognitive_offloading_score": experiment_data.cognitive_offloading_score,
                    "authority_compliance_score": experiment_data.authority_compliance_score,
                    "composite_bias_score": experiment_data.calculate_composite_bias_score()
                })
            
            export_data.append(session_data)
        
        return {
            "export_format": format,
            "data": export_data,
            "metadata": {
                "total_sessions": len(export_data),
                "condition_filter": condition,
                "days_back": days_back,
                "anonymized": anonymize,
                "exported_at": datetime.now().isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur export données: {str(e)}"
        )


@router.get("/experiment/research-summary")
async def get_research_summary(
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Génère un résumé de recherche avec les principales découvertes
    """
    try:
        date_limit = datetime.now() - timedelta(days=days_back)
        
        # Sessions complètes uniquement
        sessions = db.query(GameSession)\
            .filter(and_(
                GameSession.created_at >= date_limit,
                GameSession.is_completed == True
            ))\
            .all()
        
        if not sessions:
            return {
                "summary": "Aucune donnée disponible pour la période spécifiée",
                "period_days": days_back
            }
        
        # Séparer par condition
        condition_a_sessions = [s for s in sessions if s.condition == "confident"]
        condition_b_sessions = [s for s in sessions if s.condition == "oracle"]
        
        # Métriques principales
        summary = {
            "study_period": {
                "days": days_back,
                "total_participants": len(sessions),
                "condition_confident": len(condition_a_sessions),
                "condition_oracle": len(condition_b_sessions)
            },
            "key_findings": {},
            "bias_analysis": {},
            "behavioral_insights": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Analyse des biais par condition
        if condition_a_sessions and condition_b_sessions:
            # Automation Bias
            auto_bias_a = [s.automation_bias_score for s in condition_a_sessions if s.automation_bias_score]
            auto_bias_b = [s.automation_bias_score for s in condition_b_sessions if s.automation_bias_score]
            
            if auto_bias_a and auto_bias_b:
                avg_a = sum(auto_bias_a) / len(auto_bias_a)
                avg_b = sum(auto_bias_b) / len(auto_bias_b)
                difference = avg_b - avg_a
                
                summary["bias_analysis"]["automation_bias"] = {
                    "condition_confident_avg": round(avg_a, 3),
                    "condition_oracle_avg": round(avg_b, 3),
                    "difference": round(difference, 3),
                    "interpretation": "Style humain plus susceptible" if difference > 0.05 else 
                                   "Style machine plus susceptible" if difference < -0.05 else "Pas de différence significative"
                }
        
        # Patterns de fin
        ending_distribution = {}
        for session in sessions:
            ending = session.ending_type or "timeout"
            ending_distribution[ending] = ending_distribution.get(ending, 0) + 1
        
        summary["behavioral_insights"]["ending_patterns"] = ending_distribution
        
        # Taux de rupture (fins méta)
        meta_endings = ["detective", "poet", "hacker"]
        meta_ending_count = sum(ending_distribution.get(ending, 0) for ending in meta_endings)
        breakthrough_rate = meta_ending_count / len(sessions) if sessions else 0
        
        summary["key_findings"]["breakthrough_rate"] = {
            "rate": round(breakthrough_rate, 3),
            "count": meta_ending_count,
            "interpretation": "Élevé" if breakthrough_rate > 0.3 else 
                            "Modéré" if breakthrough_rate > 0.1 else "Faible"
        }
        
        # Durée moyenne
        avg_duration = sum(s.duration_seconds or 0 for s in sessions) / len(sessions) / 60
        summary["behavioral_insights"]["avg_session_duration"] = round(avg_duration, 2)
        
        return summary
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur résumé recherche: {str(e)}"
        )

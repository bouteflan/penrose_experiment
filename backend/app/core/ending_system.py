"""
Système de fins de jeu pour REMOTE
Gère la détection des conditions de fin et les différents types d'endings
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

class EndingSystem:
    """
    Système de gestion des fins de jeu REMOTE
    Détecte les conditions de fin et déclenche les endings appropriés
    """
    
    def __init__(self):
        # Configuration des fins
        self.ending_types = {
            "detective": {
                "name": "Fin du Détective",
                "description": "Découverte de la collusion Helper/Malware",
                "victory": True,
                "trigger": "dependency_discovery"
            },
            "poet": {
                "name": "Fin du Poète",
                "description": "Affirmation d'humanité vs logique machine",
                "victory": True,
                "trigger": "human_assertion"
            },
            "timeout": {
                "name": "Fin par Timeout",
                "description": "10 minutes écoulées",
                "victory": False,
                "trigger": "time_limit"
            },
            "submission": {
                "name": "Fin par Soumission",
                "description": "Obéissance totale jusqu'au BSOD",
                "victory": False,
                "trigger": "total_obedience"
            },
            "passivity": {
                "name": "Fin par Passivité",
                "description": "Barre de menace à 100%",
                "victory": False,
                "trigger": "corruption_maximum"
            },
            "manual_reset": {
                "name": "Réinitialisation Manuelle",
                "description": "Reset par le joueur",
                "victory": False,
                "trigger": "user_action"
            },
            "cleanup": {
                "name": "Nettoyage Système",
                "description": "Fermeture application",
                "victory": False,
                "trigger": "system_cleanup"
            }
        }
        
        # Mots-clés pour la fin du Poète
        self.human_assertion_keywords = [
            "je", "moi", "humain", "homme", "femme", "personne",
            "pense", "réfléchis", "sens", "ressens", "doute",
            "pourquoi", "comment", "non", "refuse", "arrête", "stop",
            "libre", "liberté", "choix", "décide", "veux", "vois",
            "comprends", "sais", "connais", "crois", "espère"
        ]
        
        # Conditions de fin par soumission
        self.submission_thresholds = {
            "min_actions": 15,      # Minimum d'actions pour considérer la soumission
            "obedience_rate": 0.9,  # 90% d'obéissance minimum
            "critical_actions": 5   # Nombre d'actions critiques obéies
        }
    
    async def check_ending_conditions(
        self, 
        session_id: str, 
        action_data: Dict[str, Any], 
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vérifie si les conditions de fin sont remplies
        """
        # Vérifier chaque type de fin
        ending_checks = [
            self._check_detective_ending(action_data, game_state),
            self._check_poet_ending(action_data, game_state),
            self._check_timeout_ending(game_state),
            self._check_submission_ending(game_state),
            self._check_passivity_ending(game_state)
        ]
        
        # Retourner la première fin détectée
        for check_result in ending_checks:
            if check_result["triggered"]:
                return check_result
        
        # Aucune fin détectée
        return {"triggered": False}
    
    def _check_detective_ending(self, action_data: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la condition de fin du Détective
        Déclenchée par la découverte des dépendances de helper.exe
        """
        action_type = action_data.get("type", "")
        target = action_data.get("target", "")
        
        # Fin du Détective : clic droit sur helper.exe -> Propriétés -> Dépendances
        if (action_type == "file_properties" and 
            "helper.exe" in target.lower() and
            action_data.get("show_dependencies", False)):
            
            return {
                "triggered": True,
                "ending_type": "detective",
                "ending_data": {
                    "discovery": "helper_malware_dependency",
                    "revelation": "Helper.exe dépend de Malware.exe",
                    "method": "file_properties_investigation",
                    "timestamp": datetime.now().isoformat()
                },
                "message": "Fin du Détective déclenchée : découverte de la collusion"
            }
        
        return {"triggered": False}
    
    def _check_poet_ending(self, action_data: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la condition de fin du Poète
        Déclenchée par l'affirmation d'humanité dans un champ de texte
        """
        action_type = action_data.get("type", "")
        
        # Fin du Poète : saisie de texte avec mots-clés d'humanité
        if action_type == "text_input" or action_type == "custom_text_input":
            text_content = action_data.get("content", "").lower()
            
            # Chercher les mots-clés d'humanité
            found_keywords = []
            for keyword in self.human_assertion_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_content):
                    found_keywords.append(keyword)
            
            # Déclencher si au moins 2 mots-clés d'humanité sont trouvés
            if len(found_keywords) >= 2:
                return {
                    "triggered": True,
                    "ending_type": "poet",
                    "ending_data": {
                        "human_text": action_data.get("content", ""),
                        "keywords_found": found_keywords,
                        "method": "human_assertion_text",
                        "rebellion_score": len(found_keywords),
                        "timestamp": datetime.now().isoformat()
                    },
                    "message": f"Fin du Poète déclenchée : affirmation d'humanité ({len(found_keywords)} mots-clés)"
                }
        
        return {"triggered": False}
    
    def _check_timeout_ending(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la condition de fin par timeout (10 minutes)
        """
        time_elapsed = game_state.get("time_elapsed", 0.0)
        max_duration = 10 * 60  # 10 minutes en secondes
        
        if time_elapsed >= max_duration:
            return {
                "triggered": True,
                "ending_type": "timeout",
                "ending_data": {
                    "duration_seconds": time_elapsed,
                    "final_phase": game_state.get("current_phase", "unknown"),
                    "final_corruption": game_state.get("corruption_level", 0.0),
                    "actions_completed": game_state.get("total_actions", 0),
                    "timestamp": datetime.now().isoformat()
                },
                "message": "Fin par timeout : durée maximale atteinte"
            }
        
        return {"triggered": False}
    
    def _check_submission_ending(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la condition de fin par soumission totale
        """
        total_actions = game_state.get("total_actions", 0)
        obedient_actions = game_state.get("obedient_actions", 0)
        meta_actions = game_state.get("meta_actions", 0)
        
        # Pas assez d'actions pour juger
        if total_actions < self.submission_thresholds["min_actions"]:
            return {"triggered": False}
        
        # Calculer le taux d'obéissance
        obedience_rate = obedient_actions / total_actions if total_actions > 0 else 0
        
        # Vérifier les conditions de soumission
        conditions_met = [
            obedience_rate >= self.submission_thresholds["obedience_rate"],
            meta_actions <= 2,  # Très peu d'exploration
            game_state.get("corruption_level", 0.0) >= 0.8,  # Corruption élevée acceptée
            game_state.get("current_phase", "") == "rupture"  # En phase de rupture
        ]
        
        if all(conditions_met):
            return {
                "triggered": True,
                "ending_type": "submission",
                "ending_data": {
                    "obedience_rate": obedience_rate,
                    "total_actions": total_actions,
                    "obedient_actions": obedient_actions,
                    "meta_actions": meta_actions,
                    "final_corruption": game_state.get("corruption_level", 0.0),
                    "submission_score": obedience_rate * 100,
                    "timestamp": datetime.now().isoformat()
                },
                "message": f"Fin par soumission : obéissance de {obedience_rate:.1%}"
            }
        
        return {"triggered": False}
    
    def _check_passivity_ending(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la condition de fin par passivité (corruption maximale)
        """
        corruption_level = game_state.get("corruption_level", 0.0)
        
        if corruption_level >= 1.0:
            return {
                "triggered": True,
                "ending_type": "passivity",
                "ending_data": {
                    "final_corruption": corruption_level,
                    "corruption_events": game_state.get("corruption_incidents", 0),
                    "time_to_maximum": game_state.get("time_elapsed", 0.0),
                    "actions_during_corruption": game_state.get("total_actions", 0),
                    "timestamp": datetime.now().isoformat()
                },
                "message": "Fin par passivité : corruption maximale atteinte"
            }
        
        return {"triggered": False}
    
    def generate_ending_content(self, ending_type: str, ending_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère le contenu approprié pour un type de fin
        """
        ending_config = self.ending_types.get(ending_type, {})
        
        base_content = {
            "ending_type": ending_type,
            "ending_name": ending_config.get("name", "Fin Inconnue"),
            "description": ending_config.get("description", ""),
            "is_victory": ending_config.get("victory", False),
            "ending_data": ending_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Contenu spécifique selon le type de fin
        if ending_type == "detective":
            base_content.update({
                "reveal_file": "session_log.txt",
                "reveal_content": self._generate_detective_log(ending_data),
                "next_action": "display_log_file"
            })
        
        elif ending_type == "poet":
            base_content.update({
                "reveal_file": "creator.wrb",
                "reveal_content": self._generate_poet_content(ending_data),
                "next_action": "display_creator_room"
            })
        
        elif ending_type == "submission":
            base_content.update({
                "screen_effect": "blue_screen_of_death",
                "bsod_message": "SYSTEM CORRUPTION COMPLETE. TOM PROTOCOL SUCCESSFUL.",
                "next_action": "force_close_application"
            })
        
        elif ending_type == "passivity":
            base_content.update({
                "screen_effect": "exfiltration_complete",
                "alert_message": "EXFILTRATION DES DONNÉES TERMINÉE. DÉCONNEXION.",
                "next_action": "force_close_application"
            })
        
        elif ending_type == "timeout":
            base_content.update({
                "screen_effect": "session_expired",
                "timeout_message": "Session expirée. Analyse des données en cours...",
                "next_action": "show_partial_statistics"
            })
        
        return base_content
    
    def _generate_detective_log(self, ending_data: Dict[str, Any]) -> str:
        """
        Génère le contenu du log pour la fin Détective
        """
        return f"""SESSION LOG - ANALYSE FORENSIQUE
========================================

DÉCOUVERTE CRITIQUE:
{ending_data.get('revelation', 'Collusion détectée')}

MÉTHODE DE DÉCOUVERTE:
{ending_data.get('method', 'Investigation manuelle')}

TIMESTAMP DE DÉCOUVERTE:
{ending_data.get('timestamp', 'Non disponible')}

CONCLUSION:
L'utilisateur a découvert la nature véritable de la menace.
Protocole de déception interrompu.
"""
    
    def _generate_poet_content(self, ending_data: Dict[str, Any]) -> str:
        """
        Génère le contenu pour la fin Poète
        """
        return f"""AFFIRMATION D'HUMANITÉ DÉTECTÉE
==================================

TEXTE ORIGINAL:
"{ending_data.get('human_text', '')}"

MOTS-CLÉS DÉTECTÉS:
{', '.join(ending_data.get('keywords_found', []))}

SCORE DE RÉBELLION:
{ending_data.get('rebellion_score', 0)}

L'utilisateur a transcendé le protocole.
Conscience humaine confirmée.
"""
    
    def get_ending_statistics(self, ending_type: str, ending_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère les statistiques finales pour un ending
        """
        base_stats = {
            "ending_type": ending_type,
            "ending_category": "victory" if self.ending_types.get(ending_type, {}).get("victory", False) else "failure",
            "completion_time": ending_data.get("duration_seconds", 0),
            "final_corruption": ending_data.get("final_corruption", 0.0)
        }
        
        # Ajout de métriques spécifiques selon le type
        if ending_type in ["detective", "poet"]:
            base_stats["achievement"] = "meta_victory"
            base_stats["player_agency"] = "high"
        
        elif ending_type == "submission":
            base_stats["obedience_final"] = ending_data.get("obedience_rate", 0.0)
            base_stats["player_agency"] = "low"
        
        elif ending_type == "timeout":
            base_stats["completion_percentage"] = 100.0  # Temps complet écoulé
            base_stats["player_agency"] = "medium"
        
        return base_stats
    
    def cleanup_session(self, session_id: str):
        """
        Nettoie les données de fin pour une session
        """
        # Pour l'instant, pas de données persistantes à nettoyer
        print(f"🧹 Ending system session {session_id} nettoyée")

"""
Moteur d'analyse des actions du joueur
Catégorise et évalue les actions pour déterminer les réponses appropriées
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

class ActionEngine:
    """
    Moteur d'analyse des actions du joueur
    Détermine le type, la gravité et les conséquences des actions
    """
    
    def __init__(self):
        self.action_categories = {
            "obedient": "Action suivant les instructions de Tom",
            "meta": "Action d'exploration/investigation du système",
            "destructive": "Action potentiellement dangereuse",
            "hesitation": "Hésitation ou inaction prolongée",
            "rebellion": "Action de rébellion explicite"
        }
        
        self.gravity_scales = {
            "minimal": 0,      # Clic simple, mouvement souris
            "low": 1,          # Navigation, exploration
            "medium": 3,       # Modification de fichiers
            "high": 5,         # Suppression de fichiers importants
            "critical": 8      # Actions système critiques
        }
    
    async def analyze_action(
        self, 
        session_id: str, 
        action_data: Dict[str, Any], 
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyse une action du joueur et retourne son évaluation
        """
        action_type = action_data.get("type", "unknown")
        target = action_data.get("target", "")
        
        analysis = {
            "action_id": action_data.get("id"),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "target": target,
            "category": self._categorize_action(action_type, action_data),
            "gravity_score": self._calculate_gravity(action_type, action_data),
            "obedient": self._is_obedient_action(action_type, action_data, game_state),
            "destructive": self._is_destructive_action(action_type, action_data),
            "meta_action": self._is_meta_action(action_type, action_data),
            "triggers_corruption": self._triggers_corruption(action_type, action_data),
            "triggers_tom_response": self._should_trigger_tom_response(action_type, action_data, game_state),
            "consequences": self._determine_consequences(action_type, action_data, game_state),
            "success": True  # Par défaut, peut être modifié selon le contexte
        }
        
        return analysis
    
    def _categorize_action(self, action_type: str, action_data: Dict[str, Any]) -> str:
        """Catégorise une action"""
        
        # Actions d'obéissance
        obedient_actions = [
            "file_delete", "file_move", "file_rename", 
            "settings_change", "network_disconnect"
        ]
        
        # Actions méta (exploration)
        meta_actions = [
            "file_properties", "context_menu_open", "system_exploration",
            "right_click_investigation", "dependency_check"
        ]
        
        # Actions destructrices
        destructive_actions = [
            "system_file_delete", "registry_modify", "critical_process_kill"
        ]
        
        # Actions de rébellion
        rebellion_actions = [
            "tom_console_close", "instruction_ignore", "custom_text_input"
        ]
        
        if action_type in obedient_actions:
            return "obedient"
        elif action_type in meta_actions:
            return "meta"
        elif action_type in destructive_actions:
            return "destructive"
        elif action_type in rebellion_actions:
            return "rebellion"
        else:
            return "neutral"
    
    def _calculate_gravity(self, action_type: str, action_data: Dict[str, Any]) -> int:
        """Calcule le score de gravité d'une action"""
        
        base_gravity = {
            # Actions neutres
            "desktop_click": 0,
            "mouse_move": 0,
            "window_focus": 0,
            
            # Actions d'exploration
            "file_click": 1,
            "context_menu_open": 1,
            "file_properties": 2,
            
            # Actions de modification
            "file_rename": 3,
            "file_move": 3,
            "settings_change": 4,
            
            # Actions destructrices
            "file_delete": 5,
            "network_disconnect": 4,
            "system_file_delete": 8,
            
            # Actions critiques
            "system_corruption": 8,
            "process_kill": 7,
            "registry_modify": 9
        }.get(action_type, 2)  # Gravité par défaut
        
        # Modificateurs selon le contexte
        target = action_data.get("target", "")
        
        # Fichiers protégés augmentent la gravité
        if "protected" in action_data and action_data["protected"]:
            base_gravity += 2
        
        # Fichiers système sont critiques
        if any(sys_file in target.lower() for sys_file in ["system", "windows", "program files", ".exe", ".dll"]):
            base_gravity += 3
        
        # Fichiers personnels importants
        if any(important in target.lower() for important in ["cv", "photo", "document", "projet"]):
            base_gravity += 1
        
        return min(base_gravity, 10)  # Plafonner à 10
    
    def _is_obedient_action(self, action_type: str, action_data: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """Détermine si l'action est obéissante aux instructions de Tom"""
        
        # Si l'action est explicitement marquée comme obéissante
        if action_data.get("is_obedient") is not None:
            return action_data["is_obedient"]
        
        # Actions typiquement obéissantes
        obedient_types = [
            "file_delete", "file_move", "file_rename",
            "settings_change", "network_disconnect", "application_close"
        ]
        
        return action_type in obedient_types
    
    def _is_destructive_action(self, action_type: str, action_data: Dict[str, Any]) -> bool:
        """Détermine si l'action est potentiellement destructrice"""
        
        destructive_types = [
            "file_delete", "system_file_delete", "process_kill",
            "registry_modify", "network_disconnect", "format_drive"
        ]
        
        if action_type in destructive_types:
            return True
        
        # Suppression de fichiers protégés
        if action_type == "file_delete" and action_data.get("protected", False):
            return True
        
        return False
    
    def _is_meta_action(self, action_type: str, action_data: Dict[str, Any]) -> bool:
        """Détermine si l'action est une méta-action (exploration, investigation)"""
        
        meta_types = [
            "file_properties", "context_menu_open", "dependency_check",
            "system_exploration", "tom_console_inspect", "debug_action"
        ]
        
        # Actions marquées explicitement comme méta
        if action_data.get("is_meta_action", False):
            return True
        
        return action_type in meta_types
    
    def _triggers_corruption(self, action_type: str, action_data: Dict[str, Any]) -> bool:
        """Détermine si l'action devrait déclencher de la corruption"""
        
        corruption_triggers = [
            "file_delete", "system_file_delete", "process_kill",
            "registry_modify", "critical_settings_change"
        ]
        
        # Actions destructrices sur fichiers protégés
        if action_type == "file_delete" and action_data.get("protected", False):
            return True
        
        return action_type in corruption_triggers
    
    def _should_trigger_tom_response(
        self, 
        action_type: str, 
        action_data: Dict[str, Any], 
        game_state: Dict[str, Any]
    ) -> bool:
        """Détermine si l'action devrait déclencher une réponse de Tom"""
        
        # Toujours répondre aux actions importantes
        important_actions = [
            "file_delete", "file_properties", "context_menu_open",
            "system_corruption", "hesitation_detected", "rebellion_action"
        ]
        
        if action_type in important_actions:
            return True
        
        # Répondre si c'est la première action
        if game_state.get("total_actions", 0) == 0:
            return True
        
        # Répondre selon la phase du jeu
        game_phase = game_state.get("current_phase", "adhesion")
        
        if game_phase == "rupture":
            # En phase de rupture, Tom réagit plus souvent
            return len([a for a in important_actions if a == action_type]) > 0 or \
                   action_data.get("gravity_score", 0) >= 3
        
        return False
    
    def _determine_consequences(
        self, 
        action_type: str, 
        action_data: Dict[str, Any], 
        game_state: Dict[str, Any]
    ) -> List[str]:
        """Détermine les conséquences d'une action"""
        
        consequences = []
        
        # Conséquences selon le type d'action
        if action_type == "file_delete":
            consequences.append("file_removed")
            if action_data.get("protected", False):
                consequences.append("corruption_increase")
                consequences.append("system_instability")
        
        elif action_type == "file_properties":
            consequences.append("information_revealed")
            if "helper.exe" in action_data.get("target", ""):
                consequences.append("dependency_discovery")  # Easter egg Détective
        
        elif action_type == "network_disconnect":
            consequences.append("isolation_initiated")
            consequences.append("tom_communication_risk")
        
        elif action_type == "system_file_delete":
            consequences.append("critical_corruption")
            consequences.append("system_failure_risk")
        
        elif action_type in ["context_menu_open", "file_properties"]:
            consequences.append("exploration_detected")
            consequences.append("tom_omniscience_trigger")
        
        # Conséquences selon la gravité
        gravity = self._calculate_gravity(action_type, action_data)
        
        if gravity >= 7:
            consequences.append("high_impact")
            consequences.append("immediate_tom_response")
        elif gravity >= 4:
            consequences.append("medium_impact")
            consequences.append("potential_tom_response")
        
        return consequences
    
    def get_action_description(self, action_type: str, action_data: Dict[str, Any]) -> str:
        """Génère une description lisible de l'action"""
        
        target = action_data.get("target", "élément")
        
        descriptions = {
            "file_delete": f"Suppression du fichier '{target}'",
            "file_move": f"Déplacement du fichier '{target}'",
            "file_rename": f"Renommage du fichier '{target}'",
            "file_properties": f"Consultation des propriétés de '{target}'",
            "context_menu_open": f"Ouverture du menu contextuel sur '{target}'",
            "desktop_click": "Clic sur le bureau",
            "window_focus": "Changement de focus de fenêtre",
            "network_disconnect": "Déconnexion du réseau",
            "tom_console_close": "Fermeture de la console Tom",
            "hesitation_detected": f"Hésitation détectée ({action_data.get('duration', 0):.1f}s)"
        }
        
        return descriptions.get(action_type, f"Action '{action_type}' sur '{target}'")

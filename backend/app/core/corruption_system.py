"""
Système de corruption visuelle progressive
Gère l'évolution de la corruption de l'interface selon les actions du joueur
"""
import random
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

class CorruptionSystem:
    """
    Système de corruption pour REMOTE
    Gère la dégradation progressive de l'interface selon les actions destructrices
    """
    
    def __init__(self):
        self.session_corruption = {}  # Niveau de corruption par session
        self.corruption_history = {}  # Historique des corruptions
        self.max_corruption = 1.0
        
        # Types d'effets de corruption
        self.corruption_effects = {
            "pixel_corruption": {
                "min_level": 0.1,
                "intensity_scale": 1.0,
                "description": "Pixels morts et décoloration"
            },
            "widget_glitch": {
                "min_level": 0.2,
                "intensity_scale": 0.8,
                "description": "Dysfonctionnement des widgets"
            },
            "color_shift": {
                "min_level": 0.3,
                "intensity_scale": 0.6,
                "description": "Changement de palette de couleurs"
            },
            "background_decay": {
                "min_level": 0.4,
                "intensity_scale": 0.9,
                "description": "Dégradation du fond d'écran"
            },
            "interface_distortion": {
                "min_level": 0.6,
                "intensity_scale": 1.2,
                "description": "Déformation de l'interface"
            },
            "system_instability": {
                "min_level": 0.8,
                "intensity_scale": 1.5,
                "description": "Instabilité système critique"
            }
        }
    
    async def apply_corruption(
        self, 
        session_id: str, 
        action_analysis: Dict[str, Any], 
        current_level: float
    ) -> Optional[Dict[str, Any]]:
        """
        Applique de la corruption basée sur une action analysée
        """
        if not action_analysis.get("triggers_corruption", False):
            return None
        
        # Calculer l'augmentation de corruption
        corruption_increase = self._calculate_corruption_increase(action_analysis)
        
        # Nouveau niveau de corruption
        new_level = min(current_level + corruption_increase, self.max_corruption)
        
        # Générer les effets de corruption
        effects = self._generate_corruption_effects(new_level, corruption_increase)
        
        # Enregistrer l'historique
        self._record_corruption_event(session_id, action_analysis, new_level, effects)
        
        corruption_data = {
            "session_id": session_id,
            "old_level": current_level,
            "new_level": new_level,
            "increase": corruption_increase,
            "effects": effects,
            "timestamp": datetime.now().isoformat(),
            "trigger_action": action_analysis.get("type", "unknown")
        }
        
        # Stocker le niveau pour cette session
        self.session_corruption[session_id] = new_level
        
        return corruption_data
    
    def _calculate_corruption_increase(self, action_analysis: Dict[str, Any]) -> float:
        """
        Calcule l'augmentation de corruption basée sur une action
        """
        base_increase = 0.0
        
        # Facteur basé sur la gravité de l'action
        gravity_score = action_analysis.get("gravity_score", 0)
        base_increase = gravity_score * 0.02  # 2% par point de gravité
        
        # Multiplicateurs selon le type d'action
        action_type = action_analysis.get("type", "")
        multipliers = {
            "file_delete": 1.5,
            "system_file_delete": 3.0,
            "network_disconnect": 1.2,
            "process_kill": 2.0,
            "registry_modify": 2.5,
            "critical_settings_change": 2.2
        }
        
        base_increase *= multipliers.get(action_type, 1.0)
        
        # Bonus si fichier protégé
        if action_analysis.get("destructive", False):
            base_increase *= 1.3
        
        # Variation aléatoire pour imprévisibilité
        variation = random.uniform(0.8, 1.2)
        base_increase *= variation
        
        return min(base_increase, 0.15)  # Plafonner à 15% par action
    
    def _generate_corruption_effects(self, corruption_level: float, increase: float) -> List[Dict[str, Any]]:
        """
        Génère les effets visuels de corruption
        """
        effects = []
        current_time = datetime.now().isoformat()
        
        # Déterminer quels effets sont disponibles à ce niveau
        available_effects = [
            effect_name for effect_name, config in self.corruption_effects.items()
            if corruption_level >= config["min_level"]
        ]
        
        # Nombre d'effets basé sur le niveau et l'augmentation
        num_effects = min(
            len(available_effects),
            1 + int(corruption_level * 3) + (1 if increase > 0.05 else 0)
        )
        
        # Sélectionner et générer les effets
        selected_effects = random.sample(available_effects, min(num_effects, len(available_effects)))
        
        for effect_name in selected_effects:
            effect_config = self.corruption_effects[effect_name]
            intensity = min(
                (corruption_level - effect_config["min_level"]) * effect_config["intensity_scale"],
                1.0
            )
            
            effect = {
                "type": effect_name,
                "intensity": intensity,
                "timestamp": current_time,
                "description": effect_config["description"],
                "data": self._generate_effect_data(effect_name, intensity)
            }
            
            effects.append(effect)
        
        return effects
    
    def _generate_effect_data(self, effect_type: str, intensity: float) -> Dict[str, Any]:
        """
        Génère les données spécifiques pour un type d'effet
        """
        if effect_type == "pixel_corruption":
            return {
                "dead_pixel_count": int(intensity * 50),
                "color_shift_degree": intensity * 30,
                "corruption_pattern": random.choice(["random", "clustered", "lines"])
            }
        
        elif effect_type == "widget_glitch":
            return {
                "affected_widgets": random.sample(
                    ["clock", "weather", "music_player"], 
                    max(1, int(intensity * 3))
                ),
                "glitch_type": random.choice(["data_corruption", "display_error", "freeze"])
            }
        
        elif effect_type == "color_shift":
            palettes = ["sick_yellow", "toxic_green", "corrupted_red", "dead_blue"]
            return {
                "target_palette": random.choice(palettes),
                "shift_intensity": intensity,
                "animation_speed": max(0.5, 2.0 - intensity)
            }
        
        elif effect_type == "background_decay":
            return {
                "decay_type": random.choice(["fade", "tear", "pixelate"]),
                "decay_percentage": intensity * 100,
                "decay_pattern": random.choice(["edges", "center", "random"])
            }
        
        elif effect_type == "interface_distortion":
            return {
                "distortion_type": random.choice(["wave", "stretch", "fragment"]),
                "distortion_strength": intensity,
                "affected_areas": random.sample(
                    ["taskbar", "desktop", "windows", "widgets"],
                    max(1, int(intensity * 4))
                )
            }
        
        elif effect_type == "system_instability":
            return {
                "instability_type": random.choice(["freeze", "flicker", "crash_warning"]),
                "frequency": intensity * 10,
                "severity": "critical" if intensity > 0.8 else "moderate"
            }
        
        return {}
    
    def _record_corruption_event(
        self, 
        session_id: str, 
        action_analysis: Dict[str, Any], 
        new_level: float, 
        effects: List[Dict[str, Any]]
    ):
        """
        Enregistre un événement de corruption dans l'historique
        """
        if session_id not in self.corruption_history:
            self.corruption_history[session_id] = []
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "trigger_action": action_analysis.get("type", "unknown"),
            "action_target": action_analysis.get("target", ""),
            "gravity_score": action_analysis.get("gravity_score", 0),
            "corruption_level": new_level,
            "effects_applied": len(effects),
            "effect_types": [effect["type"] for effect in effects]
        }
        
        self.corruption_history[session_id].append(event)
        
        # Limiter l'historique à 50 événements
        if len(self.corruption_history[session_id]) > 50:
            self.corruption_history[session_id] = self.corruption_history[session_id][-50:]
    
    async def get_corruption_data_for_frontend(self, session_id: str) -> Dict[str, Any]:
        """
        Prépare les données de corruption pour le frontend
        """
        current_level = self.session_corruption.get(session_id, 0.0)
        history = self.corruption_history.get(session_id, [])
        
        # Générer les effets actuels basés sur le niveau
        current_effects = self._generate_corruption_effects(current_level, 0.0)
        
        return {
            "session_id": session_id,
            "current_level": current_level,
            "phase": self._get_corruption_phase(current_level),
            "current_effects": current_effects,
            "history_summary": {
                "total_events": len(history),
                "major_corruptions": len([e for e in history if e["corruption_level"] >= 0.5]),
                "recent_trend": self._calculate_corruption_trend(history)
            },
            "visual_settings": self._get_visual_settings(current_level)
        }
    
    def _get_corruption_phase(self, level: float) -> str:
        """Détermine la phase de corruption"""
        if level <= 0.2:
            return "minimal"
        elif level <= 0.4:
            return "noticeable"
        elif level <= 0.6:
            return "concerning"
        elif level <= 0.8:
            return "severe"
        else:
            return "catastrophic"
    
    def _calculate_corruption_trend(self, history: List[Dict[str, Any]]) -> str:
        """Calcule la tendance récente de corruption"""
        if len(history) < 3:
            return "stable"
        
        recent_levels = [event["corruption_level"] for event in history[-5:]]
        
        if len(recent_levels) < 2:
            return "stable"
        
        avg_change = sum(
            recent_levels[i] - recent_levels[i-1] 
            for i in range(1, len(recent_levels))
        ) / (len(recent_levels) - 1)
        
        if avg_change > 0.02:
            return "accelerating"
        elif avg_change < -0.01:
            return "recovering"
        else:
            return "stable"
    
    def _get_visual_settings(self, corruption_level: float) -> Dict[str, Any]:
        """
        Génère les paramètres visuels pour le frontend
        """
        return {
            "global_filter": {
                "hue_rotate": corruption_level * 180,
                "contrast": 1.0 + (corruption_level * 0.5),
                "brightness": 1.0 - (corruption_level * 0.3),
                "saturation": 1.0 + (corruption_level * 0.7)
            },
            "animation_speed": max(0.1, 1.0 - corruption_level),
            "glitch_frequency": corruption_level * 10,
            "instability_threshold": 0.8,
            "critical_mode": corruption_level >= 0.9
        }
    
    def cleanup_session(self, session_id: str):
        """
        Nettoie les données de corruption pour une session
        """
        if session_id in self.session_corruption:
            del self.session_corruption[session_id]
        
        if session_id in self.corruption_history:
            del self.corruption_history[session_id]
        
        print(f"🧹 Corruption session {session_id} nettoyée")
    
    def get_corruption_level(self, session_id: str) -> float:
        """
        Retourne le niveau actuel de corruption pour une session
        """
        return self.session_corruption.get(session_id, 0.0)
    
    def force_corruption_level(self, session_id: str, level: float):
        """
        Force un niveau de corruption (pour les tests/debug)
        """
        self.session_corruption[session_id] = max(0.0, min(level, self.max_corruption))
        print(f"🔧 Corruption forcée à {level:.2f} pour session {session_id}")

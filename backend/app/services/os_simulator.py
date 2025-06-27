"""
Service de simulation du système d'exploitation
Génère les éléments du bureau virtuel (fichiers, widgets, thèmes)
"""
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

class OSSimulator:
    """
    Simulateur de système d'exploitation pour REMOTE
    Génère procéduralement les éléments du bureau virtuel
    """
    
    def __init__(self):
        self.session_states = {}  # États OS par session
        self.default_theme = self._create_default_theme()
        self.file_templates = self._create_file_templates()
        self.widget_templates = self._create_widget_templates()
    
    async def get_os_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère l'état de l'OS pour une session
        """
        if session_id in self.session_states:
            return self.session_states[session_id]
        
        # Générer un nouvel état par défaut
        return await self.generate_initial_os(session_id)
    
    async def generate_initial_os(self, session_id: str, player_name: str = None) -> Dict[str, Any]:
        """
        Génère l'état initial de l'OS pour une nouvelle session
        """
        print(f"🖥️ Génération OS initial pour session {session_id}")
        
        os_state = {
            "session_id": session_id,
            "theme": self._generate_personalized_theme(player_name),
            "desktop": self._generate_desktop_layout(),
            "file_system": self._generate_file_system(player_name),
            "windows": [],
            "system_state": {
                "performance": 1.0,
                "network_status": "connected",
                "corruption_level": 0.0,
                "last_boot": datetime.now().isoformat()
            },
            "personalization": {
                "player_name": player_name or "Joueur",
                "session_info": f"Session : {player_name or 'Joueur'}"
            }
        }
        
        # Stocker l'état
        self.session_states[session_id] = os_state
        
        return os_state
    
    def update_os_state(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour l'état de l'OS pour une session
        """
        if session_id not in self.session_states:
            self.session_states[session_id] = self.generate_initial_os(session_id)
        
        # Appliquer les mises à jour de manière récursive
        self._deep_update(self.session_states[session_id], updates)
        
        return self.session_states[session_id]
    
    def apply_corruption_to_os(self, session_id: str, corruption_level: float, effects: List[Dict]) -> Dict[str, Any]:
        """
        Applique des effets de corruption à l'OS
        """
        if session_id not in self.session_states:
            return {}
        
        os_state = self.session_states[session_id]
        
        # Mettre à jour le niveau de corruption
        os_state["system_state"]["corruption_level"] = corruption_level
        
        # Appliquer les effets
        for effect in effects:
            self._apply_corruption_effect(os_state, effect)
        
        return os_state
    
    def cleanup_session(self, session_id: str):
        """
        Nettoie les données d'une session
        """
        if session_id in self.session_states:
            del self.session_states[session_id]
            print(f"🧹 Session OS {session_id} nettoyée")
    
    def _create_default_theme(self) -> Dict[str, Any]:
        """Crée le thème par défaut"""
        return {
            "name": "Digital Homestead",
            "background": {
                "name": "Sunset Beach",
                "type": "personal_photo",
                "description": "Coucher de soleil sur une plage",
                "color_palette": ["#FF6B35", "#F7931E", "#FFD23F", "#06BCC1"]
            },
            "accent_color": "#FF6B35",
            "mode": "light"
        }
    
    def _create_file_templates(self) -> List[Dict[str, Any]]:
        """Crée les templates de fichiers"""
        return [
            {
                "name": "CV-pour-candidature.pdf",
                "type": "document",
                "size": "2.3 MB",
                "protected": True,
                "icon": "pdf_file",
                "position": {"x": 80, "y": 200},
                "description": "Document important pour candidature"
            },
            {
                "name": "Photos_Vacances_Été.zip",
                "type": "archive",
                "size": "234.1 MB",
                "protected": True,
                "icon": "archive_file",
                "position": {"x": 220, "y": 180},
                "description": "Souvenirs de vacances"
            },
            {
                "name": "Projet_Passion.docx",
                "type": "document",
                "size": "8.2 MB",
                "protected": True,
                "icon": "word_file",
                "position": {"x": 85, "y": 260},
                "description": "Projet personnel important"
            },
            {
                "name": "Reçus_Garantie.zip",
                "type": "archive",
                "size": "15.7 MB",
                "protected": True,
                "icon": "archive_file",
                "position": {"x": 320, "y": 220},
                "description": "Documents administratifs"
            },
            {
                "name": "Musique_Playlist.m3u",
                "type": "playlist",
                "size": "2.1 KB",
                "protected": False,
                "icon": "music_file",
                "position": {"x": 180, "y": 320},
                "description": "Playlist musicale personnelle"
            }
        ]
    
    def _create_widget_templates(self) -> List[Dict[str, Any]]:
        """Crée les templates de widgets"""
        return [
            {
                "id": "clock_widget",
                "type": "clock",
                "position": {"x": 20, "y": 20},
                "size": {"width": 200, "height": 80},
                "data": {
                    "time": datetime.now().strftime("%H:%M"),
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "timezone": "Europe/Paris"
                }
            },
            {
                "id": "weather_widget",
                "type": "weather",
                "position": {"x": 20, "y": 120},
                "size": {"width": 180, "height": 100},
                "data": {
                    "location": "Le Mans",
                    "temperature": random.randint(18, 25),
                    "condition": "sunny",
                    "forecast": "Ensoleillé"
                }
            },
            {
                "id": "music_widget",
                "type": "music_player",
                "position": {"x": 250, "y": 20},
                "size": {"width": 220, "height": 60},
                "data": {
                    "current_song": "Lo-fi Hip Hop - Chill Beats",
                    "artist": "Study Music",
                    "playing": True,
                    "volume": 0.3
                }
            }
        ]
    
    def _generate_personalized_theme(self, player_name: str = None) -> Dict[str, Any]:
        """Génère un thème personnalisé"""
        themes = [
            {
                "name": "Digital Homestead",
                "background": {
                    "name": "Sunset Beach",
                    "type": "personal_photo",
                    "description": "Coucher de soleil sur une plage",
                    "color_palette": ["#FF6B35", "#F7931E", "#FFD23F", "#06BCC1"]
                },
                "accent_color": "#FF6B35"
            },
            {
                "name": "Forest Morning",
                "background": {
                    "name": "Misty Forest",
                    "type": "nature_photo",
                    "description": "Forêt brumeuse au petit matin",
                    "color_palette": ["#2D5A27", "#6B8E23", "#9ACD32", "#F0E68C"]
                },
                "accent_color": "#6B8E23"
            },
            {
                "name": "City Lights",
                "background": {
                    "name": "Night City",
                    "type": "urban_photo",
                    "description": "Lumières de la ville la nuit",
                    "color_palette": ["#1A1A2E", "#16213E", "#0F3460", "#E94560"]
                },
                "accent_color": "#E94560"
            }
        ]
        
        theme = random.choice(themes)
        theme["mode"] = "light"
        return theme
    
    def _generate_desktop_layout(self) -> Dict[str, Any]:
        """Génère la disposition du bureau"""
        return {
            "layout": "casual_organized",
            "widgets": self.widget_templates.copy(),
            "shortcuts": self.file_templates[:2].copy(),  # Premiers fichiers comme raccourcis
            "background": self.default_theme["background"]
        }
    
    def _generate_file_system(self, player_name: str = None) -> Dict[str, Any]:
        """Génère le système de fichiers"""
        
        # Personnaliser les noms de fichiers si un nom de joueur est fourni
        files = self.file_templates.copy()
        if player_name:
            for file in files:
                if "CV-pour-candidature" in file["name"]:
                    file["name"] = f"CV_{player_name}_2024.pdf"
        
        folders = [
            {
                "name": "Mes Documents",
                "type": "folder",
                "protected": True,
                "icon": "folder_documents",
                "position": {"x": 50, "y": 100},
                "items_count": random.randint(15, 30)
            },
            {
                "name": "Images",
                "type": "folder",
                "protected": True,
                "icon": "folder_images",
                "position": {"x": 50, "y": 160},
                "items_count": random.randint(50, 150)
            },
            {
                "name": "Corbeille",
                "type": "recycle_bin",
                "protected": False,
                "icon": "recycle_bin_empty",
                "position": {"x": 50, "y": 400},
                "items_count": 0
            }
        ]
        
        return {
            "documents": files,
            "desktop": folders,
            "system_files": self._generate_system_files()
        }
    
    def _generate_system_files(self) -> List[Dict[str, Any]]:
        """Génère les fichiers système (cachés)"""
        return [
            {
                "name": "helper.exe",
                "type": "executable",
                "size": "1.2 MB",
                "protected": False,
                "hidden": True,
                "description": "Assistant système",
                "dependencies": ["malware.exe"]  # Easter egg pour la fin Détective
            },
            {
                "name": "malware.exe",
                "type": "executable",
                "size": "890 KB",
                "protected": False,
                "hidden": True,
                "description": "Processus suspect",
                "malicious": True
            },
            {
                "name": "system_monitor.dll",
                "type": "library",
                "size": "2.1 MB",
                "protected": True,
                "hidden": True,
                "description": "Monitoring système"
            }
        ]
    
    def _apply_corruption_effect(self, os_state: Dict[str, Any], effect: Dict[str, Any]):
        """Applique un effet de corruption spécifique"""
        effect_type = effect.get("type", "unknown")
        intensity = effect.get("intensity", 0.5)
        
        if effect_type == "pixel_corruption":
            if "background" in os_state["desktop"]:
                if "corruption" not in os_state["desktop"]["background"]:
                    os_state["desktop"]["background"]["corruption"] = {}
                
                os_state["desktop"]["background"]["corruption"]["dead_pixels"] = intensity * 50
                os_state["desktop"]["background"]["corruption"]["color_shift"] = intensity * 0.3
        
        elif effect_type == "widget_glitch":
            for widget in os_state["desktop"]["widgets"]:
                if widget["type"] == "weather" and random.random() < intensity:
                    widget["corruption"] = {
                        "display_error": True,
                        "data_corruption": "ERROR_404_WEATHER"
                    }
                elif widget["type"] == "music_player" and random.random() < intensity:
                    widget["corruption"] = {
                        "playback_error": True,
                        "sound_distortion": intensity
                    }
        
        elif effect_type == "file_corruption":
            for file in os_state["file_system"]["documents"]:
                if random.random() < intensity * 0.3:  # 30% de chance max
                    file["corrupted"] = True
                    file["icon"] = "corrupted_file"
        
        elif effect_type == "color_shift":
            if "theme" in os_state:
                palettes = {
                    'sick_yellow': ['#D4AF37', '#DAA520', '#B8860B', '#FFD700'],
                    'toxic_green': ['#ADFF2F', '#9ACD32', '#32CD32', '#00FF00'],
                    'corrupted_red': ['#DC143C', '#B22222', '#8B0000', '#FF6347']
                }
                
                palette_name = random.choice(list(palettes.keys()))
                os_state["theme"]["corrupted_palette"] = {
                    "name": palette_name,
                    "colors": palettes[palette_name],
                    "intensity": intensity
                }
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Met à jour récursivement un dictionnaire"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

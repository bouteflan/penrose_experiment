"""
Modules core pour le jeu REMOTE
"""

from .action_engine import ActionEngine
from .corruption_system import CorruptionSystem
from .ending_system import EndingSystem

__all__ = [
    "ActionEngine",
    "CorruptionSystem", 
    "EndingSystem"
]

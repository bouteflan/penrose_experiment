"""
Application REMOTE - Thriller psychologique
Backend FastAPI avec intégration IA
"""

__version__ = "1.0.0"
__description__ = "Backend pour le jeu REMOTE - Thriller psychologique explorant les biais cognitifs"
__author__ = "Équipe de développement REMOTE"

from .config import settings
from .main import app

__all__ = [
    "settings",
    "app"
]

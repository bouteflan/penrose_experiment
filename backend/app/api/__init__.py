"""
Routes API pour le jeu REMOTE
"""

from .websocket import router as websocket_router
from .game import router as game_router
from .experiment import router as experiment_router

__all__ = [
    "websocket_router",
    "game_router", 
    "experiment_router"
]

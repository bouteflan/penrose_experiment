"""
Configuration principale de l'application REMOTE
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Configuration de base
    app_name: str = "REMOTE Psychological Thriller Game"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Configuration serveur
    host: str = "localhost"
    port: int = 8000
    reload: bool = True
    
    # Configuration base de données
    database_url: str = "sqlite:///./database/game.db"
    
    # Configuration OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # Configuration sécurité
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuration CORS
    allowed_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Configuration WebSocket
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # Configuration expérimentale
    collect_experiment_data: bool = True
    anonymize_data: bool = True
    
    # Configuration Tom AI
    tom_personality_condition: str = "confident"  # "confident" ou "oracle"
    tom_response_delay_min: float = 0.5  # Délai minimum entre les réponses
    tom_response_delay_max: float = 2.0  # Délai maximum entre les réponses
    tom_typing_speed: float = 0.05  # Vitesse de frappe simulée (secondes par caractère)
    
    # Configuration du jeu
    game_duration_minutes: int = 10
    corruption_intensity_max: float = 1.0
    bias_measurement_interval: int = 5  # Secondes entre les mesures
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale des paramètres
settings = Settings()


def get_settings() -> Settings:
    """Retourne l'instance des paramètres"""
    return settings


def validate_openai_config() -> bool:
    """Valide la configuration OpenAI"""
    if not settings.openai_api_key:
        print("⚠️  ATTENTION: Clé API OpenAI non configurée")
        print("   Ajoutez OPENAI_API_KEY dans votre fichier .env")
        return False
    return True


def print_startup_info():
    """Affiche les informations de démarrage"""
    print(f"🎮 {settings.app_name} v{settings.app_version}")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🚀 Server: http://{settings.host}:{settings.port}")
    print(f"🤖 Tom condition: {settings.tom_personality_condition}")
    print(f"📊 Data collection: {settings.collect_experiment_data}")
    
    if validate_openai_config():
        print("✅ OpenAI configuré correctement")
    else:
        print("❌ Configuration OpenAI manquante")

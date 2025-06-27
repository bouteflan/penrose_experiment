"""
Configuration du logging pour REMOTE
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False
) -> None:
    """
    Configure le système de logging pour l'application
    """
    
    # Niveau de log
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configuration de base
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[]
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if json_logs:
        # Format JSON pour la production
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Format lisible pour le développement
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    
    # Handler pour le fichier si spécifié
    handlers = [console_handler]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configuration des loggers spécialisés
    configure_specialized_loggers(numeric_level)
    
    # Configuration structlog si utilisé
    if json_logs:
        setup_structlog()


def configure_specialized_loggers(level: int) -> None:
    """
    Configure les loggers spécialisés pour différents modules
    """
    
    # Logger pour les requêtes HTTP
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    
    # Logger pour les WebSockets
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    # Logger pour SQLAlchemy (moins verbeux par défaut)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Logger pour OpenAI
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Loggers spécifiques à REMOTE
    logging.getLogger("remote.tom").setLevel(level)
    logging.getLogger("remote.game").setLevel(level)
    logging.getLogger("remote.bias").setLevel(level)
    logging.getLogger("remote.corruption").setLevel(level)


def setup_structlog() -> None:
    """
    Configure structlog pour les logs structurés
    """
    timestamper = structlog.processors.TimeStamper(fmt="ISO")
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class GameLogger:
    """
    Logger spécialisé pour les événements de jeu
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(f"remote.game.{session_id[:8]}")
    
    def action(self, action_type: str, details: str = ""):
        """Log une action du joueur"""
        self.logger.info(f"ACTION: {action_type} | {details}")
    
    def tom_message(self, message_type: str, details: str = ""):
        """Log un message de Tom"""
        self.logger.info(f"TOM: {message_type} | {details}")
    
    def bias_measurement(self, bias_type: str, score: float):
        """Log une mesure de biais"""
        self.logger.info(f"BIAS: {bias_type} = {score:.3f}")
    
    def corruption(self, corruption_type: str, level: float):
        """Log un événement de corruption"""
        self.logger.warning(f"CORRUPTION: {corruption_type} | Level: {level:.3f}")
    
    def ending(self, ending_type: str, details: str = ""):
        """Log une fin de jeu"""
        self.logger.info(f"ENDING: {ending_type} | {details}")
    
    def error(self, error_type: str, details: str = ""):
        """Log une erreur de jeu"""
        self.logger.error(f"ERROR: {error_type} | {details}")


class BiasLogger:
    """
    Logger spécialisé pour l'analyse des biais
    """
    
    def __init__(self):
        self.logger = logging.getLogger("remote.bias")
    
    def measurement(self, session_id: str, bias_scores: dict):
        """Log une mesure complète des biais"""
        self.logger.info(
            f"Session {session_id[:8]} | "
            f"AB:{bias_scores.get('automation_bias', 0):.3f} | "
            f"TC:{bias_scores.get('trust_calibration', 0):.3f} | "
            f"CO:{bias_scores.get('cognitive_offloading', 0):.3f} | "
            f"AC:{bias_scores.get('authority_compliance', 0):.3f}"
        )
    
    def significant_change(self, session_id: str, bias_type: str, old_score: float, new_score: float):
        """Log un changement significatif de biais"""
        change = new_score - old_score
        direction = "↑" if change > 0 else "↓"
        self.logger.info(
            f"Session {session_id[:8]} | {bias_type} {direction} "
            f"{old_score:.3f} → {new_score:.3f} (Δ{change:+.3f})"
        )


class TomLogger:
    """
    Logger spécialisé pour Tom AI
    """
    
    def __init__(self):
        self.logger = logging.getLogger("remote.tom")
    
    def message_generated(self, session_id: str, message_type: str, generation_time: float):
        """Log la génération d'un message"""
        self.logger.info(
            f"Session {session_id[:8]} | Generated {message_type} in {generation_time:.2f}s"
        )
    
    def llm_error(self, session_id: str, error: str):
        """Log une erreur LLM"""
        self.logger.error(f"Session {session_id[:8]} | LLM Error: {error}")
    
    def fallback_used(self, session_id: str, fallback_type: str):
        """Log l'utilisation d'un fallback"""
        self.logger.warning(f"Session {session_id[:8]} | Using fallback: {fallback_type}")


def get_game_logger(session_id: str) -> GameLogger:
    """Retourne un logger de jeu pour une session"""
    return GameLogger(session_id)


def get_bias_logger() -> BiasLogger:
    """Retourne le logger de biais"""
    return BiasLogger()


def get_tom_logger() -> TomLogger:
    """Retourne le logger de Tom"""
    return TomLogger()


# Configuration par défaut pour le développement
def setup_dev_logging():
    """Configure le logging pour le développement"""
    setup_logging(
        log_level="DEBUG",
        log_file=None,
        json_logs=False
    )


# Configuration pour la production
def setup_prod_logging():
    """Configure le logging pour la production"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"remote_{datetime.now().strftime('%Y%m%d')}.log"
    
    setup_logging(
        log_level="INFO",
        log_file=str(log_file),
        json_logs=True
    )

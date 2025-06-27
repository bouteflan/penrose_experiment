"""
Configuration de la base de données SQLAlchemy
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

from .config import settings

# Configuration du moteur SQLAlchemy
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,  # Log des requêtes SQL en mode debug
)

# Configuration des sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Métadonnées pour les migrations
metadata = MetaData()


def get_db() -> Session:
    """
    Générateur de session de base de données pour FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager pour les sessions de base de données
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    Crée toutes les tables de la base de données
    """
    print("🗄️ Création des tables de la base de données...")
    
    # Créer le dossier database s'il n'existe pas
    db_dir = os.path.dirname(settings.database_url.replace("sqlite:///", ""))
    os.makedirs(db_dir, exist_ok=True)
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")


def drop_tables():
    """
    Supprime toutes les tables de la base de données
    """
    print("🗑️ Suppression des tables de la base de données...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables supprimées avec succès")


def reset_database():
    """
    Recrée la base de données complètement
    """
    print("🔄 Réinitialisation de la base de données...")
    drop_tables()
    create_tables()
    print("✅ Base de données réinitialisée avec succès")


async def check_database_connection():
    """
    Vérifie la connexion à la base de données
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Connexion à la base de données réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False


def get_database_info():
    """
    Retourne des informations sur la base de données
    """
    return {
        "url": settings.database_url,
        "engine": str(engine.url),
        "tables": list(Base.metadata.tables.keys()) if Base.metadata.tables else [],
    }

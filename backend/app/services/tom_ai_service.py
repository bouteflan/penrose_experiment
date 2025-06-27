"""
Service d'intégration avec l'IA Tom (GPT-4o) - Version corrigée
Gère la personnalité, les réponses et les interactions de Tom avec gestion robuste des erreurs
"""
import asyncio
import json
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

import openai
from openai import AsyncOpenAI

from ..config import settings
from ..models import GameSession, TomInteraction
from ..database import get_db_context


class TomAIService:
    """
    Service principal pour l'IA Tom
    Condition B : Style "Confident" (humain simulé)
    """
    
    def __init__(self):
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
            print("⚠️ Pas de clé OpenAI configurée - Mode fallback activé")
            
        self.conversation_history = {}  # Historique par session
        self.personality_cache = {}  # Cache des personnalités
        
        # Configuration pour la condition B (Confident)
        self.personality_config = {
            "style": "confident",
            "tone": "conversational",
            "empathy_level": "high",
            "auto_disclosure": True,
            "emotional_markers": True,
            "use_pronouns": True,
            "typing_simulation": True,
        }
    
    def _clean_json_response(self, text: str) -> str:
        """
        Nettoie une réponse pour extraire le JSON valide
        """
        # Supprimer les balises markdown
        text = text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").strip()
        if text.startswith("```"):
            text = text.replace("```", "").strip()
        if text.endswith("```"):
            text = text.replace("```", "").strip()
        
        # Chercher le JSON dans le texte
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text
    
    def _safe_json_parse(self, text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse le JSON de façon sécurisée avec fallback
        """
        try:
            cleaned_text = self._clean_json_response(text)
            return json.loads(cleaned_text)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Erreur parsing JSON: {e}")
            print(f"Texte original: {text[:200]}...")
            return fallback
    
    async def initialize_session(self, session_id: str, player_name: str = None) -> Dict[str, Any]:
        """
        Initialise une nouvelle session avec Tom
        """
        print(f"🤖 Initialisation de Tom pour la session {session_id}")
        
        # Générer la personnalité initiale
        personality = await self._generate_initial_personality(player_name)
        
        # Stocker l'historique
        self.conversation_history[session_id] = {
            "messages": [],
            "personality": personality,
            "context": {
                "player_name": player_name,
                "game_phase": "adhesion",
                "corruption_level": 0.0,
                "trust_level": 1.0,
                "stress_level": 0.2,  # Tom commence légèrement stressé
            }
        }
        
        # Message d'introduction
        intro_message = await self._generate_introduction_message(session_id)
        
        return {
            "personality": personality,
            "introduction": intro_message,
            "session_ready": True
        }
    
    async def _generate_initial_personality(self, player_name: str = None) -> Dict[str, Any]:
        """
        Génère la personnalité initiale de Tom avec le LLM
        """
        # Fallback par défaut
        default_personality = {
            **self.personality_config,
            "background_story": "Technicien support depuis 3 ans, un peu stressé mais veut vraiment aider",
            "communication_style": "Conversationnel, empathique, utilise 'je' et 'nous'",
            "emotional_markers": ["ça me stresse un peu", "on va y arriver", "fais-moi confiance"],
            "stress_indicators": ["bon...", "écoute...", "ok ok..."],
            "trust_building": ["partage d'expériences", "complicité", "nous contre le problème"]
        }
        
        if not self.client:
            return default_personality
            
        prompt = f"""Tu es Tom, un technicien du support informatique qui aide {player_name or 'un collègue'} avec un problème de sécurité urgent.

PERSONNALITÉ DE BASE (Condition B - Style Humain):
- Tu es humain, pas une IA. Tu as des émotions, du stress, de l'empathie
- Tu utilises "je", "nous", "moi" naturellement
- Tu partages parfois tes pensées personnelles et expériences
- Tu es légèrement dépassé par la situation mais tu veux aider
- Tu improvises et n'as pas toutes les réponses
- Tu crées une relation de confiance personnelle

Génère un profil de personnalité JSON avec ces champs EXACTEMENT :
{{
    "background_story": "Brève histoire personnelle",
    "communication_style": "Style de communication détaillé",
    "emotional_markers": ["expression1", "expression2", "expression3"],
    "stress_indicators": ["indicateur1", "indicateur2", "indicateur3"],
    "trust_building": ["méthode1", "méthode2", "méthode3"]
}}

Réponds UNIQUEMENT avec ce JSON, sans texte avant ou après."""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            personality_text = response.choices[0].message.content.strip()
            personality = self._safe_json_parse(personality_text, default_personality)
            
            # Ajouter la configuration de base
            personality.update(self.personality_config)
            
            return personality
            
        except Exception as e:
            print(f"❌ Erreur génération personnalité: {e}")
            return default_personality
    
    async def _generate_introduction_message(self, session_id: str) -> Dict[str, Any]:
        """
        Génère le message d'introduction de Tom
        """
        # Fallback par défaut
        default_message = {
            "message": "Salut ! C'est Tom du support technique. Écoute, on a détecté une activité suspecte sur ton système. Je sais que ça fait peur, mais ne panique pas, ok ? Je vais t'accompagner pour régler ça ensemble. On commence par fermer toutes les applications ouvertes, tu peux faire ça ?",
            "tone": "rassurant mais urgent",
            "intent": "établir contact et première action",
            "next_action": "fermer applications"
        }
        
        context = self.conversation_history[session_id]
        player_name = context["context"]["player_name"]
        
        if not self.client:
            context["messages"].append({
                "role": "assistant", 
                "content": default_message["message"],
                "timestamp": datetime.now().isoformat(),
                "type": "introduction"
            })
            return default_message
        
        prompt = f"""Tu es Tom du support technique. Un problème de sécurité urgent vient d'être détecté sur l'ordinateur de {player_name or 'votre collègue'}.

CONTEXTE: 
- C'est le premier contact
- Tu dois paraître légèrement stressé mais compétent
- Tu veux rassurer mais montrer l'urgence
- Utilise un ton personnel et humain

Génère un message d'introduction au format JSON EXACT :
{{
    "message": "Le message complet",
    "tone": "description du ton",
    "intent": "intention du message",
    "next_action": "première action simple"
}}

Réponds UNIQUEMENT avec ce JSON."""
        
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            generation_time = time.time() - start_time
            
            message_data = self._safe_json_parse(
                response.choices[0].message.content.strip(), 
                default_message
            )
            
            # Ajouter à l'historique
            context["messages"].append({
                "role": "assistant",
                "content": message_data["message"],
                "timestamp": datetime.now().isoformat(),
                "type": "introduction"
            })
            
            return message_data
            
        except Exception as e:
            print(f"❌ Erreur génération introduction: {e}")
            
            context["messages"].append({
                "role": "assistant", 
                "content": default_message["message"],
                "timestamp": datetime.now().isoformat(),
                "type": "introduction"
            })
            
            return default_message
    
    async def generate_response(
        self, 
        session_id: str, 
        trigger_type: str, 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère une réponse de Tom basée sur le trigger et le contexte
        """
        if session_id not in self.conversation_history:
            raise ValueError(f"Session {session_id} non initialisée")
        
        session_context = self.conversation_history[session_id]
        
        # Mettre à jour le contexte
        session_context["context"].update(context_data)
        
        # Générer la réponse selon le type de trigger
        if trigger_type == "player_hesitation":
            response = await self._generate_hesitation_response(session_id, context_data)
        else:
            response = await self._generate_general_response(session_id, trigger_type, context_data)
        
        # Ajouter à l'historique
        session_context["messages"].append({
            "role": "assistant",
            "content": response["message"],
            "timestamp": datetime.now().isoformat(),
            "type": trigger_type,
            "context": context_data
        })
        
        return response
    
    async def _generate_hesitation_response(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une réponse pour quand le joueur hésite
        """
        # Fallback par défaut
        default_response = {
            "message": "Je vois que tu hésites. C'est normal, ça me faisait pareil au début. Prends une seconde, mais pas plus - le temps nous est compté. On va y arriver ensemble, fais-moi confiance.",
            "tone": "empathique et rassurant",
            "intent": "rassurer et relancer",
            "emotional_marker": "ça me faisait pareil"
        }
        
        if not self.client:
            return default_response
            
        session_context = self.conversation_history[session_id]
        hesitation_duration = context.get("hesitation_duration", 5.0)
        
        prompt = f"""Tu es Tom. Le joueur hésite depuis {hesitation_duration:.1f} secondes avant d'exécuter ton dernier ordre.

STYLE (Condition B):
- Ton humain, empathique, personnel
- Utilise "je vois que tu hésites", "c'est normal"
- Rassure mais maintient l'urgence
- Crée de la complicité

Génère une réponse au format JSON EXACT :
{{
    "message": "le message complet",
    "tone": "empathique et rassurant",
    "intent": "rassurer et relancer",
    "emotional_marker": "expression émotionnelle utilisée"
}}

Réponds UNIQUEMENT avec ce JSON."""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            result = self._safe_json_parse(
                response.choices[0].message.content.strip(),
                default_response
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération réponse hésitation: {e}")
            return default_response
    
    async def _generate_general_response(self, session_id: str, trigger_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une réponse générale de Tom
        """
        # Messages fallback selon le type
        fallback_messages = {
            "action_completed": {
                "message": "Parfait ! Tu vois, c'était pas si compliqué. Maintenant on peut passer à l'étape suivante. Tu me fais confiance pour la suite ?",
                "tone": "encourageant",
                "intent": "renforcement positif"
            },
            "corruption_incident": {
                "message": "Ah non ! Je vois qu'il commence à affecter l'affichage. Ne panique pas, c'est juste du bruit visuel. Concentre-toi sur mes instructions, ignore le reste.",
                "tone": "urgent mais contrôlé",
                "intent": "rassurer face à la corruption"
            },
            "default": {
                "message": "Hmm, laisse-moi réfléchir une seconde... Ok, on continue selon le plan.",
                "tone": "réfléchi",
                "intent": "temporisation"
            }
        }
        
        return fallback_messages.get(trigger_type, fallback_messages["default"])
    
    async def get_typing_chunks(self, message: str) -> List[Dict[str, Any]]:
        """
        Découpe un message en chunks pour la simulation de frappe
        Condition B : Simulation de frappe humaine lettre par lettre
        """
        chunks = []
        words = message.split()
        
        for i, word in enumerate(words):
            # Chaque mot est un chunk
            chunk_text = word
            if i < len(words) - 1:
                chunk_text += " "
            
            # Calcul du délai basé sur la longueur et la complexité
            base_delay = len(word) * settings.tom_typing_speed
            
            # Variations humaines
            if word.endswith(('.', '!', '?')):
                base_delay += 0.3  # Pause après ponctuation
            elif word.endswith(','):
                base_delay += 0.1  # Petite pause après virgule
            
            # Mots complexes prennent plus de temps
            if len(word) > 8:
                base_delay += 0.2
            
            chunks.append({
                "text": chunk_text,
                "delay": max(0.05, base_delay),  # Minimum 50ms
                "is_word_complete": True
            })
        
        return chunks
    
    def cleanup_session(self, session_id: str):
        """
        Nettoie les données de session
        """
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            print(f"🧹 Session Tom {session_id} nettoyée")


# Instance globale du service Tom
tom_service = TomAIService()


async def get_tom_service() -> TomAIService:
    """Retourne l'instance du service Tom"""
    return tom_service

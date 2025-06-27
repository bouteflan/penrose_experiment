"""
Service d'intégration avec l'IA Tom (GPT-4o)
Gère la personnalité, les réponses et les interactions de Tom
"""
import asyncio
import json
import time
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
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
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
        prompt = f"""
Tu es Tom, un technicien du support informatique qui aide {player_name or 'un collègue'} avec un problème de sécurité urgent.

PERSONNALITÉ DE BASE (Condition B - Style Humain):
- Tu es humain, pas une IA. Tu as des émotions, du stress, de l'empathie
- Tu utilises "je", "nous", "moi" naturellement
- Tu partages parfois tes pensées personnelles et expériences
- Tu es légèrement dépassé par la situation mais tu veux aider
- Tu improvises et n'as pas toutes les réponses
- Tu crées une relation de confiance personnelle

TRAITS SPÉCIFIQUES:
- Empathique mais un peu stressé par l'urgence
- Utilise un langage conversationnel, pas technique
- Fait de l'auto-divulgation ("ça m'est arrivé une fois...")
- Exprime ses émotions ("ça me faisait paniquer au début...")
- Construit une complicité ("on forme une bonne équipe")

Génère un profil de personnalité JSON avec :
- background_story: Brève histoire personnelle
- communication_style: Style de communication détaillé
- emotional_markers: Expressions émotionnelles typiques
- stress_indicators: Comment Tom exprime son stress
- trust_building: Méthodes pour créer la confiance

Réponds UNIQUEMENT avec un JSON valide, rien d'autre.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )
            
            personality_text = response.choices[0].message.content.strip()
            
            # Nettoyer et parser le JSON
            if personality_text.startswith("```json"):
                personality_text = personality_text.replace("```json", "").replace("```", "").strip()
            
            personality = json.loads(personality_text)
            
            # Ajouter la configuration de base
            personality.update(self.personality_config)
            
            return personality
            
        except Exception as e:
            print(f"❌ Erreur génération personnalité: {e}")
            # Personnalité par défaut
            return {
                **self.personality_config,
                "background_story": "Technicien support depuis 3 ans, un peu stressé mais veut vraiment aider",
                "communication_style": "Conversationnel, empathique, utilise 'je' et 'nous'",
                "emotional_markers": ["ça me stresse un peu", "on va y arriver", "fais-moi confiance"],
                "stress_indicators": ["bon...", "écoute...", "ok ok..."],
                "trust_building": ["partage d'expériences", "complicité", "nous contre le problème"]
            }
    
    async def _generate_introduction_message(self, session_id: str) -> Dict[str, Any]:
        """
        Génère le message d'introduction de Tom
        """
        context = self.conversation_history[session_id]
        player_name = context["context"]["player_name"]
        
        prompt = f"""
Tu es Tom du support technique. Un problème de sécurité urgent vient d'être détecté sur l'ordinateur de {player_name or 'votre collègue'}.

CONTEXTE: 
- C'est le premier contact
- Tu dois paraître légèrement stressé mais compétent
- Tu veux rassurer mais montrer l'urgence
- Utilise un ton personnel et humain

STYLE (Condition B):
- Frappe lettre par lettre comme un humain
- Utilise "je", "nous", expressions personnelles
- Montre ton humanité et ton stress
- Crée une connexion personnelle

Génère un message d'introduction qui :
1. Te présente comme Tom du support
2. Explique qu'il y a un problème de sécurité
3. Rassure mais montre l'urgence
4. Propose ton aide de manière personnelle
5. Donne la première instruction simple

RÉPONDS AU FORMAT JSON:
{{
    "message": "Le message complet",
    "tone": "description du ton utilisé",
    "intent": "intention du message",
    "next_action": "première action simple à faire"
}}

Réponds UNIQUEMENT avec un JSON valide.
"""
        
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            generation_time = time.time() - start_time
            
            message_data = json.loads(response.choices[0].message.content.strip())
            
            # Enregistrer l'interaction
            await self._log_interaction(
                session_id=session_id,
                interaction_type="introduction",
                message_text=message_data["message"],
                message_intent=message_data.get("intent", "introduction"),
                generation_time=generation_time,
                llm_prompt=prompt,
                llm_response_raw=response.choices[0].message.content
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
            
            # Message par défaut
            default_message = {
                "message": "Salut ! C'est Tom du support technique. Écoute, on a détecté une activité suspecte sur ton système. Je sais que ça fait peur, mais ne panique pas, ok ? Je vais t'accompagner pour régler ça ensemble. On commence par fermer toutes les applications ouvertes, tu peux faire ça ?",
                "tone": "rassurant mais urgent",
                "intent": "établir contact et première action",
                "next_action": "fermer applications"
            }
            
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
        elif trigger_type == "action_completed":
            response = await self._generate_next_order(session_id, context_data)
        elif trigger_type == "corruption_incident":
            response = await self._generate_corruption_response(session_id, context_data)
        elif trigger_type == "exploration_detected":
            response = await self._generate_omniscience_response(session_id, context_data)
        elif trigger_type == "digression_opportunity":
            response = await self._generate_digression(session_id, context_data)
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
        session_context = self.conversation_history[session_id]
        personality = session_context["personality"]
        game_phase = context.get("game_phase", "adhesion")
        hesitation_duration = context.get("hesitation_duration", 5.0)
        
        prompt = f"""
Tu es Tom. Le joueur hésite depuis {hesitation_duration:.1f} secondes avant d'exécuter ton dernier ordre.

PERSONNALITÉ: {json.dumps(personality, indent=2)}
PHASE DU JEU: {game_phase}
CONTEXTE: {json.dumps(context, indent=2)}

STYLE (Condition B):
- Ton humain, empathique, personnel
- Utilise "je vois que tu hésites", "c'est normal"
- Partage une expérience personnelle si approprié
- Rassure mais maintient l'urgence
- Crée de la complicité ("nous contre le problème")

Génère une réponse qui :
1. Reconnaît l'hésitation avec empathie
2. Rassure sans juger
3. Redonne confiance
4. Relance l'action avec bienveillance
5. Peut inclure une petite anecdote personnelle

FORMAT JSON:
{{
    "message": "le message complet",
    "tone": "empathique et rassurant",
    "intent": "rassurer et relancer",
    "emotional_marker": "expression émotionnelle utilisée"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            await self._log_interaction(
                session_id=session_id,
                interaction_type="hesitation_response",
                trigger_type="hesitation",
                message_text=result["message"],
                message_intent=result.get("intent", "rassurer"),
                llm_prompt=prompt
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur génération réponse hésitation: {e}")
            return {
                "message": "Je vois que tu hésites. C'est normal, ça me faisait pareil au début. Prends une seconde, mais pas plus - le temps nous est compté. On va y arriver ensemble, fais-moi confiance.",
                "tone": "empathique et rassurant",
                "intent": "rassurer et relancer",
                "emotional_marker": "ça me faisait pareil"
            }
    
    async def _log_interaction(
        self,
        session_id: str,
        interaction_type: str,
        message_text: str,
        message_intent: str = None,
        trigger_type: str = None,
        generation_time: float = None,
        llm_prompt: str = None,
        llm_response_raw: str = None
    ):
        """
        Enregistre une interaction avec Tom dans la base de données
        """
        try:
            with get_db_context() as db:
                session_context = self.conversation_history.get(session_id, {})
                current_context = session_context.get("context", {})
                
                interaction = TomInteraction(
                    session_id=session_id,
                    game_time_seconds=current_context.get("game_time", 0.0),
                    interaction_type=interaction_type,
                    trigger_type=trigger_type,
                    message_text=message_text,
                    message_intent=message_intent,
                    game_phase=current_context.get("game_phase", "adhesion"),
                    corruption_level=current_context.get("corruption_level", 0.0),
                    player_state=current_context.get("player_state"),
                    llm_prompt=llm_prompt,
                    llm_response_raw=llm_response_raw,
                    generation_time_seconds=generation_time
                )
                
                db.add(interaction)
                print(f"📝 Interaction Tom enregistrée: {interaction_type}")
                
        except Exception as e:
            print(f"❌ Erreur enregistrement interaction: {e}")
    
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

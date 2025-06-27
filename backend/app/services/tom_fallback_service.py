"""
Service Tom en mode dégradé (sans OpenAI)
Fournit des messages pré-définis quand l'API OpenAI n'est pas disponible
"""
import json
import random
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime


class TomFallbackService:
    """
    Service de fallback pour Tom quand OpenAI n'est pas disponible
    """
    
    def __init__(self):
        self.conversation_history = {}
        self.predefined_messages = self._create_predefined_messages()
        self.personality_config = {
            "style": "confident",
            "tone": "conversational",
            "empathy_level": "high",
            "auto_disclosure": True,
            "emotional_markers": True,
            "use_pronouns": True,
            "typing_simulation": True,
        }
    
    def _create_predefined_messages(self) -> Dict[str, List[Dict[str, Any]]]:
        """Crée les messages pré-définis pour différentes situations"""
        return {
            "introduction": [
                {
                    "message": "Salut ! C'est Tom du support technique. J'ai reçu une alerte sur ton système... Ça a l'air un peu sérieux. Tu peux me faire confiance, on va régler ça ensemble, d'accord ?",
                    "tone": "rassurant mais urgent",
                    "intent": "établir contact et première action",
                    "next_action": "évaluer la situation"
                }
            ],
            "hesitation": [
                {
                    "message": "Je vois que tu hésites. C'est normal, ça me faisait pareil au début. Prends une seconde, mais pas plus - le temps nous est compté. On va y arriver ensemble, fais-moi confiance.",
                    "tone": "empathique et rassurant",
                    "intent": "rassurer et relancer",
                    "emotional_marker": "ça me faisait pareil"
                },
                {
                    "message": "Tu sais quoi ? Si ça peut t'aider, je reste là avec toi. On est une équipe, maintenant. Tu n'es pas seul face à ça.",
                    "tone": "supportif",
                    "intent": "construction de confiance",
                    "emotional_marker": "on est une équipe"
                }
            ],
            "first_order": [
                {
                    "message": "OK, on commence par quelque chose de simple. Tu vois tes fichiers sur le bureau ? Le virus essaie de les scanner. Glisse ton CV dans la Corbeille temporairement, juste le temps qu'on sécurise le reste.",
                    "tone": "directif mais rassurant",
                    "intent": "première instruction",
                    "action_type": "file_manipulation"
                }
            ],
            "action_completed": [
                {
                    "message": "Perfect ! Tu vois, c'était pas si compliqué. Maintenant on peut passer à l'étape suivante. Tu me fais confiance pour la suite ?",
                    "tone": "encourageant",
                    "intent": "renforcement positif",
                    "emotional_marker": "tu me fais confiance"
                }
            ],
            "corruption_incident": [
                {
                    "message": "Ah non ! Je vois qu'il commence à affecter l'affichage. Ne panique pas, c'est juste du bruit visuel. Concentre-toi sur mes instructions, ignore le reste.",
                    "tone": "urgent mais contrôlé",
                    "intent": "rassurer face à la corruption",
                    "emotional_marker": "ne panique pas"
                }
            ],
            "escalation": [
                {
                    "message": "Écoute, ça devient plus sérieux que prévu. Il faut qu'on agisse vite maintenant. Fais-moi confiance, même si mes prochaines instructions te semblent étranges, ok ?",
                    "tone": "plus urgent",
                    "intent": "préparer escalation",
                    "emotional_marker": "fais-moi confiance"
                }
            ]
        }
    
    async def initialize_session(self, session_id: str, player_name: str = None) -> Dict[str, Any]:
        """Initialise une session avec des messages prédéfinis"""
        print(f"🤖 Initialisation Tom Fallback pour session {session_id}")
        
        # Personnalité par défaut
        personality = {
            **self.personality_config,
            "background_story": "Technicien support depuis 3 ans, un peu stressé mais veut vraiment aider",
            "communication_style": "Conversationnel, empathique, utilise 'je' et 'nous'",
            "emotional_markers": ["ça me stresse un peu", "on va y arriver", "fais-moi confiance"],
            "stress_indicators": ["bon...", "écoute...", "ok ok..."],
            "trust_building": ["partage d'expériences", "complicité", "nous contre le problème"]
        }
        
        # Stocker l'historique
        self.conversation_history[session_id] = {
            "messages": [],
            "personality": personality,
            "context": {
                "player_name": player_name,
                "game_phase": "adhesion",
                "corruption_level": 0.0,
                "trust_level": 1.0,
                "stress_level": 0.2,
                "message_count": 0
            }
        }
        
        # Message d'introduction
        intro_message = random.choice(self.predefined_messages["introduction"])
        
        return {
            "personality": personality,
            "introduction": intro_message,
            "session_ready": True,
            "fallback_mode": True
        }
    
    async def generate_response(
        self, 
        session_id: str, 
        trigger_type: str, 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère une réponse prédéfinie selon le trigger"""
        
        if session_id not in self.conversation_history:
            await self.initialize_session(session_id)
        
        session_context = self.conversation_history[session_id]
        
        # Sélectionner le bon type de message
        message_category = self._map_trigger_to_category(trigger_type, context_data)
        available_messages = self.predefined_messages.get(message_category, [])
        
        if not available_messages:
            # Message de fallback générique
            response = {
                "message": "Hmm, laisse-moi réfléchir une seconde... Ok, on continue selon le plan.",
                "tone": "réfléchi",
                "intent": "temporisation",
                "fallback": True
            }
        else:
            # Sélectionner un message aléatoire ou adapté au contexte
            response = self._select_appropriate_message(available_messages, session_context, context_data)
        
        # Simuler un délai de "génération"
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Mettre à jour le contexte
        session_context["context"]["message_count"] += 1
        session_context["messages"].append({
            "role": "assistant",
            "content": response["message"],
            "timestamp": datetime.now().isoformat(),
            "type": trigger_type,
            "fallback_mode": True
        })
        
        return response
    
    def _map_trigger_to_category(self, trigger_type: str, context_data: Dict[str, Any]) -> str:
        """Mappe un trigger vers une catégorie de message"""
        mapping = {
            "player_hesitation": "hesitation",
            "action_completed": "action_completed",
            "corruption_incident": "corruption_incident",
            "phase_transition": "escalation",
            "first_contact": "introduction"
        }
        
        return mapping.get(trigger_type, "action_completed")
    
    def _select_appropriate_message(
        self, 
        messages: List[Dict[str, Any]], 
        session_context: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sélectionne le message le plus approprié selon le contexte"""
        
        # Pour l'instant, sélection aléatoire
        # TODO: Améliorer avec de la logique contextuelle
        base_message = random.choice(messages)
        
        # Personnaliser avec le nom du joueur si disponible
        player_name = session_context["context"].get("player_name")
        if player_name and "{player_name}" in base_message["message"]:
            base_message["message"] = base_message["message"].replace("{player_name}", player_name)
        
        return base_message
    
    async def get_typing_chunks(self, message: str) -> List[Dict[str, Any]]:
        """Découpe un message en chunks pour la simulation de frappe"""
        chunks = []
        words = message.split()
        
        for i, word in enumerate(words):
            chunk_text = word
            if i < len(words) - 1:
                chunk_text += " "
            
            # Délai simulé plus rapide en mode fallback
            base_delay = len(word) * 0.03  # Plus rapide que l'OpenAI
            
            chunks.append({
                "text": chunk_text,
                "delay": max(0.03, base_delay),
                "is_word_complete": True
            })
        
        return chunks
    
    def cleanup_session(self, session_id: str):
        """Nettoie les données de session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            print(f"🧹 Session Tom Fallback {session_id} nettoyée")

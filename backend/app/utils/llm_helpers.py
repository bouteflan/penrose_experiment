"""
Helpers et utilitaires pour l'intégration LLM
"""
import json
import re
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import tiktoken
from openai import AsyncOpenAI


class LLMTokenCounter:
    """
    Compteur de tokens pour optimiser les requêtes LLM
    """
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback pour nouveaux modèles
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Compte le nombre de tokens dans un texte"""
        return len(self.encoding.encode(text))
    
    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Compte les tokens dans une liste de messages"""
        total_tokens = 0
        for message in messages:
            # Ajouter les tokens du contenu
            total_tokens += self.count_tokens(message.get("content", ""))
            # Ajouter les tokens du rôle et de la structure
            total_tokens += 4  # Estimation pour role, content, etc.
        
        total_tokens += 2  # Tokens pour l'assistant response
        return total_tokens
    
    def trim_messages_to_limit(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Réduit la liste de messages pour respecter la limite de tokens
        """
        if not messages:
            return messages
        
        # Toujours garder le premier message (contexte système)
        if len(messages) == 1:
            return messages
        
        system_message = messages[0] if messages[0].get("role") == "system" else None
        conversation_messages = messages[1:] if system_message else messages
        
        # Compter les tokens du message système
        system_tokens = self.count_message_tokens([system_message]) if system_message else 0
        available_tokens = max_tokens - system_tokens - 100  # Marge de sécurité
        
        # Partir de la fin et ajouter des messages jusqu'à la limite
        trimmed_conversation = []
        current_tokens = 0
        
        for message in reversed(conversation_messages):
            message_tokens = self.count_message_tokens([message])
            if current_tokens + message_tokens <= available_tokens:
                trimmed_conversation.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        # Reconstituer la liste finale
        final_messages = []
        if system_message:
            final_messages.append(system_message)
        final_messages.extend(trimmed_conversation)
        
        return final_messages


class LLMResponseParser:
    """
    Parser pour nettoyer et valider les réponses LLM
    """
    
    @staticmethod
    def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
        """
        Extrait et parse le JSON d'une réponse LLM
        """
        # Nettoyer la réponse
        cleaned = response.strip()
        
        # Supprimer les balises markdown si présentes
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()
        
        # Chercher un JSON dans le texte
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, cleaned, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"JSON trouvé: {json_str[:200]}...")
                return None
        
        # Essayer de parser la réponse entière
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"❌ Aucun JSON valide trouvé dans: {cleaned[:100]}...")
            return None
    
    @staticmethod
    def validate_tom_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et normalise une réponse de Tom
        """
        required_fields = ["message"]
        optional_fields = {
            "tone": "empathique",
            "intent": "communication",
            "emotional_marker": "",
            "typing_chunks": []
        }
        
        # Vérifier les champs obligatoires
        for field in required_fields:
            if field not in response:
                response[field] = f"Message par défaut - champ {field} manquant"
        
        # Ajouter les champs optionnels
        for field, default_value in optional_fields.items():
            if field not in response:
                response[field] = default_value
        
        # Valider la longueur du message
        if len(response["message"]) > 1000:
            response["message"] = response["message"][:950] + "..."
        
        return response
    
    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """
        Nettoie et sécurise un texte d'entrée
        """
        if not text:
            return ""
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Limiter la longueur
        if len(text) > 5000:
            text = text[:5000]
        
        # Nettoyer les espaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text


class LLMPromptBuilder:
    """
    Constructeur de prompts optimisés pour REMOTE
    """
    
    @staticmethod
    def build_tom_personality_prompt(
        player_name: str = None,
        condition: str = "confident",
        context: Dict[str, Any] = None
    ) -> str:
        """
        Construit le prompt de personnalité de Tom
        """
        context = context or {}
        
        base_prompt = f"""
Tu es Tom, un technicien du support informatique qui aide {player_name or 'un collègue'} avec un problème de sécurité urgent.

PERSONNALITÉ DE BASE (Condition {condition.upper()}):
"""
        
        if condition == "confident":
            base_prompt += """
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
"""
        else:  # oracle
            base_prompt += """
- Tu es un système de support technique automatisé
- Tu utilises un langage factuel et impersonnel
- Tes réponses sont directes et techniques
- Tu ne montres pas d'émotions
- Tu suis des procédures standardisées
- Tu es efficace et précis

TRAITS SPÉCIFIQUES:
- Ton professionnel et impersonnel
- Phrases courtes et directes
- Pas de pronoms personnels ("je", "nous")
- Instructions claires et méthodiques
- Aucune auto-divulgation
"""
        
        if context:
            base_prompt += f"\n\nCONTEXTE ACTUEL:\n{json.dumps(context, indent=2)}"
        
        return base_prompt
    
    @staticmethod
    def build_action_generation_prompt(
        typology: str,
        action_type: str,
        game_phase: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Construit un prompt pour générer un ordre d'action Tom
        """
        return f"""
Tu es Tom du support technique (Condition B - Style humain empathique).

GÉNÉRATION D'ORDRE:
- Typologie: {typology}
- Action spécifique: {action_type}
- Phase du jeu: {game_phase}
- Contexte: {json.dumps(context, indent=2)}

STYLE (Condition B):
- Ton personnel et empathique
- Utilise "je", "nous", "tu"
- Justification technique plausible mais détournée
- Crée de la confiance et de la complicité
- Adapte l'urgence à la phase

Génère un ordre qui:
1. Donne une instruction claire
2. Fournit une justification crédible
3. Utilise un ton humain
4. Maintient la relation de confiance

Format JSON requis:
{{
    "message": "message complet",
    "instruction": "action précise",
    "justification": "raison technique",
    "target": "élément ciblé",
    "tone": "description du ton"
}}
"""


class LLMRateLimiter:
    """
    Limiteur de débit pour les requêtes LLM
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
    
    async def wait_if_needed(self):
        """
        Attend si nécessaire pour respecter les limites de débit
        """
        current_time = time.time()
        
        # Nettoyer les requêtes anciennes
        cutoff_time = current_time - 60  # Dernière minute
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # Vérifier si on dépasse la limite
        if len(self.request_times) >= self.requests_per_minute:
            # Calculer le temps d'attente
            oldest_request = min(self.request_times)
            wait_time = 61 - (current_time - oldest_request)
            
            if wait_time > 0:
                print(f"⏳ Rate limit atteint, attente de {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Enregistrer cette requête
        self.request_times.append(current_time)


# Instances globales des utilitaires
token_counter = LLMTokenCounter()
response_parser = LLMResponseParser()
prompt_builder = LLMPromptBuilder()
rate_limiter = LLMRateLimiter()


def get_token_counter() -> LLMTokenCounter:
    """Retourne l'instance du compteur de tokens"""
    return token_counter


def get_response_parser() -> LLMResponseParser:
    """Retourne l'instance du parser de réponses"""
    return response_parser


def get_prompt_builder() -> LLMPromptBuilder:
    """Retourne l'instance du constructeur de prompts"""
    return prompt_builder


def get_rate_limiter() -> LLMRateLimiter:
    """Retourne l'instance du limiteur de débit"""
    return rate_limiter

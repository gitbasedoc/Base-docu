"""
Service IA pour KB Support Basedoc
Utilise l'API Claude d'Anthropic pour:
- Génération automatique de tags
- Reformulation de contenu
- Mise en page assistée
- Recherche sémantique
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from functools import wraps

import anthropic
from anthropic import APIError, APIConnectionError, RateLimitError

# Configuration logging
logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Exception de base pour les erreurs du service IA"""
    pass


class AIServiceConnectionError(AIServiceError):
    """Erreur de connexion à l'API"""
    pass


class AIServiceRateLimitError(AIServiceError):
    """Erreur de rate limit"""
    pass


class AIServiceConfig:
    """Configuration du service IA"""

    def __init__(self):
        self.api_key = os.environ.get('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY non définie dans les variables d'environnement")

        self.model = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
        self.max_tokens = int(os.environ.get('CLAUDE_MAX_TOKENS', 4096))
        self.timeout = int(os.environ.get('CLAUDE_TIMEOUT', 60))
        self.max_retries = 3
        self.retry_delay = 2  # secondes


def retry_on_error(max_retries: int = 3, delay: int = 2):
    """
    Décorateur pour retry automatique en cas d'erreur
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Rate limit atteint. Retry {attempt + 1}/{max_retries} "
                            f"dans {wait_time}s"
                        )
                        time.sleep(wait_time)
                    else:
                        raise AIServiceRateLimitError(
                            "Rate limit API dépassé après plusieurs tentatives"
                        ) from e

                except APIConnectionError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"Erreur de connexion. Retry {attempt + 1}/{max_retries} "
                            f"dans {wait_time}s"
                        )
                        time.sleep(wait_time)
                    else:
                        raise AIServiceConnectionError(
                            "Impossible de se connecter à l'API après plusieurs tentatives"
                        ) from e

                except APIError as e:
                    last_exception = e
                    logger.error(f"Erreur API: {str(e)}")
                    raise AIServiceError(f"Erreur API Claude: {str(e)}") from e

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class AIService:
    """
    Service principal pour toutes les fonctionnalités IA
    """

    def __init__(self, config: Optional[AIServiceConfig] = None):
        """
        Initialise le service IA

        Args:
            config: Configuration personnalisée (optionnel)
        """
        self.config = config or AIServiceConfig()
        self.client = anthropic.Anthropic(api_key=self.config.api_key)

    def _call_claude(
            self,
            prompt: str,
            temperature: float = 0.3,
            max_tokens: Optional[int] = None
    ) -> str:
        """
        Appel générique à l'API Claude

        Args:
            prompt: Le prompt à envoyer
            temperature: Température (0-1, plus bas = plus déterministe)
            max_tokens: Nombre max de tokens (défaut: config)

        Returns:
            Réponse de Claude en texte brut
        """
        max_tokens = max_tokens or self.config.max_tokens

        logger.debug(f"Appel Claude API - Temperature: {temperature}, Max tokens: {max_tokens}")

        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.config.timeout
        )

        response_text = message.content[0].text
        logger.debug(f"Réponse reçue - Longueur: {len(response_text)} caractères")

        return response_text

    @retry_on_error(max_retries=3, delay=2)
    def generate_tags(
            self,
            title: str,
            content: str,
            min_tags: int = 4,
            max_tags: int = 8
    ) -> List[str]:
        """
        Génère des tags automatiquement pour une procédure

        Args:
            title: Titre de la procédure
            content: Contenu de la procédure
            min_tags: Nombre minimum de tags
            max_tags: Nombre maximum de tags

        Returns:
            Liste de tags

        Raises:
            AIServiceError: En cas d'erreur API
        """
        logger.info(f"Génération de tags pour: {title[:50]}...")

        # Limiter le contenu pour éviter de dépasser les tokens
        content_preview = content[:2000] if len(content) > 2000 else content

        prompt = f"""Tu es un assistant qui analyse des procédures IT pour un service support.

Ta mission est d'extraire des tags pertinents basés sur :
- Mots-clés récurrents (apparaissant plus de 2 fois)
- Termes techniques (noms de logiciels, commandes, technologies)
- Actions principales (installation, configuration, dépannage, etc.)
- Contexte général de la procédure

TITRE : {title}

CONTENU (extrait) :
{content_preview}

INSTRUCTIONS :
1. Analyse le titre et le contenu
2. Extrais entre {min_tags} et {max_tags} tags pertinents
3. Tags en minuscules, sans accents
4. Utilise des tirets pour les termes composés (ex: boite-partagee)
5. Privilégie les termes techniques précis
6. Pas de tags génériques comme "informatique" ou "aide"

Retourne UNIQUEMENT un objet JSON au format :
{{"tags": ["tag1", "tag2", "tag3"]}}

Ne fournis AUCUNE explication, UNIQUEMENT le JSON."""

        try:
            response = self._call_claude(prompt, temperature=0.2)

            # Parser la réponse JSON
            # Nettoyer la réponse au cas où il y a du texte avant/après le JSON
            response = response.strip()

            # Trouver le JSON dans la réponse
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.error(f"Pas de JSON dans la réponse: {response}")
                raise AIServiceError("Réponse invalide de l'API (pas de JSON)")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            tags = data.get('tags', [])

            # Validation
            if not isinstance(tags, list):
                raise AIServiceError("Format de tags invalide")

            if len(tags) < min_tags:
                logger.warning(f"Seulement {len(tags)} tags générés (min: {min_tags})")

            if len(tags) > max_tags:
                tags = tags[:max_tags]

            # Normaliser les tags
            tags = [self._normalize_tag(tag) for tag in tags]

            logger.info(f"Tags générés: {tags}")
            return tags

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            logger.error(f"Réponse brute: {response}")
            raise AIServiceError(f"Impossible de parser la réponse JSON: {e}") from e

    @retry_on_error(max_retries=3, delay=2)
    def reformulate_content(
            self,
            title: str,
            content: str
    ) -> str:
        """
        Reformule le contenu d'une procédure de manière professionnelle

        Args:
            title: Titre de la procédure
            content: Contenu original

        Returns:
            Contenu reformulé

        Raises:
            AIServiceError: En cas d'erreur API
        """
        logger.info(f"Reformulation du contenu pour: {title[:50]}...")

        if len(content.strip()) < 50:
            raise ValueError("Le contenu est trop court pour être reformulé (min 50 caractères)")

        prompt = f"""Tu es un rédacteur technique professionnel spécialisé dans les procédures IT.

MISSION : Reformuler cette procédure IT de manière professionnelle.

TITRE : {title}

CONTENU ORIGINAL :
{content}

INSTRUCTIONS :
1. Corriger TOUTES les fautes d'orthographe et de grammaire
2. Améliorer la syntaxe pour un style professionnel et clair
3. Utiliser un vocabulaire technique approprié
4. Structurer avec des titres markdown (## pour sections, ### pour sous-sections)
5. Numéroter les étapes si c'est une procédure séquentielle
6. Conserver TOUTES les informations techniques (chemins, commandes, paramètres) EXACTEMENT
7. Garder le même niveau de détail
8. Format markdown avec mise en forme appropriée

STYLE :
- Professionnel et clair
- Phrases courtes et précises
- Vocabulaire IT approprié
- Ton neutre et instructif
- Tutoiement (utiliser "vous")

IMPORTANT :
- NE PAS inventer d'informations
- NE PAS modifier les commandes, chemins, ou paramètres techniques
- NE PAS réduire le niveau de détail

Retourne UNIQUEMENT le contenu reformulé en markdown, sans commentaire ni explication."""

        try:
            reformulated = self._call_claude(prompt, temperature=0.3)

            # Validation basique
            if len(reformulated.strip()) < 50:
                raise AIServiceError("Contenu reformulé trop court")

            logger.info(f"Reformulation réussie - Longueur: {len(reformulated)} caractères")
            return reformulated.strip()

        except Exception as e:
            logger.error(f"Erreur reformulation: {e}")
            raise

    @retry_on_error(max_retries=3, delay=2)
    def layout_content(
            self,
            title: str,
            content: str,
            options: Optional[Dict[str, bool]] = None
    ) -> str:
        """
        Réorganise la mise en page d'une procédure

        Args:
            title: Titre de la procédure
            content: Contenu original
            options: Options de mise en page
                - use_emojis: Utiliser des emojis (défaut: True)
                - structure_sections: Structurer en sections (défaut: True)
                - number_steps: Numéroter les étapes (défaut: True)
                - add_troubleshooting: Ajouter section dépannage (défaut: True)

        Returns:
            Contenu réorganisé

        Raises:
            AIServiceError: En cas d'erreur API
        """
        logger.info(f"Réorganisation de la mise en page pour: {title[:50]}...")

        # Options par défaut
        default_options = {
            'use_emojis': True,
            'structure_sections': True,
            'number_steps': True,
            'add_troubleshooting': True
        }

        if options:
            default_options.update(options)

        options = default_options

        # Construire les instructions selon les options
        emoji_instruction = "Utiliser des emojis appropriés pour les sections (📋 🔧 ⚠️ ✅ 🆘 📚)" \
            if options['use_emojis'] else "Ne PAS utiliser d'emojis"

        structure_instruction = """Structurer en sections logiques:
   ## 📋 Objectif
   ## ⚠️ Prérequis
   ## 🔧 Procédure
   ## ✅ Validation
   ## 🆘 Dépannage (si pertinent)
   ## 📚 Références""" if options['structure_sections'] else "Conserver la structure actuelle"

        numbering_instruction = "Numéroter les étapes de la procédure" \
            if options['number_steps'] else "Utiliser des puces pour les listes"

        troubleshooting_instruction = "Ajouter une section dépannage avec les erreurs courantes" \
            if options['add_troubleshooting'] else "Ne pas ajouter de section dépannage"

        prompt = f"""Tu es un expert en documentation technique IT.

MISSION : Réorganiser cette procédure pour une présentation professionnelle optimale.

TITRE : {title}

CONTENU ACTUEL :
{content}

INSTRUCTIONS DE MISE EN PAGE :

1. STRUCTURE :
{structure_instruction}

2. EMOJIS :
{emoji_instruction}

3. NUMÉROTATION :
{numbering_instruction}

4. DÉPANNAGE :
{troubleshooting_instruction}

5. MISE EN FORME :
   - Mettre en **gras** les éléments importants
   - Utiliser des listes à puces ou numérotées
   - Encadrer les commandes dans des blocs code ```
   - Ajouter des notes avec > pour les remarques importantes
   - Utiliser des tableaux si pertinent

6. CLARTÉ :
   - Titres courts et descriptifs
   - Une idée par paragraphe
   - Ordre logique et progressif
   - Transitions fluides entre sections

7. PRÉSERVATION :
   - Garder TOUTES les informations techniques
   - Ne rien inventer
   - Conserver les commandes, chemins, paramètres exacts

Retourne UNIQUEMENT le contenu réorganisé en markdown, sans commentaire ni explication."""

        try:
            layout = self._call_claude(prompt, temperature=0.4)

            # Validation basique
            if len(layout.strip()) < 50:
                raise AIServiceError("Contenu réorganisé trop court")

            logger.info(f"Réorganisation réussie - Longueur: {len(layout)} caractères")
            return layout.strip()

        except Exception as e:
            logger.error(f"Erreur réorganisation: {e}")
            raise

    @retry_on_error(max_retries=3, delay=2)
    def semantic_search(
            self,
            query: str,
            procedures: List[Dict],
            top_k: int = 10
    ) -> List[Tuple[Dict, int]]:
        """
        Recherche sémantique dans les procédures

        Args:
            query: Question de l'utilisateur
            procedures: Liste de procédures {id, title, content}
            top_k: Nombre de résultats à retourner

        Returns:
            Liste de tuples (procédure, score_pertinence)
            Score de 0-100

        Raises:
            AIServiceError: En cas d'erreur API
        """
        logger.info(f"Recherche sémantique: {query[:50]}...")

        results = []

        # Limiter le nombre de procédures pour éviter les coûts
        procedures_to_search = procedures[:20]

        for proc in procedures_to_search:
            # Limiter le contenu
            content_preview = proc['content'][:500] if len(proc['content']) > 500 else proc['content']

            prompt = f"""Question utilisateur : {query}

Titre procédure : {proc['title']}
Contenu (extrait) : {content_preview}

Cette procédure répond-elle à la question de l'utilisateur ?

Réponds UNIQUEMENT par un score de 0 à 100 :
- 0 = Pas du tout pertinent
- 50 = Moyennement pertinent
- 100 = Très pertinent, répond exactement à la question

Retourne UNIQUEMENT le nombre, rien d'autre."""

            try:
                response = self._call_claude(prompt, temperature=0.1, max_tokens=10)

                # Extraire le score
                score_str = response.strip()
                score = int(''.join(filter(str.isdigit, score_str)))

                # Valider le score
                score = max(0, min(100, score))

                if score > 30:  # Seuil minimum
                    results.append((proc, score))

                logger.debug(f"Procédure {proc['id']}: score {score}")

            except (ValueError, Exception) as e:
                logger.warning(f"Erreur scoring procédure {proc['id']}: {e}")
                continue

        # Trier par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)

        # Retourner top_k résultats
        top_results = results[:top_k]

        logger.info(f"Recherche sémantique: {len(top_results)} résultats trouvés")
        return top_results

    def _normalize_tag(self, tag: str) -> str:
        """
        Normalise un tag (minuscules, sans accents, etc.)

        Args:
            tag: Tag à normaliser

        Returns:
            Tag normalisé
        """
        import unicodedata

        # Enlever les accents
        tag = ''.join(
            c for c in unicodedata.normalize('NFD', tag)
            if unicodedata.category(c) != 'Mn'
        )

        # Minuscules
        tag = tag.lower()

        # Enlever espaces multiples et trim
        tag = ' '.join(tag.split())

        # Remplacer espaces par tirets
        tag = tag.replace(' ', '-')

        # Garder seulement alphanum et tirets
        tag = ''.join(c for c in tag if c.isalnum() or c == '-')

        return tag

    def estimate_cost(
            self,
            input_tokens: int,
            output_tokens: int
    ) -> float:
        """
        Estime le coût d'un appel API

        Args:
            input_tokens: Nombre de tokens en input
            output_tokens: Nombre de tokens en output

        Returns:
            Coût estimé en USD

        Note:
            Prix Claude Sonnet 4.5 (décembre 2024):
            - Input: $3 / 1M tokens
            - Output: $15 / 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0

        total_cost = input_cost + output_cost

        return round(total_cost, 6)


# Instance globale (singleton)
_ai_service_instance = None


def get_ai_service() -> AIService:
    """
    Récupère l'instance globale du service IA (singleton)

    Returns:
        Instance AIService
    """
    global _ai_service_instance

    if _ai_service_instance is None:
        _ai_service_instance = AIService()

    return _ai_service_instance

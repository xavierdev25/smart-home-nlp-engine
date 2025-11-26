"""
Módulo NLP para Casa Inteligente
================================

Este módulo contiene todas las reglas y lógica de procesamiento
de lenguaje natural para el sistema de domótica.

Estructura del módulo:
- constants.py: Enums, constantes y configuración global
- intents.py: Patrones regex para detectar intenciones
- aliases.py: Sinónimos de dispositivos, habitaciones y acciones
- negations.py: Detección de negaciones en español
- normalizer.py: Normalización de texto (acentos, espacios, etc.)
- matchers.py: Lógica de matching de intenciones y dispositivos
"""

from .constants import NLPConstants, IntentType, DeviceType, ActionCategory
from .intents import IntentDefinitions, ContextPatterns
from .aliases import DeviceAliases, RoomAliases, ActionAliases
from .negations import NegationDetector, NegationResult
from .normalizer import TextNormalizer, SpanishTextPreprocessor
from .matchers import (
    IntentMatcher, 
    DeviceMatcher, 
    EntityExtractor,
    IntentMatch,
    DeviceMatch,
    EntityMatch
)

__all__ = [
    # Constants
    "NLPConstants",
    "IntentType",
    "DeviceType",
    "ActionCategory",
    # Intents
    "IntentDefinitions",
    "ContextPatterns",
    # Aliases
    "DeviceAliases",
    "RoomAliases",
    "ActionAliases",
    # Negations
    "NegationDetector",
    "NegationResult",
    # Normalizer
    "TextNormalizer",
    "SpanishTextPreprocessor",
    # Matchers
    "IntentMatcher",
    "DeviceMatcher",
    "EntityExtractor",
    "IntentMatch",
    "DeviceMatch",
    "EntityMatch",
]

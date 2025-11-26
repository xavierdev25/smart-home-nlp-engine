"""
Sistema de Detección de Negaciones
==================================

Detecta y procesa negaciones en comandos de voz/texto en español.
Maneja casos como "no enciendas", "no quiero que se abra", etc.
"""
import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class NegationResult:
    """Resultado del análisis de negación"""
    is_negated: bool
    negation_type: str          # tipo de negación detectada
    original_intent: str        # intención original (antes de negar)
    negation_word: str          # palabra de negación encontrada
    confidence: float           # confianza en la detección
    span: Tuple[int, int]       # posición de la negación en el texto


class NegationDetector:
    """
    Detector de negaciones para español.
    
    Tipos de negaciones soportadas:
    1. Negación directa: "no enciendas", "no prendas"
    2. Negación con pronombre: "no la enciendas", "no lo abras"
    3. Negación doble: "no quiero que enciendas"
    4. Negación prohibitiva: "deja de", "para de"
    5. Negación implícita: "mejor no", "prefiero que no"
    """
    
    # ==========================================================================
    # PATRONES DE NEGACIÓN DIRECTA
    # ==========================================================================
    DIRECT_NEGATION_PATTERNS: List[str] = [
        # "No" + verbo imperativo
        r"\bno\s+(enciendas?|prendas?|actives?|inicies?)\b",
        r"\bno\s+(apagues?|desactives?|detengas?|pares?)\b",
        r"\bno\s+(abras?|despejes?|descorras?|levantes?)\b",
        r"\bno\s+(cierres?|corras?|bajes?|tapes?|bloquees?)\b",
        
        # "No" + verbo infinitivo
        r"\bno\s+(encender|prender|activar|iniciar)\b",
        r"\bno\s+(apagar|desactivar|detener|parar)\b",
        r"\bno\s+(abrir|despejar|descorrer|levantar)\b",
        r"\bno\s+(cerrar|correr|bajar|tapar|bloquear)\b",
        
        # Formas regionales (Argentina/Uruguay con voseo)
        r"\bno\s+(encendás|prendás|activés|iniciés)\b",
        r"\bno\s+(apagués|desactivés|detengás|parés)\b",
        r"\bno\s+(abrás|despejés|descorrás|levantés)\b",
        r"\bno\s+(cerrés|corrás|bajés|tapés|bloqueés)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE NEGACIÓN CON PRONOMBRE
    # ==========================================================================
    PRONOUN_NEGATION_PATTERNS: List[str] = [
        # "No" + pronombre + verbo
        r"\bno\s+(la|lo|las|los|le|les|me)\s+(enciendas?|prendas?|actives?)\b",
        r"\bno\s+(la|lo|las|los|le|les|me)\s+(apagues?|desactives?)\b",
        r"\bno\s+(la|lo|las|los|le|les|me)\s+(abras?|cierres?)\b",
        
        # Con doble pronombre
        r"\bno\s+me\s+(la|lo|las|los)\s+(enciendas?|prendas?|apagues?|abras?|cierres?)\b",
        r"\bno\s+te\s+(la|lo|las|los)\s+(enciendas?|prendas?|apagues?|abras?|cierres?)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE NEGACIÓN COMPUESTA/DOBLE
    # ==========================================================================
    COMPOUND_NEGATION_PATTERNS: List[str] = [
        # "No quiero/deseo/necesito que..."
        r"\bno\s+(quiero|deseo|necesito|me\s+gustaría)\s+(que\s+)?(se\s+)?(encienda|prenda|active)\b",
        r"\bno\s+(quiero|deseo|necesito|me\s+gustaría)\s+(que\s+)?(se\s+)?(apague|desactive)\b",
        r"\bno\s+(quiero|deseo|necesito|me\s+gustaría)\s+(que\s+)?(se\s+)?(abra|cierre)\b",
        
        # "Que no se..."
        r"\bque\s+no\s+se\s+(encienda|prenda|active|apague|desactive|abra|cierre)\b",
        
        # "Prefiero que no..."
        r"\bprefiero\s+(que\s+)?no\s+(enciendas?|prendas?|apagues?|abras?|cierres?)\b",
        r"\bprefiero\s+(que\s+)?no\s+se\s+(encienda|prenda|apague|abra|cierre)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE NEGACIÓN PROHIBITIVA
    # ==========================================================================
    PROHIBITIVE_PATTERNS: List[str] = [
        # "Deja de", "Para de"
        r"\bdeja\s+de\s+(encender|prender|activar|apagar|abrir|cerrar)\b",
        r"\bpara\s+de\s+(encender|prender|activar|apagar|abrir|cerrar)\b",
        r"\bdejá\s+de\s+(encender|prender|activar|apagar|abrir|cerrar)\b",  # Voseo
        r"\bpará\s+de\s+(encender|prender|activar|apagar|abrir|cerrar)\b",  # Voseo
        
        # "Evita", "Evitar"
        r"\bevita(r)?\s+(encender|prender|activar|apagar|abrir|cerrar)\b",
        
        # "Sin" + infinitivo
        r"\bsin\s+(encender|prender|activar|apagar|abrir|cerrar)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE NEGACIÓN IMPLÍCITA
    # ==========================================================================
    IMPLICIT_NEGATION_PATTERNS: List[str] = [
        # "Mejor no"
        r"\bmejor\s+no\b",
        r"\bmejor\s+que\s+no\b",
        
        # "Todavía no", "Aún no"
        r"\b(todavía|aún|aun)\s+no\b",
        
        # "Nunca", "Jamás"
        r"\bnunca\s+(enciendas?|prendas?|apagues?|abras?|cierres?)\b",
        r"\bjamás\s+(enciendas?|prendas?|apagues?|abras?|cierres?)\b",
        
        # "Nada de"
        r"\bnada\s+de\s+(encender|prender|apagar|abrir|cerrar)\b",
    ]
    
    # ==========================================================================
    # PALABRAS CLAVE DE NEGACIÓN
    # ==========================================================================
    NEGATION_KEYWORDS: List[str] = [
        "no", "ni", "nunca", "jamás", "jamas", "tampoco",
        "ninguno", "ninguna", "nada", "nadie",
        "sin", "apenas", "difícilmente", "dificilmente",
    ]
    
    # ==========================================================================
    # EXCEPCIONES (frases que parecen negaciones pero no lo son)
    # ==========================================================================
    FALSE_POSITIVE_PATTERNS: List[str] = [
        r"\bno\s+sé\s+(si|cómo|como|qué|que)\b",        # "No sé si..."
        r"\b¿?no\s+(puedes|podrías|podés)\b",           # Pregunta cortés
        r"\bpor\s+qué\s+no\b",                           # "¿Por qué no...?"
        r"\bcómo\s+no\b",                                # "¡Cómo no!" (afirmativo)
        r"\b(ya|que)\s+no\s+(está|funciona)\b",         # Estado actual negativo
    ]
    
    def __init__(self):
        """Inicializa el detector compilando los patrones regex"""
        self._compiled_direct = [
            re.compile(p, re.IGNORECASE | re.UNICODE) 
            for p in self.DIRECT_NEGATION_PATTERNS
        ]
        self._compiled_pronoun = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.PRONOUN_NEGATION_PATTERNS
        ]
        self._compiled_compound = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.COMPOUND_NEGATION_PATTERNS
        ]
        self._compiled_prohibitive = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.PROHIBITIVE_PATTERNS
        ]
        self._compiled_implicit = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.IMPLICIT_NEGATION_PATTERNS
        ]
        self._compiled_false_positive = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.FALSE_POSITIVE_PATTERNS
        ]
    
    def detect(self, text: str) -> NegationResult:
        """
        Detecta si el texto contiene una negación.
        
        Args:
            text: Texto a analizar
            
        Returns:
            NegationResult con los detalles de la detección
        """
        # Primero verificar falsos positivos
        for pattern in self._compiled_false_positive:
            if pattern.search(text):
                return NegationResult(
                    is_negated=False,
                    negation_type="none",
                    original_intent="",
                    negation_word="",
                    confidence=0.0,
                    span=(0, 0)
                )
        
        # Buscar negaciones directas (mayor confianza)
        for pattern in self._compiled_direct:
            match = pattern.search(text)
            if match:
                return NegationResult(
                    is_negated=True,
                    negation_type="direct",
                    original_intent=self._extract_intent_from_match(match),
                    negation_word="no",
                    confidence=0.95,
                    span=match.span()
                )
        
        # Buscar negaciones con pronombre
        for pattern in self._compiled_pronoun:
            match = pattern.search(text)
            if match:
                return NegationResult(
                    is_negated=True,
                    negation_type="pronoun",
                    original_intent=self._extract_intent_from_match(match),
                    negation_word="no",
                    confidence=0.90,
                    span=match.span()
                )
        
        # Buscar negaciones compuestas
        for pattern in self._compiled_compound:
            match = pattern.search(text)
            if match:
                return NegationResult(
                    is_negated=True,
                    negation_type="compound",
                    original_intent=self._extract_intent_from_match(match),
                    negation_word="no quiero",
                    confidence=0.85,
                    span=match.span()
                )
        
        # Buscar negaciones prohibitivas
        for pattern in self._compiled_prohibitive:
            match = pattern.search(text)
            if match:
                return NegationResult(
                    is_negated=True,
                    negation_type="prohibitive",
                    original_intent=self._extract_intent_from_match(match),
                    negation_word=match.group(0).split()[0],
                    confidence=0.85,
                    span=match.span()
                )
        
        # Buscar negaciones implícitas
        for pattern in self._compiled_implicit:
            match = pattern.search(text)
            if match:
                return NegationResult(
                    is_negated=True,
                    negation_type="implicit",
                    original_intent=self._extract_intent_from_match(match),
                    negation_word=match.group(0).split()[0],
                    confidence=0.75,
                    span=match.span()
                )
        
        # Búsqueda simple de palabras clave de negación
        text_lower = text.lower()
        for keyword in self.NEGATION_KEYWORDS:
            if f" {keyword} " in f" {text_lower} ":
                # Encontrada palabra de negación, pero sin patrón específico
                return NegationResult(
                    is_negated=True,
                    negation_type="keyword",
                    original_intent="",
                    negation_word=keyword,
                    confidence=0.60,
                    span=(text_lower.find(keyword), text_lower.find(keyword) + len(keyword))
                )
        
        # No se encontró negación
        return NegationResult(
            is_negated=False,
            negation_type="none",
            original_intent="",
            negation_word="",
            confidence=0.0,
            span=(0, 0)
        )
    
    def _extract_intent_from_match(self, match: re.Match) -> str:
        """Extrae la intención original del match de regex"""
        matched_text = match.group(0).lower()
        
        # Mapeo de verbos a intenciones
        intent_mapping = {
            "enciend": "turn_on",
            "prend": "turn_on",
            "activ": "turn_on",
            "inici": "turn_on",
            "apag": "turn_off",
            "desactiv": "turn_off",
            "deteng": "turn_off",
            "par": "turn_off",
            "abr": "open",
            "despej": "open",
            "descorr": "open",
            "levant": "open",
            "cierr": "close",
            "corr": "close",
            "baj": "close",
            "tap": "close",
            "bloque": "close",
        }
        
        for verb_stem, intent in intent_mapping.items():
            if verb_stem in matched_text:
                return intent
        
        return "unknown"
    
    def remove_negation(self, text: str) -> str:
        """
        Remueve la negación del texto para procesar la intención subyacente.
        
        Args:
            text: Texto con negación
            
        Returns:
            Texto sin la negación
        """
        # Patrones de eliminación ordenados por especificidad
        removal_patterns = [
            (r"\bno\s+(quiero|deseo|necesito)\s+(que\s+)?(se\s+)?", ""),
            (r"\bprefiero\s+(que\s+)?no\s+", ""),
            (r"\bdeja\s+de\s+", ""),
            (r"\bpara\s+de\s+", ""),
            (r"\bmejor\s+(que\s+)?no\s+", ""),
            (r"\bnunca\s+", ""),
            (r"\bjamás\s+", ""),
            (r"\bno\s+(la|lo|las|los|le|les|me|te)\s+", ""),
            (r"\bno\s+", ""),
        ]
        
        result = text
        for pattern, replacement in removal_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def get_negated_response(self, original_intent: str) -> str:
        """
        Genera una respuesta apropiada para un comando negado.
        
        Args:
            original_intent: La intención original que fue negada
            
        Returns:
            Mensaje de respuesta
        """
        responses = {
            "turn_on": "Entendido, NO encenderé el dispositivo.",
            "turn_off": "Entendido, NO apagaré el dispositivo.",
            "open": "Entendido, NO abriré el dispositivo.",
            "close": "Entendido, NO cerraré el dispositivo.",
            "unknown": "Entendido, cancelaré la acción.",
        }
        return responses.get(original_intent, responses["unknown"])

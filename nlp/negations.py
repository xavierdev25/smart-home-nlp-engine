"""
Sistema de Detección de Negaciones - Bilingüe ES/EN
===================================================

Detecta y procesa negaciones en comandos de voz/texto en español e inglés.
Maneja casos como "no enciendas", "don't turn on", etc.
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
        
        # ===== ENGLISH DIRECT NEGATION PATTERNS =====
        r"\b(don't|do\s+not|dont)\s+(turn\s+on|switch\s+on|enable|activate)\b",
        r"\b(don't|do\s+not|dont)\s+(turn\s+off|switch\s+off|disable|deactivate)\b",
        r"\b(don't|do\s+not|dont)\s+(open|unlock|raise)\b",
        r"\b(don't|do\s+not|dont)\s+(close|shut|lock|lower)\b",
        r"\b(do\s+not|don't|dont)\s+(start|stop)\b",
        r"\bnot?\s+(turn|switch)\s+(on|off)\b",
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
        
        # ===== ENGLISH COMPOUND NEGATION PATTERNS =====
        r"\b(i\s+)?don't\s+want\s+(to|you\s+to)\s+(turn|switch|open|close)\b",
        r"\b(please\s+)?(do\s+)?not\s+(turn|switch|open|close)\b",
        r"\bi\s+(don't|do\s+not)\s+(need|want)\s+(it|the\s+\w+)\s+(on|off|open|closed)\b",
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
        
        # ===== ENGLISH IMPLICIT NEGATION PATTERNS =====
        r"\bnever\s+(turn|switch|open|close)\b",
        r"\b(stop|avoid)\s+(turning|opening|closing)\b",
        r"\bkeep\s+(it\s+)?(off|closed|shut)\b",
        r"\bleave\s+(it\s+)?(off|closed|shut)\b",
    ]
    
    # ==========================================================================
    # PALABRAS CLAVE DE NEGACIÓN
    # ==========================================================================
    NEGATION_KEYWORDS: List[str] = [
        # Spanish
        "no", "ni", "nunca", "jamás", "jamas", "tampoco",
        "ninguno", "ninguna", "nada", "nadie",
        "sin", "apenas", "difícilmente", "dificilmente",
        # English
        "not", "don't", "dont", "never", "no",
        "cannot", "can't", "cant", "won't", "wont",
        "shouldn't", "shouldnt", "wouldn't", "wouldnt",
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
        # English false positives
        r"\bwhy\s+not\b",                                # "Why not...?"
        r"\bwhy\s+don't\s+you\b",                        # Polite request
        r"\bi\s+don't\s+know\s+(if|how|what)\b",         # "I don't know if..."
        r"\bno\s+problem\b",                             # "No problem"
        r"\bnot\s+(yet|sure|bad)\b",                     # "Not yet", "Not sure"
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
            # Spanish
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
            # English
            "turn on": "turn_on",
            "switch on": "turn_on",
            "enable": "turn_on",
            "start": "turn_on",
            "turn off": "turn_off",
            "switch off": "turn_off",
            "disable": "turn_off",
            "stop": "turn_off",
            "open": "open",
            "unlock": "open",
            "raise": "open",
            "close": "close",
            "shut": "close",
            "lock": "close",
            "lower": "close",
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
            # Spanish
            (r"\bno\s+(quiero|deseo|necesito)\s+(que\s+)?(se\s+)?", ""),
            (r"\bprefiero\s+(que\s+)?no\s+", ""),
            (r"\bdeja\s+de\s+", ""),
            (r"\bpara\s+de\s+", ""),
            (r"\bmejor\s+(que\s+)?no\s+", ""),
            (r"\bnunca\s+", ""),
            (r"\bjamás\s+", ""),
            (r"\bno\s+(la|lo|las|los|le|les|me|te)\s+", ""),
            (r"\bno\s+", ""),
            # English
            (r"\b(i\s+)?(don't|do\s+not)\s+want\s+(to|you\s+to)\s+", ""),
            (r"\b(please\s+)?(do\s+)?not\s+", ""),
            (r"\b(don't|dont|do\s+not)\s+", ""),
            (r"\bnever\s+", ""),
            (r"\bstop\s+", ""),
            (r"\bavoid\s+", ""),
        ]
        
        result = text
        for pattern, replacement in removal_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def get_negated_response(self, original_intent: str, language: str = "es") -> str:
        """
        Genera una respuesta apropiada para un comando negado.
        
        Args:
            original_intent: La intención original que fue negada
            language: Idioma de respuesta ('es' o 'en')
            
        Returns:
            Mensaje de respuesta
        """
        responses_es = {
            "turn_on": "Entendido, NO encenderé el dispositivo.",
            "turn_off": "Entendido, NO apagaré el dispositivo.",
            "open": "Entendido, NO abriré el dispositivo.",
            "close": "Entendido, NO cerraré el dispositivo.",
            "unknown": "Entendido, cancelaré la acción.",
        }
        responses_en = {
            "turn_on": "Got it, I will NOT turn on the device.",
            "turn_off": "Got it, I will NOT turn off the device.",
            "open": "Got it, I will NOT open the device.",
            "close": "Got it, I will NOT close the device.",
            "unknown": "Got it, I will cancel the action.",
        }
        responses = responses_en if language == "en" else responses_es
        return responses.get(original_intent, responses["unknown"])

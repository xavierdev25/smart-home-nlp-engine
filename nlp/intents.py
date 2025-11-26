"""
Definiciones de Intenciones (Intents) - Bilingüe ES/EN
======================================================

Define los patrones regex para detectar intenciones en español e inglés.
Cada intent tiene múltiples patrones que cubren variaciones del lenguaje natural.
"""
import re
from typing import Dict, List, Pattern, Tuple
from dataclasses import dataclass


@dataclass
class IntentPattern:
    """Representa un patrón de intención con su peso"""
    pattern: Pattern
    weight: float = 1.0
    description: str = ""


class IntentDefinitions:
    """
    Define todos los patrones de intención para el español.
    Los patrones están ordenados por especificidad (más específicos primero).
    """
    
    # ==========================================================================
    # PATRONES DE TURN_ON (Encender)
    # ==========================================================================
    TURN_ON_PATTERNS: List[str] = [
        # Formas directas (indicativo e imperativo)
        r"\b(enciende|encender|encienda|encendé|prende|prender|prenda|prendé)\b",
        r"\b(activa|activar|active|activá)\b",
        r"\b(inicia|iniciar|inicie|iniciá)\b",
        r"\b(arranca|arrancar|arranque|arrancá)\b",
        r"\b(conecta|conectar|conecte|conectá)\b",
        r"\b(dale|darle)\s+(luz|energia|energía|corriente)\b",
        
        # Formas subjuntivas (para negaciones: "no enciendas")
        r"\b(enciendas|prendas|actives|inicies|arranques|conectes)\b",
        
        # Formas coloquiales
        r"\bpon(er|go|ga|le)?\s+(en\s+marcha|funcionando)\b",
        r"\bpon(er|go|ga|le|me)?\s+(la\s+)?(luz|lampara|lámpara)\b",  # "pon la luz"
        r"\b(que\s+)?(se\s+)?encienda\b",
        r"\b(quiero|necesito|deseo)\s+(que\s+)?(se\s+)?encienda\b",
        r"\b(haz|hazme)\s+(que\s+)?(se\s+)?encienda\b",
        
        # Formas con "luz"
        r"\bda(r|me|le)?\s+(luz|energia|energía)\b",
        r"\becha(r)?\s+luz\b",
        
        # Imperativos con por favor
        r"\b(por\s+favor\s+)?(enciende|prende|activa)\b",
        
        # Formas regionales
        r"\bprendé(me|le)?\b",                      # Argentina/Uruguay
        r"\bencendé(me|le)?\b",                     # Argentina/Uruguay
        r"\bilumina(r|me)?\b",                      # Iluminar
        
        # ===== ENGLISH PATTERNS =====
        r"\b(turn\s+on|switch\s+on)\b",
        r"\b(power\s+on|start|enable)\b",
        r"\b(light\s+up|activate)\b",
        r"\b(please\s+)?(turn|switch)\s+on\b",
    ]
    
    # ==========================================================================
    # PATRONES DE TURN_OFF (Apagar)
    # ==========================================================================
    TURN_OFF_PATTERNS: List[str] = [
        # Formas directas
        r"\b(apaga|apagar|apague|apagá)\b",
        r"\b(desactiva|desactivar|desactive|desactivá)\b",
        r"\b(detén|deten|detener|detenga)\b",
        r"\b(para|parar|pare|pará)\s+(el|la)?\b",
        r"\b(desconecta|desconectar|desconecte|desconectá)\b",
        r"\b(corta|cortar|corte|cortá)\s+(la\s+)?(luz|energia|energía|corriente)\b",
        
        # Formas subjuntivas (para negaciones: "no apagues")
        r"\b(apagues|desactives|detengas|pares|desconectes|cortes)\b",
        
        # Formas coloquiales
        r"\b(quita|quitar|quite)\s+(la\s+)?(luz|energia|energía)\b",
        r"\b(que\s+)?(se\s+)?apague\b",
        r"\b(quiero|necesito|deseo)\s+(que\s+)?(se\s+)?apague\b",
        
        # Formas regionales
        r"\bapagá(me|le)?\b",                       # Argentina/Uruguay
        r"\bcortá(le)?\s+(la\s+)?luz\b",           # Argentina
        
        # ===== ENGLISH PATTERNS =====
        r"\b(turn\s+off|switch\s+off)\b",
        r"\b(power\s+off|stop|disable)\b",
        r"\b(shut\s+(off|down)|deactivate)\b",
        r"\b(please\s+)?(turn|switch)\s+off\b",
    ]
    
    # ==========================================================================
    # PATRONES DE OPEN (Abrir)
    # ==========================================================================
    OPEN_PATTERNS: List[str] = [
        # Formas directas
        r"\b(abre|abrir|abra|abrí|abrime)\b",
        r"\b(despeja|despejar|despeje)\b",
        r"\b(descorre|descorrer|descorra)\b",      # Para cortinas
        r"\b(levanta|levantar|levante)\b",         # Para persianas
        r"\b(sube|subir|suba)\s+(la|el)?\s*(persiana|cortina)?\b",
        r"\b(destapa|destapar|destape)\b",
        
        # Formas subjuntivas (para negaciones: "no abras")
        r"\b(abras|despejes|descorras|levantes|subas|destapes)\b",
        
        # Formas coloquiales
        r"\b(que\s+)?(se\s+)?abra\b",
        r"\b(quiero|necesito|deseo)\s+(que\s+)?(se\s+)?abra\b",
        r"\bdeja(r)?\s+(abierto|abierta|pasar)\b",
        
        # Formas regionales
        r"\babrí(me|le)?\b",                       # Argentina/Uruguay
        r"\bdestrabá(me|le)?\b",                   # Destrabar
        
        # ===== ENGLISH PATTERNS =====
        r"\b(open|unlock|raise)\b",
        r"\b(lift\s+up|pull\s+up)\b",
        r"\b(please\s+)?open\b",
        r"\b(roll\s+up|slide\s+open)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE CLOSE (Cerrar)
    # ==========================================================================
    CLOSE_PATTERNS: List[str] = [
        # Formas directas
        r"\b(cierra|cerrar|cierre|cerrá|cierrame)\b",
        r"\b(corre|correr|corra)\s+(la|el)?\s*(cortina|persiana)?\b",
        r"\b(baja|bajar|baje)\s+(la|el)?\s*(persiana|cortina|toldo)?\b",
        r"\b(tapa|tapar|tape)\b",
        r"\b(bloquea|bloquear|bloquee)\b",
        
        # Formas subjuntivas (para negaciones: "no cierres")
        r"\b(cierres|corras|bajes|tapes|bloquees)\b",
        
        # Formas coloquiales
        r"\b(que\s+)?(se\s+)?cierre\b",
        r"\b(quiero|necesito|deseo)\s+(que\s+)?(se\s+)?cierre\b",
        r"\bdeja(r)?\s+(cerrado|cerrada)\b",
        
        # Formas regionales
        r"\bcerrá(me|le)?\b",                      # Argentina/Uruguay
        r"\btrabá(me|le)?\b",                      # Trabar (cerrar con llave)
        
        # ===== ENGLISH PATTERNS =====
        r"\b(close|shut|lock)\b",
        r"\b(lower|pull\s+down)\b",
        r"\b(please\s+)?close\b",
        r"\b(roll\s+down|slide\s+(shut|close))\b",
    ]
    
    # ==========================================================================
    # PATRONES DE STATUS (Consulta de Estado)
    # ==========================================================================
    STATUS_PATTERNS: List[str] = [
        # Preguntas directas
        r"\b(está|esta|están|estan)\s+(encendid[oa]|apagad[oa]|abiert[oa]|cerrad[oa]|activad[oa]|funcionando)\b",
        r"\b(cómo|como)\s+(está|esta|están|estan)\b",
        r"\b(qué|que)\s+tal\s+(está|esta|están|estan)\b",
        r"\b(cuál|cual)\s+es\s+(el\s+)?(estado|status)\b",
        
        # Consultas de estado
        r"\b(estado|status|situación|situacion)\s+(de|del|de\s+la|de\s+el)\b",
        r"\b(dime|decime|muéstrame|muestrame|dame)\s+(el\s+)?(estado|status)\b",
        r"\b(consulta|consultar|verifica|verificar|revisa|revisar|checa|chequea)\b",
        r"\b(info|información|informacion)\s+(de|del|sobre)\b",
        
        # Preguntas implícitas
        r"\b(hay\s+)?luz\s+(en|encendida)\b",
        r"\b(funciona|funcionando|anda|andando)\b",
        r"\bqué\s+pasa\s+con\b",
        
        # Formas regionales
        r"\b(fijate|fijá|fíjate)\s+(si|como|cómo)\b",  # Argentina
        r"\b(checá|chequeá)\b",                          # Argentina
        
        # ===== ENGLISH PATTERNS =====
        r"\b(is|are)\s+(the\s+)?\w+\s+(on|off|open|closed)\b",
        r"\b(what\s+is|what's)\s+(the\s+)?(status|state)\b",
        r"\b(check|verify|show)\s+(the\s+)?(status|state)\b",
        r"\b(how\s+is|how's)\s+(the\s+)?\w+\b",
        r"\b(status|state)\s+(of|for)\b",
    ]
    
    # ==========================================================================
    # PATRONES DE TOGGLE (Alternar)
    # ==========================================================================
    TOGGLE_PATTERNS: List[str] = [
        r"\b(alterna|alternar|alterne)\b",
        r"\b(cambia|cambiar|cambie)\s+(el\s+)?(estado|modo)\b",
        r"\b(invierte|invertir|invierta)\s+(el\s+)?(estado)?\b",
        r"\b(si\s+está\s+)?(encendid[oa]|prendid[oa])\s*,?\s*(apaga|apágala|apágalo)\b",
        r"\b(si\s+está\s+)?(apagad[oa])\s*,?\s*(enciende|préndela|préndelo)\b",
        r"\bswitch(ea|ear)?(?!\s+(on|off))\b",  # "switch" pero no "switch on/off"
        
        # ===== ENGLISH PATTERNS =====
        r"\b(toggle|flip)\b",
        r"\bchange\s+(the\s+)?(state|mode)\b",
    ]
    
    @classmethod
    def get_all_patterns(cls) -> Dict[str, List[str]]:
        """Retorna todos los patrones organizados por intent"""
        return {
            "turn_on": cls.TURN_ON_PATTERNS,
            "turn_off": cls.TURN_OFF_PATTERNS,
            "open": cls.OPEN_PATTERNS,
            "close": cls.CLOSE_PATTERNS,
            "status": cls.STATUS_PATTERNS,
            "toggle": cls.TOGGLE_PATTERNS,
        }
    
    @classmethod
    def get_compiled_patterns(cls) -> Dict[str, List[Pattern]]:
        """Retorna los patrones compilados para mejor rendimiento"""
        patterns = cls.get_all_patterns()
        compiled = {}
        for intent, pattern_list in patterns.items():
            compiled[intent] = [
                re.compile(p, re.IGNORECASE | re.UNICODE)
                for p in pattern_list
            ]
        return compiled


# =============================================================================
# PATRONES DE CONTEXTO (modificadores que afectan la interpretación)
# =============================================================================
class ContextPatterns:
    """Patrones que proveen contexto adicional a la intención"""
    
    # Ubicaciones/habitaciones
    LOCATION_PREPOSITIONS: List[str] = [
        r"\b(en\s+)(el|la|los|las)?\s*",
        r"\b(de\s+)(el|la|los|las)?\s*",
        r"\b(del)\s+",
    ]
    
    # Tiempo/programación
    TIME_PATTERNS: List[str] = [
        r"\b(en|dentro\s+de)\s+(\d+)\s+(minutos?|horas?|segundos?)\b",
        r"\b(a\s+las?)\s+(\d{1,2})(:\d{2})?\s*(am|pm|de\s+la\s+(mañana|tarde|noche))?\b",
        r"\b(cuando|si)\s+(llegue|salga|entre|me\s+vaya)\b",
        r"\b(por\s+la\s+)(mañana|tarde|noche)\b",
        r"\b(mañana|hoy|ahora|ya|después|luego|más\s+tarde)\b",
    ]
    
    # Condicionales
    CONDITIONAL_PATTERNS: List[str] = [
        r"\b(si|cuando|mientras|hasta\s+que)\b",
        r"\b(solo\s+si|únicamente\s+si|siempre\s+que)\b",
    ]
    
    # Intensidad/nivel
    INTENSITY_PATTERNS: List[str] = [
        r"\b(al\s+)?(\d{1,3})\s*(%|por\s*ciento)?\b",
        r"\b(bajo|medio|alto|máximo|mínimo)\b",
        r"\b(un\s+poco|mucho|bastante|completamente)\b",
        r"\b(más|menos)\s+(fuerte|intenso|brillante|suave)\b",
    ]
    
    @classmethod
    def get_all_context_patterns(cls) -> Dict[str, List[str]]:
        """Retorna todos los patrones de contexto"""
        return {
            "location": cls.LOCATION_PREPOSITIONS,
            "time": cls.TIME_PATTERNS,
            "conditional": cls.CONDITIONAL_PATTERNS,
            "intensity": cls.INTENSITY_PATTERNS,
        }

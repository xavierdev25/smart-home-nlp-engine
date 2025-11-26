"""
Constantes del Sistema NLP
==========================

Define todas las constantes utilizadas en el procesamiento NLP.
"""
from enum import Enum
from typing import List, Dict


class IntentType(str, Enum):
    """Tipos de intenciones soportadas por el sistema"""
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    OPEN = "open"
    CLOSE = "close"
    STATUS = "status"
    TOGGLE = "toggle"           # Alternar estado
    DIM = "dim"                 # Atenuar luz
    BRIGHTEN = "brighten"       # Aumentar luz
    SET_LEVEL = "set_level"     # Establecer nivel
    UNKNOWN = "unknown"
    NEGATED = "negated"         # Intención negada


class DeviceType(str, Enum):
    """Tipos de dispositivos IoT soportados"""
    LIGHT = "light"
    FAN = "fan"
    DOOR = "door"
    WINDOW = "window"
    CURTAIN = "curtain"
    ALARM = "alarm"
    SENSOR = "sensor"
    SWITCH = "switch"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    LOCK = "lock"
    OTHER = "other"


class ActionCategory(str, Enum):
    """Categorías de acciones por tipo de dispositivo"""
    POWER = "power"         # on/off para luces, ventiladores
    ACCESS = "access"       # open/close para puertas, ventanas
    SECURITY = "security"   # activate/deactivate para alarmas
    QUERY = "query"         # status, consultas


class NLPConstants:
    """Constantes globales del sistema NLP"""
    
    # Umbrales de confianza
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.70
    LOW_CONFIDENCE_THRESHOLD = 0.50
    
    # Configuración de procesamiento
    MAX_COMMAND_LENGTH = 500
    MIN_COMMAND_LENGTH = 2
    
    # Intents válidos para la API
    VALID_INTENTS: List[str] = [
        "turn_on", "turn_off", "open", "close", 
        "status", "toggle", "unknown", "negated"
    ]
    
    # Mapeo de intent a acción de endpoint
    INTENT_TO_ACTION: Dict[str, str] = {
        "turn_on": "on",
        "turn_off": "off",
        "open": "open",
        "close": "close",
        "status": "status",
        "toggle": "toggle",
    }
    
    # Acciones válidas por tipo de dispositivo
    DEVICE_ACTIONS: Dict[str, List[str]] = {
        "light": ["turn_on", "turn_off", "toggle", "dim", "brighten", "status"],
        "fan": ["turn_on", "turn_off", "toggle", "status"],
        "door": ["open", "close", "status"],
        "window": ["open", "close", "status"],
        "curtain": ["open", "close", "status"],
        "alarm": ["turn_on", "turn_off", "status"],
        "lock": ["open", "close", "status"],
        "thermostat": ["turn_on", "turn_off", "set_level", "status"],
        "sensor": ["status"],
        "camera": ["turn_on", "turn_off", "status"],
    }
    
    # Palabras que indican múltiples dispositivos
    PLURAL_INDICATORS: List[str] = [
        "todas", "todos", "las", "los", "cada", "cualquier",
        "luces", "ventiladores", "puertas", "ventanas", "cortinas"
    ]
    
    # Conectores gramaticales a ignorar
    STOPWORDS: List[str] = [
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "al", "a", "en", "por", "para", "con",
        "mi", "tu", "su", "mis", "tus", "sus",
        "me", "te", "se", "nos", "les",
        "que", "cual", "cuales", "como", "donde",
        "favor", "porfa", "porfavor", "please"
    ]

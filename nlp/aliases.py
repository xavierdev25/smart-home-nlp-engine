"""
Sistema de Alias y Sinónimos - Bilingüe ES/EN
=============================================

Define todos los alias y sinónimos para dispositivos, habitaciones y acciones
en español e inglés. Incluye variaciones regionales y coloquiales.
"""
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class AliasEntry:
    """Representa una entrada de alias con su canonical y variaciones"""
    canonical: str              # Nombre canónico/estándar
    aliases: List[str]          # Lista de alias
    device_type: str = ""       # Tipo de dispositivo (opcional)
    region: str = ""            # Región específica (opcional)


class DeviceAliases:
    """
    Alias y sinónimos para dispositivos IoT.
    El formato es: alias -> device_key (nombre canónico)
    """
    
    # ==========================================================================
    # LUCES (LIGHTS)
    # ==========================================================================
    LIGHTS: Dict[str, List[str]] = {
        # Dispositivo base
        "luz": [
            "lámpara", "lampara", "foco", "bombilla", "bombillo",
            "iluminación", "iluminacion", "luminaria", "candela",
            "foquito", "lamparita", "lucecita", "lucesita",
            "velador",                                   # Lámpara de mesa (Arg)
            # English
            "light", "lamp", "bulb", "lighting",
            "ceiling light", "floor lamp", "table lamp",
        ],
        "led": ["tira led", "tira de led", "leds", "tiras led", "led strip"],
        "spot": ["spotlight", "dicroico", "dicroica", "ojo de buey"],
        "plafon": ["plafón", "lámpara de techo", "lampara de techo"],
    }
    
    # ==========================================================================
    # VENTILADORES (FANS)
    # ==========================================================================
    FANS: Dict[str, List[str]] = {
        "ventilador": [
            "abanico", "fan", "ventilación", "ventilacion",
            "aire", "venti", "turbina",
            "enfriador", "cooler",                       # Coloquiales
            "aspas",                                      # Por las aspas
            # English
            "ceiling fan", "floor fan", "desk fan",
            "blower", "air circulator",
        ],
        "extractor": [
            "extractor de aire", "extractora", "ventilador extractor",
            "campana extractora", "exhaust"
        ],
        "ventilador_techo": [
            "ventilador de techo", "fan de techo", "abanico de techo"
        ],
    }
    
    # ==========================================================================
    # PUERTAS (DOORS)
    # ==========================================================================
    DOORS: Dict[str, List[str]] = {
        "puerta": [
            "portón", "porton", "portal", "entrada",
            "acceso", "paso",
            # English
            "door", "gate", "entrance", "entry",
        ],
        "garage": [
            "garaje", "cochera", "parking", "estacionamiento",
            "puerta del garage", "puerta del garaje",
            "portón del garage", "porton del garaje",
            # English
            "garage door", "carport",
        ],
        "puerta_principal": [
            "puerta principal", "puerta de entrada", "entrada principal",
            "puerta delantera", "puerta frontal", "front door"
        ],
        "puerta_trasera": [
            "puerta trasera", "puerta de atrás", "puerta de atras",
            "puerta del patio", "back door"
        ],
    }
    
    # ==========================================================================
    # VENTANAS (WINDOWS)
    # ==========================================================================
    WINDOWS: Dict[str, List[str]] = {
        "ventana": [
            "ventanal", "cristal",
            "vidriera", "vidrio",
            "ventanita", "ventanilla",
            # English
            "window", "windowpane", "glass",
        ],
        "persiana": [
            "persiana",
            "celosía", "celosia",
            "estor", "store",
            # English
            "blind", "blinds", "shutter", "shutters",
            "roller blind", "venetian blind",
        ],
        "toldo": [
            "toldo", "awning", "marquesina", "parasol"
        ],
    }
    
    # ==========================================================================
    # CORTINAS (CURTAINS)
    # ==========================================================================
    CURTAINS: Dict[str, List[str]] = {
        "cortina": [
            "cortinas",
            "visillo", "visillos",
            "cortinado", "cortinaje",
            "blackout",                                  # Cortinas blackout
            # English
            "curtain", "curtains", "drape", "drapes",
            "window covering", "drapery",
        ],
        "cortina_motorizada": [
            "cortina eléctrica", "cortina electrica",
            "cortina motorizada", "cortina automática", "cortina automatica"
        ],
    }
    
    # ==========================================================================
    # CERRADURAS (LOCKS)
    # ==========================================================================
    LOCKS: Dict[str, List[str]] = {
        "cerradura": [
            "cerrojo", "lock", "chapa",
            "seguro", "pestillo",
            "cerradura inteligente", "smart lock",
            "traba", "candado",
        ],
        "cerradura_principal": [
            "cerradura principal", "cerradura de entrada",
            "chapa principal", "cerrojo principal"
        ],
    }
    
    # ==========================================================================
    # ALARMAS (ALARMS)
    # ==========================================================================
    ALARMS: Dict[str, List[str]] = {
        "alarma": [
            "sirena", "alerta",
            "sistema de alarma", "sistema de seguridad",
            "alarma de seguridad",
            # English  
            "alarm", "security alarm", "siren",
            "alarm system", "security system",
        ],
        "detector": [
            "detector de humo", "smoke detector",
            "detector de movimiento", "motion sensor",
            "sensor de presencia",
        ],
    }
    
    # ==========================================================================
    # SENSORES (SENSORS)
    # ==========================================================================
    SENSORS: Dict[str, List[str]] = {
        "sensor": [
            "sensor", "detector", "medidor",
        ],
        "sensor_temperatura": [
            "termómetro", "termometro", "sensor de temperatura",
            "temperature sensor", "termo"
        ],
        "sensor_humedad": [
            "higrómetro", "higrometro", "sensor de humedad",
            "humidity sensor"
        ],
        "sensor_movimiento": [
            "sensor de movimiento", "detector de movimiento",
            "motion sensor", "PIR"
        ],
    }
    
    # ==========================================================================
    # CLIMATIZACIÓN (CLIMATE)
    # ==========================================================================
    CLIMATE: Dict[str, List[str]] = {
        "aire_acondicionado": [
            "aire", "ac", "a/c", "aire acondicionado",
            "climatizador", "split", "minisplit",
            "enfriador de aire", "air conditioner",
            "clima",                                     # México
        ],
        "calefaccion": [
            "calefacción", "calefactor", "estufa",
            "calentador", "heater", "heating",
            "radiador", "caldera",
        ],
        "termostato": [
            "termostato", "thermostat",
            "control de temperatura", "regulador de temperatura"
        ],
    }
    
    # ==========================================================================
    # OTROS DISPOSITIVOS
    # ==========================================================================
    OTHER: Dict[str, List[str]] = {
        "television": [
            "tv", "tele", "televisor", "pantalla",
            "smart tv", "televisión"
        ],
        "enchufe": [
            "enchufe inteligente", "smart plug", "tomacorriente",
            "toma", "socket", "outlet"
        ],
        "camara": [
            "cámara", "camera", "webcam",
            "cámara de seguridad", "security camera",
            "cámara ip", "ip camera"
        ],
        "timbre": [
            "timbre", "doorbell", "campanilla",
            "timbre inteligente", "video doorbell"
        ],
        "riego": [
            "sistema de riego", "riego", "aspersores",
            "sprinklers", "irrigación", "regadera automática"
        ],
    }
    
    @classmethod
    def get_all_device_aliases(cls) -> Dict[str, List[str]]:
        """Retorna todos los alias de dispositivos combinados"""
        all_aliases = {}
        for category in [cls.LIGHTS, cls.FANS, cls.DOORS, cls.WINDOWS, 
                        cls.CURTAINS, cls.LOCKS, cls.ALARMS, cls.SENSORS,
                        cls.CLIMATE, cls.OTHER]:
            all_aliases.update(category)
        return all_aliases
    
    @classmethod
    def build_reverse_lookup(cls) -> Dict[str, str]:
        """
        Construye un diccionario inverso: alias -> canonical
        Útil para normalizar cualquier variación a su forma canónica
        """
        reverse = {}
        for canonical, aliases in cls.get_all_device_aliases().items():
            reverse[canonical.lower()] = canonical
            for alias in aliases:
                reverse[alias.lower()] = canonical
        return reverse


class RoomAliases:
    """
    Alias y sinónimos para habitaciones/ubicaciones.
    Incluye variaciones regionales del español.
    """
    
    ROOMS: Dict[str, List[str]] = {
        # Áreas principales
        "sala": [
            "salón", "salon", "sala de estar", "estancia",
            "recibidor", "sala principal",
            # English
            "living", "living room", "lounge",
            "family room", "sitting room",
        ],
        "cocina": [
            "cocineta",
            "área de cocina", "zona de cocina",
            # English
            "kitchen", "kitchenette",
        ],
        "comedor": [
            "área de comedor",
            "zona de comedor", "antecomedor",
            # English
            "dining", "dining room", "dining area",
        ],
        
        # Habitaciones
        "dormitorio": [
            "habitación", "habitacion", "cuarto", "recámara", "recamara",
            "alcoba", "pieza",                # "Pieza" común en Chile/Arg
            "cuarto de dormir", "aposento",
            # English
            "bedroom", "room", "sleeping room",
        ],
        "dormitorio_principal": [
            "habitación principal", "cuarto principal", "recámara principal",
            "dormitorio master", "suite principal",
            "cuarto matrimonial",
            # English
            "master bedroom", "main bedroom", "primary bedroom",
        ],
        "dormitorio_ninos": [
            "habitación de niños", "cuarto de niños", "cuarto de los niños",
            "habitación infantil", "cuarto de los chicos",
            # English
            "kids room", "children's room", "kids bedroom",
        ],
        "dormitorio_invitados": [
            "habitación de invitados", "cuarto de invitados",
            "cuarto de huéspedes", "habitación de huéspedes",
            # English
            "guest room", "guest bedroom", "spare room",
        ],
        
        # Baños
        "bano": [
            "baño", "sanitario", "aseo", "servicio",
            "toilette", "wc", "lavabo",
            "medio baño",
            # English
            "bathroom", "toilet", "restroom", "washroom",
            "half bath", "powder room",
        ],
        "bano_principal": [
            "baño principal", "baño master",
            "baño de la habitación", "baño en suite",
            # English
            "master bathroom", "main bathroom", "ensuite",
        ],
        
        # Áreas de trabajo/estudio
        "oficina": [
            "despacho", "estudio",
            "cuarto de trabajo", "área de trabajo",
            # English
            "office", "home office", "study", "workspace",
        ],
        "biblioteca": [
            "library", "sala de lectura", "cuarto de lectura",
        ],
        
        # Exteriores y áreas auxiliares
        "garage": [
            "garaje", "cochera", "parking", "estacionamiento",
            # English
            "carport",
        ],
        "jardin": [
            "jardín", "patio", "terraza", "balcón", "balcon",
            "área exterior", "exterior", "afuera",
            "quincho",                                   # Argentina
            # English
            "garden", "yard", "backyard", "outdoor area",
        ],
        "terraza": [
            "azotea", "mirador",
            "terraza techada",
            # English
            "terrace", "rooftop", "deck", "patio",
        ],
        "patio": [
            "patio trasero", "traspatio",
            "patio delantero",
            # English
            "backyard", "front yard", "courtyard",
        ],
        
        # Áreas de servicio
        "lavanderia": [
            "lavandería", "cuarto de lavado",
            "área de lavado", "zona de lavado",
            "lavadero",                                  # Argentina
            # English
            "laundry", "laundry room", "utility room",
        ],
        "bodega": [
            "almacén", "almacen", "despensa",
            "cuarto de almacenamiento", "trastero",
            # English
            "storage", "storage room", "pantry", "cellar",
        ],
        
        # Áreas de recreación
        "gym": [
            "gimnasio", "gym", "sala de ejercicios",
            "cuarto de ejercicio", "home gym",
        ],
        "cine": [
            "sala de cine", "home theater", "home cinema",
            "cuarto de tv", "sala de tv", "media room",
        ],
        
        # Pasillos y conectores
        "pasillo": [
            "corredor", "hallway", "hall", "vestíbulo", "vestibulo",
            "entrada", "recibidor", "foyer",
        ],
        "escalera": [
            "escaleras", "stairs", "stairway",
            "escalera principal",
        ],
        
        # Pisos/niveles
        "planta_baja": [
            "primer piso", "piso 1", "ground floor",
            "planta baja", "abajo", "nivel 1",
        ],
        "segundo_piso": [
            "piso 2", "planta alta", "second floor",
            "arriba", "nivel 2", "piso de arriba",
        ],
        "sotano": [
            "sótano", "basement", "subsuelo",
            "nivel -1", "bajo tierra",
        ],
    }
    
    @classmethod
    def build_reverse_lookup(cls) -> Dict[str, str]:
        """Construye diccionario inverso: alias -> canonical room"""
        reverse = {}
        for canonical, aliases in cls.ROOMS.items():
            reverse[canonical.lower()] = canonical
            for alias in aliases:
                reverse[alias.lower()] = canonical
        return reverse
    
    @classmethod
    def get_all_room_names(cls) -> Set[str]:
        """Retorna un set con todos los nombres de habitaciones"""
        all_names = set()
        for canonical, aliases in cls.ROOMS.items():
            all_names.add(canonical.lower())
            all_names.update(alias.lower() for alias in aliases)
        return all_names


class ActionAliases:
    """
    Alias para acciones/verbos de control.
    Útil para normalizar diferentes formas verbales.
    """
    
    ACTIONS: Dict[str, List[str]] = {
        "encender": [
            "prender", "activar", "iniciar", "arrancar",
            "conectar", "dar luz", "iluminar",
            "poner en marcha", "habilitar",
            # English
            "turn on", "switch on", "power on",
            "enable", "activate", "start",
        ],
        "apagar": [
            "desactivar", "detener", "parar", "desconectar",
            "cortar", "quitar",
            "inhabilitar", "deshabilitar",
            # English
            "turn off", "switch off", "power off",
            "disable", "deactivate", "stop",
        ],
        "abrir": [
            "despejar", "descorrer", "levantar", "subir",
            "destapar", "destrabar",
            # English
            "open", "unlock", "raise", "lift",
        ],
        "cerrar": [
            "correr", "bajar", "tapar", "bloquear",
            "trabar",
            # English
            "close", "shut", "lock", "lower",
        ],
        "consultar": [
            "verificar", "revisar", "checar", "chequear",
            "ver", "mostrar",
            # English
            "check", "status", "verify", "show",
        ],
    }
    
    @classmethod
    def build_reverse_lookup(cls) -> Dict[str, str]:
        """Construye diccionario inverso: alias -> canonical action"""
        reverse = {}
        for canonical, aliases in cls.ACTIONS.items():
            reverse[canonical.lower()] = canonical
            for alias in aliases:
                reverse[alias.lower()] = canonical
        return reverse

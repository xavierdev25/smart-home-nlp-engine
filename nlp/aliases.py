"""
Sistema de Alias y Sinónimos
============================

Define todos los alias y sinónimos para dispositivos, habitaciones y acciones
en español. Incluye variaciones regionales y coloquiales.
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
            "light", "lamp", "bulb",                    # Anglicismos
            "velador",                                   # Lámpara de mesa (Arg)
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
            "door", "gate",
            "acceso", "paso",
        ],
        "garage": [
            "garaje", "cochera", "parking", "estacionamiento",
            "puerta del garage", "puerta del garaje",
            "portón del garage", "porton del garaje",
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
            "ventanal", "window", "cristal",
            "vidriera", "vidrio",
            "ventanita", "ventanilla",
        ],
        "persiana": [
            "persiana", "blind", "blinds",
            "celosía", "celosia",
            "estor", "store",
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
            "cortinas", "curtain", "curtains",
            "visillo", "visillos",
            "drape", "drapes",
            "cortinado", "cortinaje",
            "blackout",                                  # Cortinas blackout
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
            "alarm", "sirena", "alerta",
            "sistema de alarma", "sistema de seguridad",
            "alarma de seguridad", "security alarm",
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
            "living", "salón", "salon", "sala de estar", "estancia",
            "living room", "lounge", "recibidor",
            "sala principal", "living principal",
        ],
        "cocina": [
            "kitchen", "cocineta", "kitchenette",
            "área de cocina", "zona de cocina",
        ],
        "comedor": [
            "dining", "dining room", "área de comedor",
            "zona de comedor", "antecomedor",
        ],
        
        # Habitaciones
        "dormitorio": [
            "habitación", "habitacion", "cuarto", "recámara", "recamara",
            "bedroom", "alcoba", "pieza",                # "Pieza" común en Chile/Arg
            "cuarto de dormir", "aposento",
        ],
        "dormitorio_principal": [
            "habitación principal", "cuarto principal", "recámara principal",
            "master bedroom", "dormitorio master", "suite principal",
            "cuarto matrimonial",
        ],
        "dormitorio_ninos": [
            "habitación de niños", "cuarto de niños", "cuarto de los niños",
            "habitación infantil", "kids room", "cuarto de los chicos",
        ],
        "dormitorio_invitados": [
            "habitación de invitados", "cuarto de invitados", "guest room",
            "cuarto de huéspedes", "habitación de huéspedes",
        ],
        
        # Baños
        "bano": [
            "baño", "bathroom", "sanitario", "aseo", "servicio",
            "toilette", "toilet", "wc", "lavabo",
            "medio baño",
        ],
        "bano_principal": [
            "baño principal", "baño master", "master bathroom",
            "baño de la habitación", "baño en suite",
        ],
        
        # Áreas de trabajo/estudio
        "oficina": [
            "office", "despacho", "estudio", "home office",
            "cuarto de trabajo", "área de trabajo",
        ],
        "biblioteca": [
            "library", "sala de lectura", "cuarto de lectura",
        ],
        
        # Exteriores y áreas auxiliares
        "garage": [
            "garaje", "cochera", "parking", "estacionamiento",
        ],
        "jardin": [
            "jardín", "garden", "patio", "terraza", "balcón", "balcon",
            "área exterior", "exterior", "afuera",
            "quincho",                                   # Argentina
        ],
        "terraza": [
            "terrace", "azotea", "rooftop", "mirador",
            "terraza techada",
        ],
        "patio": [
            "patio trasero", "backyard", "traspatio",
            "patio delantero", "front yard",
        ],
        
        # Áreas de servicio
        "lavanderia": [
            "lavandería", "laundry", "cuarto de lavado",
            "área de lavado", "zona de lavado",
            "lavadero",                                  # Argentina
        ],
        "bodega": [
            "almacén", "almacen", "storage", "despensa",
            "cuarto de almacenamiento", "trastero",
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
            "conectar", "dar luz", "iluminar", "turn on",
            "poner en marcha", "habilitar",
        ],
        "apagar": [
            "desactivar", "detener", "parar", "desconectar",
            "cortar", "quitar", "turn off",
            "inhabilitar", "deshabilitar",
        ],
        "abrir": [
            "despejar", "descorrer", "levantar", "subir",
            "destapar", "destrabar", "open",
        ],
        "cerrar": [
            "correr", "bajar", "tapar", "bloquear",
            "trabar", "close",
        ],
        "consultar": [
            "verificar", "revisar", "checar", "chequear",
            "ver", "mostrar", "status", "check",
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

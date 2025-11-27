"""
Matchers de Intenciones y Dispositivos
======================================

Implementa la lógica de matching para detectar intenciones y dispositivos
a partir del texto normalizado.
"""
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

from .intents import IntentDefinitions
from .aliases import DeviceAliases, RoomAliases
from .normalizer import TextNormalizer
from .constants import NLPConstants, IntentType


@dataclass
class IntentMatch:
    """Resultado del matching de intención"""
    intent: str
    confidence: float
    matched_pattern: str
    matched_text: str


@dataclass
class DeviceMatch:
    """Resultado del matching de dispositivo"""
    device_key: str
    device_type: str
    confidence: float
    matched_alias: str
    room: Optional[str] = None


@dataclass
class EntityMatch:
    """Resultado del matching de entidad (dispositivo + ubicación)"""
    device: Optional[DeviceMatch]
    room: Optional[str]
    raw_device_text: str
    raw_room_text: str


class IntentMatcher:
    """
    Matcher de intenciones basado en patrones regex.
    Utiliza los patrones definidos en IntentDefinitions.
    """
    
    def __init__(self):
        """Inicializa el matcher compilando los patrones"""
        self.patterns = IntentDefinitions.get_compiled_patterns()
        self.normalizer = TextNormalizer()
    
    def match(self, text: str) -> IntentMatch:
        """
        Detecta la intención en el texto.
        
        Args:
            text: Texto a analizar (puede estar sin normalizar)
            
        Returns:
            IntentMatch con los resultados
        """
        # Normalizar texto para matching
        normalized = self.normalizer.normalize(text)
        
        best_match: Optional[IntentMatch] = None
        highest_confidence = 0.0
        
        # Buscar en cada tipo de intención
        for intent, pattern_list in self.patterns.items():
            for i, pattern in enumerate(pattern_list):
                match = pattern.search(normalized)
                if match:
                    # Calcular confianza basada en:
                    # - Posición del patrón (primeros = más específicos = mayor confianza)
                    # - Longitud del match
                    position_factor = 1.0 - (i * 0.05)  # Reducir 5% por cada posición
                    length_factor = min(1.0, len(match.group(0)) / 15)  # Normalizar longitud
                    
                    confidence = min(0.95, position_factor * 0.7 + length_factor * 0.3)
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = IntentMatch(
                            intent=intent,
                            confidence=confidence,
                            matched_pattern=pattern.pattern,
                            matched_text=match.group(0)
                        )
        
        # Si no se encontró ningún match
        if best_match is None:
            return IntentMatch(
                intent="unknown",
                confidence=0.0,
                matched_pattern="",
                matched_text=""
            )
        
        return best_match
    
    def get_all_matches(self, text: str) -> List[IntentMatch]:
        """
        Encuentra TODAS las intenciones que matchean en el texto.
        Útil para comandos compuestos.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de IntentMatch ordenada por confianza
        """
        normalized = self.normalizer.normalize(text)
        matches = []
        
        for intent, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = pattern.search(normalized)
                if match:
                    matches.append(IntentMatch(
                        intent=intent,
                        confidence=0.8,
                        matched_pattern=pattern.pattern,
                        matched_text=match.group(0)
                    ))
                    break  # Solo un match por tipo de intención
        
        # Ordenar por confianza
        return sorted(matches, key=lambda m: m.confidence, reverse=True)


class DeviceMatcher:
    """
    Matcher de dispositivos usando índice invertido.
    Permite búsqueda O(1) de dispositivos por alias.
    """
    
    # Preposiciones y artículos a eliminar para mejor matching
    SKIP_WORDS = {'del', 'de', 'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas', 'en', 'al'}
    
    def __init__(self, devices: Optional[List[Dict]] = None):
        """
        Inicializa el matcher con los dispositivos disponibles.
        
        Args:
            devices: Lista de dispositivos con formato:
                     [{"device_key": "...", "name": "...", "aliases": [...], "room": "..."}]
        """
        self.normalizer = TextNormalizer()
        self.devices = devices or []
        self.device_index: Dict[str, Dict] = {}  # alias -> device info
        self.room_index = RoomAliases.build_reverse_lookup()
        
        if devices:
            self._build_index(devices)
    
    def _remove_skip_words(self, text: str) -> str:
        """Elimina preposiciones y artículos del texto"""
        words = text.split()
        filtered = [w for w in words if w not in self.SKIP_WORDS]
        return ' '.join(filtered)
    
    def _build_index(self, devices: List[Dict]) -> None:
        """
        Construye el índice invertido de alias a dispositivos.
        """
        self.device_index.clear()
        
        for device in devices:
            device_key = device.get("device_key", "")
            name = device.get("name", "")
            device_type = device.get("type", "other")
            room = device.get("room", "")
            aliases = device.get("aliases", [])
            
            # Agregar nombre principal al índice
            normalized_name = self.normalizer.normalize(name)
            self.device_index[normalized_name] = {
                "device_key": device_key,
                "name": name,
                "type": device_type,
                "room": room,
            }
            
            # Agregar cada alias al índice
            for alias in aliases:
                normalized_alias = self.normalizer.normalize(alias)
                self.device_index[normalized_alias] = {
                    "device_key": device_key,
                    "name": name,
                    "type": device_type,
                    "room": room,
                }
            
            # Agregar device_key también
            normalized_key = self.normalizer.normalize(device_key)
            self.device_index[normalized_key] = {
                "device_key": device_key,
                "name": name,
                "type": device_type,
                "room": room,
            }
    
    def update_devices(self, devices: List[Dict]) -> None:
        """Actualiza el índice con nuevos dispositivos"""
        self.devices = devices
        self._build_index(devices)
    
    def match(self, text: str) -> DeviceMatch:
        """
        Busca un dispositivo en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            DeviceMatch con el dispositivo encontrado
        """
        normalized = self.normalizer.normalize(text)
        # También crear versión sin preposiciones/artículos
        normalized_clean = self._remove_skip_words(normalized)
        tokens = normalized.split()
        tokens_clean = normalized_clean.split()
        
        # Estrategia 1: Buscar frases completas (n-gramas) - primero sin preposiciones
        for n in range(min(4, len(tokens_clean)), 0, -1):
            for i in range(len(tokens_clean) - n + 1):
                phrase = ' '.join(tokens_clean[i:i+n])
                if phrase in self.device_index:
                    device = self.device_index[phrase]
                    return DeviceMatch(
                        device_key=device["device_key"],
                        device_type=device["type"],
                        confidence=0.95 if n >= 2 else 0.85,
                        matched_alias=phrase,
                        room=device.get("room")
                    )
        
        # Estrategia 2: Buscar frases completas con preposiciones (texto original)
        for n in range(min(4, len(tokens)), 0, -1):
            for i in range(len(tokens) - n + 1):
                phrase = ' '.join(tokens[i:i+n])
                if phrase in self.device_index:
                    device = self.device_index[phrase]
                    return DeviceMatch(
                        device_key=device["device_key"],
                        device_type=device["type"],
                        confidence=0.95 if n >= 2 else 0.85,
                        matched_alias=phrase,
                        room=device.get("room")
                    )
        
        # Estrategia 3: Buscar coincidencia parcial (más estricta)
        for token in tokens_clean:
            # Ignorar tokens muy cortos o stopwords comunes
            if len(token) < 4 or token in ['por', 'para', 'con', 'sin', 'que', 'del', 'las', 'los', 'una', 'uno']:
                continue
            for alias, device in self.device_index.items():
                # Solo matchear si el token es sustancial parte del alias
                if len(token) >= 4 and (token in alias.split() or alias in token):
                    return DeviceMatch(
                        device_key=device["device_key"],
                        device_type=device["type"],
                        confidence=0.70,
                        matched_alias=alias,
                        room=device.get("room")
                    )
        
        # No se encontró dispositivo
        return DeviceMatch(
            device_key="",
            device_type="unknown",
            confidence=0.0,
            matched_alias="",
            room=None
        )
    
    def match_room(self, text: str) -> Optional[str]:
        """
        Detecta la habitación mencionada en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Nombre canónico de la habitación o None
        """
        normalized = self.normalizer.normalize(text)
        
        # Buscar patrones de ubicación
        location_patterns = [
            r"(?:en|de|del)\s+(?:el|la|los|las)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*$",  # Última palabra/frase
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, normalized)
            if match:
                potential_room = match.group(1).strip()
                # Verificar si es una habitación conocida
                if potential_room in self.room_index:
                    return self.room_index[potential_room]
        
        return None


class EntityExtractor:
    """
    Extractor de entidades que combina dispositivo y ubicación.
    """
    
    def __init__(self, devices: Optional[List[Dict]] = None):
        self.device_matcher = DeviceMatcher(devices)
        self.normalizer = TextNormalizer()
        self.room_aliases = RoomAliases.build_reverse_lookup()
    
    def update_devices(self, devices: List[Dict]) -> None:
        """Actualiza los dispositivos disponibles"""
        self.device_matcher.update_devices(devices)
    
    def extract(self, text: str) -> EntityMatch:
        """
        Extrae dispositivo y ubicación del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            EntityMatch con dispositivo y ubicación
        """
        normalized = self.normalizer.normalize(text)
        
        # Extraer dispositivo
        device_match = self.device_matcher.match(text)
        
        # Extraer ubicación
        room = self._extract_room(normalized)
        
        # Si el dispositivo ya tiene room, usar ese
        if device_match.room and not room:
            room = device_match.room
        
        return EntityMatch(
            device=device_match if device_match.device_key else None,
            room=room,
            raw_device_text=device_match.matched_alias,
            raw_room_text=room or ""
        )
    
    def _extract_room(self, text: str) -> Optional[str]:
        """Extrae la ubicación del texto"""
        # Patrones para detectar ubicación
        patterns = [
            r"(?:en|de|del)\s+(?:el|la|los|las)?\s*(\w+(?:\s+\w+)?)",
            r"(?:habitacion|cuarto|sala)\s+(?:de|del)?\s*(\w+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                normalized_match = match.strip().lower()
                if normalized_match in self.room_aliases:
                    return self.room_aliases[normalized_match]
        
        # Buscar nombres de habitaciones directamente
        words = text.split()
        for i in range(len(words)):
            # Probar combinaciones de 1-3 palabras
            for j in range(i + 1, min(i + 4, len(words) + 1)):
                phrase = ' '.join(words[i:j])
                if phrase in self.room_aliases:
                    return self.room_aliases[phrase]
        
        return None
    
    def get_device_by_room(self, room: str, device_type: str) -> Optional[DeviceMatch]:
        """
        Busca un dispositivo específico en una habitación.
        
        Args:
            room: Habitación donde buscar
            device_type: Tipo de dispositivo (light, fan, etc.)
            
        Returns:
            DeviceMatch si se encuentra
        """
        normalized_room = self.normalizer.normalize(room)
        
        for device in self.device_matcher.devices:
            device_room = self.normalizer.normalize(device.get("room", ""))
            device_type_val = device.get("type", "")
            
            if normalized_room in device_room and device_type_val == device_type:
                return DeviceMatch(
                    device_key=device["device_key"],
                    device_type=device_type_val,
                    confidence=0.80,
                    matched_alias=device["name"],
                    room=device.get("room")
                )
        
        return None

"""
Pipeline NLP para interpretación de comandos domóticos usando Ollama con Phi3
=============================================================================

Pipeline híbrido que combina:
1. Sistema de reglas basado en patrones (rápido, ~1ms)
2. Ollama/Phi3 como respaldo (potente, ~2-5s)
3. Detección de negaciones para comandos cancelados
"""
import json
import httpx
import logging
import re
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from functools import lru_cache

from config.settings import settings

# Importar componentes del módulo NLP
from nlp import (
    TextNormalizer,
    IntentMatcher,
    DeviceMatcher,
    EntityExtractor,
    NegationDetector,
    NLPConstants,
    IntentType,
)

logger = logging.getLogger(__name__)


class NLPPipeline:
    """
    Pipeline de procesamiento de lenguaje natural para comandos domóticos.
    
    Combina:
    - Sistema de reglas basado en patrones (rápido, ~1ms)
    - Ollama/Phi3 como respaldo inteligente (potente, ~2-5s)
    - Detección de negaciones para comandos cancelados
    """
    
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.OLLAMA_MODEL
        
        # Cargar datos de dispositivos
        self.devices_data = self._load_devices()
        
        # Inicializar componentes NLP del módulo
        self.normalizer = TextNormalizer()
        self.negation_detector = NegationDetector()
        self.intent_matcher = IntentMatcher()
        self.device_matcher = DeviceMatcher(self._get_devices_list())
        self.entity_extractor = EntityExtractor(self._get_devices_list())
        
        # Sistema de prompts para Ollama
        self.system_prompt = self._build_system_prompt()
        self._ollama_available: Optional[bool] = None
    
    def _get_devices_list(self) -> List[Dict]:
        """Convierte el diccionario de dispositivos a lista para los matchers"""
        devices = self.devices_data.get("devices", {})
        result = []
        for key, info in devices.items():
            result.append({
                "device_key": key,
                "name": info.get("name", key),
                "type": info.get("type", "other"),
                "room": info.get("room", ""),
                "aliases": info.get("aliases", []),
            })
        return result
        
    def _load_devices(self) -> Dict[str, Any]:
        """Carga el archivo de dispositivos JSON"""
        devices_path = Path(__file__).parent.parent / settings.DEVICES_FILE
        try:
            with open(devices_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Cargados {len(data.get('devices', {}))} dispositivos desde {devices_path}")
                return data
        except FileNotFoundError:
            logger.error(f"Archivo de dispositivos no encontrado: {devices_path}")
            return {"devices": {}, "rooms": {}, "device_types": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear archivo de dispositivos: {e}")
            return {"devices": {}, "rooms": {}, "device_types": {}}
    
    @lru_cache(maxsize=1)
    def _build_system_prompt(self) -> str:
        """
        Construye el prompt del sistema optimizado para Phi3.
        Usa formato conciso para minimizar tokens y maximizar precisión.
        """
        # Construir lista compacta de dispositivos
        device_lines = []
        for key, device in self.devices_data.get("devices", {}).items():
            device_lines.append(f"{key}|{device['type']}|{device['room']}")
        
        devices_compact = "\n".join(device_lines)
        
        prompt = f"""Eres un parser de comandos domóticos. Extrae intent y device del comando en español.

INTENTS: turn_on, turn_off, open, close, status, negated, unknown

DEVICES (key|type|room):
{devices_compact}

REGLAS:
- Responde SOLO JSON: {{"intent":"X","device":"Y","negated":false}}
- device=null si no se identifica
- intent=unknown si no es comando domótico
- negated=true si el comando es negativo ("no enciendas", "no abras")
- turn_on/turn_off: luces, ventiladores, alarmas
- open/close: puertas, ventanas, cortinas

EJEMPLOS:
"enciende luz comedor" → {{"intent":"turn_on","device":"luz_comedor","negated":false}}
"no enciendas la luz" → {{"intent":"turn_on","device":"luz_sala","negated":true}}
"apaga ventilador sala" → {{"intent":"turn_off","device":"ventilador_sala","negated":false}}
"no apagues el ventilador" → {{"intent":"turn_off","device":"ventilador_sala","negated":true}}
"abre puerta garage" → {{"intent":"open","device":"puerta_garage","negated":false}}
"no abras la puerta" → {{"intent":"open","device":"puerta_principal","negated":true}}
"estado luz cocina" → {{"intent":"status","device":"luz_cocina","negated":false}}

Solo JSON, sin explicaciones."""

        return prompt

    async def check_ollama_connection(self) -> bool:
        """Verifica la conexión con Ollama y cachea el resultado"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                self._ollama_available = response.status_code == 200
                return self._ollama_available
        except Exception as e:
            logger.error(f"Error conectando con Ollama: {e}")
            self._ollama_available = False
            return False

    async def interpret(self, user_command: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Pipeline de interpretación híbrido:
        1. Detecta negaciones primero
        2. Intenta con el sistema de reglas (rápido y confiable)
        3. Si la confianza es baja, usa Ollama como respaldo
        
        Args:
            user_command: Comando en lenguaje natural del usuario
            
        Returns:
            Tupla con (resultado_interpretación, nota_de_confianza)
        """
        # Paso 0: Detectar negaciones
        negation_result = self.negation_detector.detect(user_command)
        is_negated = negation_result.is_negated
        
        # Si hay negación, procesar el comando sin la negación para detectar intent
        command_to_process = user_command
        if is_negated:
            command_to_process = self.negation_detector.remove_negation(user_command)
            logger.info(f"Negación detectada. Comando original: '{user_command}' -> Sin negación: '{command_to_process}'")
        
        # Paso 1: Interpretación basada en reglas
        rule_based_result = self._rule_based_interpretation(command_to_process)
        intent_confidence = rule_based_result.get("intent_confidence", 0)
        device_confidence = rule_based_result.get("device_confidence", 0)
        
        # Agregar flag de negación al resultado
        rule_based_result["negated"] = is_negated
        
        # Si la confianza es alta, usar resultado de reglas
        if intent_confidence >= 0.8 and device_confidence >= 0.7:
            logger.info(f"Interpretación por reglas: intent={rule_based_result['intent']}, device={rule_based_result['device']}, negated={is_negated}")
            return self._format_result(rule_based_result), None
        
        # Paso 2: Si la confianza es baja, intentar con Ollama
        if self._ollama_available is None:
            await self.check_ollama_connection()
        
        if self._ollama_available:
            ollama_result, confidence_note = await self._ollama_interpretation(user_command)
            
            # Si Ollama no detectó negación pero nosotros sí, usar nuestra detección
            if is_negated and not ollama_result.get("negated", False):
                ollama_result["negated"] = True
            
            # Combinar resultados: preferir Ollama si tuvo éxito, sino usar reglas
            if ollama_result["intent"] != "unknown" or rule_based_result["intent"] == "unknown":
                return ollama_result, confidence_note
        
        # Paso 3: Fallback a reglas si Ollama no está disponible o falló
        confidence_note = None
        if rule_based_result["intent"] == "unknown":
            confidence_note = "No se pudo identificar una intención válida"
        elif rule_based_result["device"] is None:
            confidence_note = "Intención identificada pero dispositivo no especificado"
        
        if not self._ollama_available:
            confidence_note = (confidence_note or "") + " (Ollama no disponible)"
        
        return self._format_result(rule_based_result), confidence_note.strip() if confidence_note else None
    
    def _rule_based_interpretation(self, user_command: str) -> Dict[str, Any]:
        """Interpretación basada en reglas y patrones usando módulos NLP"""
        # Detectar intención usando el IntentMatcher del módulo nlp
        intent_match = self.intent_matcher.match(user_command)
        
        # Detectar dispositivo usando el DeviceMatcher del módulo nlp
        device_match = self.device_matcher.match(user_command)
        
        return {
            "intent": intent_match.intent,
            "device": device_match.device_key if device_match.device_key else None,
            "intent_confidence": intent_match.confidence,
            "device_confidence": device_match.confidence,
            "negated": False  # Se establece después
        }
    
    def _format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea el resultado eliminando campos de confianza internos"""
        return {
            "intent": result["intent"],
            "device": result["device"],
            "negated": result.get("negated", False)
        }
    
    async def _ollama_interpretation(self, user_command: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """Interpretación usando Ollama/Phi3"""
        full_prompt = f"""{self.system_prompt}

Comando: "{user_command}"
JSON:"""

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 100,  # Respuesta para incluir negated
                            "stop": ["\n", "```"]  # Parar después del JSON
                        }
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Error de Ollama: {response.status_code}")
                    self._ollama_available = False
                    return {"intent": "unknown", "device": None, "negated": False}, "Error en Ollama"
                
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                logger.debug(f"Respuesta de Ollama: {generated_text}")
                
                interpretation = self._parse_model_response(generated_text)
                interpretation = self._validate_device(interpretation)
                
                confidence_note = None
                if interpretation["intent"] == "unknown":
                    confidence_note = "Intención no reconocida"
                elif interpretation["device"] is None and interpretation["intent"] != "unknown":
                    confidence_note = "Dispositivo no especificado"
                
                return interpretation, confidence_note
                
        except httpx.TimeoutException:
            logger.error("Timeout al conectar con Ollama")
            self._ollama_available = False
            return {"intent": "unknown", "device": None, "negated": False}, "Timeout de Ollama"
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")
            return {"intent": "unknown", "device": None, "negated": False}, f"Error: {str(e)}"
    
    def _parse_model_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del modelo para extraer el JSON.
        Maneja múltiples formatos de respuesta del LLM.
        """
        # Limpiar respuesta
        text = response_text.strip()
        
        # Intentar parsear directamente
        try:
            parsed = json.loads(text)
            # Asegurar que negated esté presente
            if "negated" not in parsed:
                parsed["negated"] = False
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Buscar JSON en la respuesta con regex más robusto
        patterns = [
            r'\{[^{}]*"intent"\s*:\s*"[^"]+"\s*,\s*"device"\s*:\s*(?:"[^"]+"|null)[^{}]*\}',
            r'\{[^{}]*"device"\s*:\s*(?:"[^"]+"|null)\s*,\s*"intent"\s*:\s*"[^"]+"\s*[^{}]*\}',
            r'\{[^}]+\}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if "intent" in parsed:
                        if "negated" not in parsed:
                            parsed["negated"] = False
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Extraer valores manualmente como último recurso
        intent = "unknown"
        device = None
        negated = False
        
        # Buscar intent
        intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
        if intent_match:
            found_intent = intent_match.group(1).lower()
            if found_intent in ["turn_on", "turn_off", "open", "close", "status", "unknown", "negated"]:
                intent = found_intent
        
        # Buscar device
        device_match = re.search(r'"device"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
        if device_match:
            device = device_match.group(1)
        elif "null" in text.lower():
            device = None
        
        # Buscar negated
        negated_match = re.search(r'"negated"\s*:\s*(true|false)', text, re.IGNORECASE)
        if negated_match:
            negated = negated_match.group(1).lower() == "true"
        
        return {"intent": intent, "device": device, "negated": negated}
    
    def _validate_device(self, interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """Valida que el dispositivo exista en la lista de dispositivos conocidos."""
        device = interpretation.get("device")
        
        if device is None:
            return interpretation
            
        if device in self.devices_data.get("devices", {}):
            return interpretation
        
        # Intentar encontrar dispositivo similar
        device_normalized = self.normalizer.normalize(device)
        
        for key in self.devices_data.get("devices", {}).keys():
            key_normalized = self.normalizer.normalize(key)
            if device_normalized in key_normalized or key_normalized in device_normalized:
                interpretation["device"] = key
                return interpretation
        
        # No se encontró dispositivo válido
        interpretation["device"] = None
        return interpretation
    
    def get_available_devices(self) -> Dict[str, Any]:
        """Retorna la lista de dispositivos disponibles"""
        return self.devices_data.get("devices", {})
    
    def get_device_info(self, device_key: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un dispositivo específico"""
        return self.devices_data.get("devices", {}).get(device_key)
    
    def reload_devices(self) -> bool:
        """Recarga el archivo de dispositivos (útil para actualizaciones en caliente)"""
        try:
            self.devices_data = self._load_devices()
            devices_list = self._get_devices_list()
            self.device_matcher.update_devices(devices_list)
            self.entity_extractor.update_devices(devices_list)
            self._build_system_prompt.cache_clear()
            self.system_prompt = self._build_system_prompt()
            logger.info("Dispositivos recargados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error recargando dispositivos: {e}")
            return False


# Instancia singleton del pipeline
nlp_pipeline = NLPPipeline()

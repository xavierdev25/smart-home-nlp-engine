"""
Ejemplo de integración del NLP Service con un Backend IoT
Este archivo muestra cómo tu backend principal puede usar el servicio NLP
"""
import httpx
from typing import Optional, Dict, Any

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

NLP_SERVICE_URL = "http://localhost:8001"  # Tu servicio NLP

# Mapeo de dispositivos NLP -> Endpoints de tu Backend IoT
# Ajusta esto según los endpoints reales de tu sistema
IOT_ENDPOINTS = {
    # Luces
    "luz_sala": {"on": "/api/lights/sala/on", "off": "/api/lights/sala/off", "status": "/api/lights/sala/status"},
    "luz_cocina": {"on": "/api/lights/cocina/on", "off": "/api/lights/cocina/off", "status": "/api/lights/cocina/status"},
    "luz_comedor": {"on": "/api/lights/comedor/on", "off": "/api/lights/comedor/off", "status": "/api/lights/comedor/status"},
    "luz_bano": {"on": "/api/lights/bano/on", "off": "/api/lights/bano/off", "status": "/api/lights/bano/status"},
    "luz_dormitorio_principal": {"on": "/api/lights/dormitorio/on", "off": "/api/lights/dormitorio/off", "status": "/api/lights/dormitorio/status"},
    
    # Ventiladores
    "ventilador_sala": {"on": "/api/fans/sala/on", "off": "/api/fans/sala/off", "status": "/api/fans/sala/status"},
    "ventilador_dormitorio_principal": {"on": "/api/fans/dormitorio/on", "off": "/api/fans/dormitorio/off", "status": "/api/fans/dormitorio/status"},
    
    # Puertas
    "puerta_principal": {"open": "/api/doors/principal/open", "close": "/api/doors/principal/close", "status": "/api/doors/principal/status"},
    "puerta_garage": {"open": "/api/doors/garage/open", "close": "/api/doors/garage/close", "status": "/api/doors/garage/status"},
    
    # Cortinas
    "cortina_sala": {"open": "/api/curtains/sala/open", "close": "/api/curtains/sala/close", "status": "/api/curtains/sala/status"},
    "cortina_dormitorio_principal": {"open": "/api/curtains/dormitorio/open", "close": "/api/curtains/dormitorio/close", "status": "/api/curtains/dormitorio/status"},
    
    # Alarmas
    "alarma_principal": {"on": "/api/alarm/on", "off": "/api/alarm/off", "status": "/api/alarm/status"},
}

# Mapeo de intents -> acciones
INTENT_TO_ACTION = {
    "turn_on": "on",
    "turn_off": "off",
    "open": "open",
    "close": "close",
    "status": "status",
}


# =============================================================================
# CLIENTE NLP
# =============================================================================

class SmartHomeNLPClient:
    """Cliente para interactuar con el servicio NLP y ejecutar acciones IoT"""
    
    def __init__(self, nlp_url: str, iot_base_url: str):
        self.nlp_url = nlp_url
        self.iot_base_url = iot_base_url
    
    async def interpret_command(self, text: str) -> Dict[str, Any]:
        """
        Envía un comando al servicio NLP y obtiene la interpretación.
        
        Args:
            text: Comando en lenguaje natural
            
        Returns:
            Diccionario con intent y device
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.nlp_url}/interpret",
                json={"text": text}
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result["data"]
            else:
                raise Exception(f"Error en NLP: {result}")
    
    async def execute_action(self, intent: str, device: str) -> Dict[str, Any]:
        """
        Ejecuta la acción correspondiente en el backend IoT.
        
        Args:
            intent: Intención (turn_on, turn_off, open, close, status)
            device: Clave del dispositivo (ej: luz_comedor)
            
        Returns:
            Respuesta del backend IoT
        """
        # Obtener la acción correspondiente al intent
        action = INTENT_TO_ACTION.get(intent)
        if not action:
            return {"success": False, "error": f"Intent no soportado: {intent}"}
        
        # Obtener el endpoint del dispositivo
        device_endpoints = IOT_ENDPOINTS.get(device)
        if not device_endpoints:
            return {"success": False, "error": f"Dispositivo no configurado: {device}"}
        
        endpoint = device_endpoints.get(action)
        if not endpoint:
            return {"success": False, "error": f"Acción '{action}' no disponible para {device}"}
        
        # Ejecutar la llamada al backend IoT
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Usar POST para acciones, GET para status
                if action == "status":
                    response = await client.get(f"{self.iot_base_url}{endpoint}")
                else:
                    response = await client.post(f"{self.iot_base_url}{endpoint}")
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"success": False, "error": str(e)}
    
    async def process_voice_command(self, text: str) -> Dict[str, Any]:
        """
        Procesa un comando de voz completo: interpreta y ejecuta.
        
        Args:
            text: Comando en lenguaje natural
            
        Returns:
            Resultado completo de la operación
        """
        # Paso 1: Interpretar el comando
        interpretation = await self.interpret_command(text)
        
        intent = interpretation.get("intent")
        device = interpretation.get("device")
        
        # Paso 2: Validar interpretación
        if intent == "unknown":
            return {
                "success": False,
                "message": "No entendí el comando. Por favor, intenta de nuevo.",
                "interpretation": interpretation
            }
        
        if device is None:
            return {
                "success": False,
                "message": f"Entendí que quieres '{intent}', pero no identifiqué el dispositivo.",
                "interpretation": interpretation
            }
        
        # Paso 3: Ejecutar la acción
        result = await self.execute_action(intent, device)
        
        return {
            "success": result.get("success", False),
            "message": self._generate_response_message(intent, device, result),
            "interpretation": interpretation,
            "iot_response": result
        }
    
    def _generate_response_message(self, intent: str, device: str, result: Dict) -> str:
        """Genera un mensaje de respuesta amigable para el usuario"""
        device_name = device.replace("_", " ")
        
        if not result.get("success"):
            return f"No pude ejecutar la acción en {device_name}. Error: {result.get('error', 'desconocido')}"
        
        messages = {
            "turn_on": f"Listo, he encendido {device_name}",
            "turn_off": f"Listo, he apagado {device_name}",
            "open": f"Listo, he abierto {device_name}",
            "close": f"Listo, he cerrado {device_name}",
            "status": f"El estado de {device_name} es: {result.get('state', 'desconocido')}",
        }
        
        return messages.get(intent, f"Acción completada en {device_name}")


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

async def main():
    """Ejemplo de uso del cliente NLP para casa inteligente"""
    
    # Configuración - ajusta estas URLs a tu entorno
    NLP_URL = "http://localhost:8001"      # Servicio NLP
    IOT_URL = "http://localhost:3000"       # Tu backend IoT (Node.js, Flask, etc.)
    
    client = SmartHomeNLPClient(NLP_URL, IOT_URL)
    
    # Ejemplos de comandos
    comandos = [
        "enciende la luz del comedor",
        "apaga el ventilador de la sala",
        "abre la puerta del garage",
        "¿está encendida la luz de la cocina?",
        "cierra las cortinas del dormitorio",
        "activa la alarma",
    ]
    
    print("=" * 60)
    print("🏠 Sistema de Casa Inteligente - Prueba de Comandos")
    print("=" * 60)
    
    for comando in comandos:
        print(f"\n📢 Comando: \"{comando}\"")
        
        try:
            # Solo interpretar (sin ejecutar IoT para esta demo)
            interpretation = await client.interpret_command(comando)
            print(f"   ✅ Intent: {interpretation['intent']}")
            print(f"   🔧 Device: {interpretation['device']}")
            
            # Para ejecutar realmente, descomentar:
            # result = await client.process_voice_command(comando)
            # print(f"   📝 Respuesta: {result['message']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

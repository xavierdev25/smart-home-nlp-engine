"""
Microservicio NLP para interpretación de comandos domóticos
API FastAPI que utiliza Ollama con Phi3 para procesamiento de lenguaje natural
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from models.schemas import (
    CommandInput,
    InterpretationResult,
    InterpretationResponse,
    HealthResponse,
    ErrorResponse
)
from services.nlp_pipeline import nlp_pipeline

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Inicializar base de datos
    from database.connection import init_db
    init_db()
    logger.info("Base de datos inicializada")
    
    # Verificar conexión con Ollama
    ollama_ok = await nlp_pipeline.check_ollama_connection()
    if ollama_ok:
        logger.info(f"Conexión con Ollama establecida - Modelo: {settings.OLLAMA_MODEL}")
    else:
        logger.warning("No se pudo conectar con Ollama. El servicio usará interpretación de respaldo.")
    
    yield
    
    # Shutdown
    logger.info("Cerrando servicio NLP...")


# Crear aplicación FastAPI con documentación OpenAPI mejorada
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# 🏠 Smart Home NLP Engine - Bilingual Voice Controller

Microservicio NLP que interpreta comandos de voz/texto en **Español** e **Inglés** 
y los convierte en acciones estructuradas para sistemas de automatización del hogar.

## 🌍 Bilingual Support / Soporte Bilingüe

| Language | Commands | TTS Voices | Example |
|----------|----------|------------|---------|
| 🇪🇸 Español | 50+ patterns | 8 voices | "enciende la luz del salón" |
| 🇺🇸 English | 40+ patterns | 7 voices | "turn on the living room light" |

## 🚀 Main Features / Características Principales

| Feature | Description |
|---------|-------------|
| **Hybrid Pipeline** | Regex rules (~1ms) + LLM Ollama/Phi3 (~2-5s) fallback |
| **Negation Detection** | 5 types: direct, pronoun, compound, prohibitive, implicit |
| **Bilingual NLP** | ES + EN patterns, aliases, and responses |
| **Voice Control** | STT (Google/Whisper) + TTS (gTTS/Edge-TTS) |
| **Extensible** | Easy to add devices, rooms, and patterns |

## 🎯 Supported Intents / Intenciones Soportadas

| Intent | Spanish | English |
|--------|---------|---------|
| `turn_on` | "enciende", "prende", "activa" | "turn on", "switch on", "power on" |
| `turn_off` | "apaga", "desactiva" | "turn off", "switch off", "power off" |
| `open` | "abre", "abrir" | "open", "unlock" |
| `close` | "cierra", "cerrar" | "close", "shut", "lock" |
| `status` | "estado", "cómo está" | "status", "check", "how is" |
| `toggle` | "alterna", "cambia" | "toggle", "flip" |

## 📦 Supported Devices / Dispositivos

Lights, fans, doors, windows, blinds, curtains, alarms, sensors, thermostats, smart locks, and more.

## 🔄 Data Flow / Flujo de Datos

```
Text → Normalization → Negation Detection → Intent Matching → Device Matching → JSON Result
                                    ↓
                              Ollama/Phi3 (low confidence fallback)
```

## 🔊 Voice Endpoints / Endpoints de Voz

| Endpoint | Description |
|----------|-------------|
| `POST /voice/interpret` | Audio → Text → NLP → Response |
| `POST /voice/synthesize` | Text → Audio (MP3) |
| `GET /voice/voices` | List available TTS voices |
| `POST /voice/stt` | Speech-to-Text only |
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "NLP",
            "description": "Natural Language Processing endpoints - Bilingual ES/EN support for interpreting and executing smart home commands",
        },
        {
            "name": "Voz",
            "description": "Voice Control: Speech-to-Text (STT) and Text-to-Speech (TTS) with 15 voices (8 ES + 7 EN)",
        },
        {
            "name": "Dispositivos",
            "description": "IoT Device Management - Configure and query connected devices",
        },
        {
            "name": "Sistema",
            "description": "System Monitoring - Health checks and service status",
        }
    ],
    contact={
        "name": "Smart Home NLP Engine",
        "url": "https://github.com/xavierdev25/smart-home-nlp-engine",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
from routers.devices import router as devices_router
from routers.voice import router as voice_router
app.include_router(devices_router)
app.include_router(voice_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Sistema"],
    summary="Verificar estado del servicio",
    responses={
        200: {
            "description": "Servicio operativo",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy": {
                            "summary": "Servicio completamente operativo",
                            "value": {
                                "status": "healthy",
                                "service": "NLP Service - Smart Home",
                                "version": "1.0.0",
                                "ollama_status": "connected"
                            }
                        },
                        "degraded": {
                            "summary": "Servicio degradado (sin Ollama)",
                            "value": {
                                "status": "healthy",
                                "service": "NLP Service - Smart Home",
                                "version": "1.0.0",
                                "ollama_status": "disconnected"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    ## 🔍 Health Check del Servicio
    
    Verifica el estado del servicio NLP y sus dependencias.
    
    ### Estados de Ollama
    
    | Estado | Descripción |
    |--------|-------------|
    | `connected` | Ollama disponible - fallback LLM activo |
    | `disconnected` | Ollama no disponible - solo reglas básicas |
    
    ### Uso
    ```bash
    curl http://localhost:8001/health
    ```
    """
    ollama_ok = await nlp_pipeline.check_ollama_connection()
    
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        ollama_status="connected" if ollama_ok else "disconnected"
    )


@app.post(
    "/interpret",
    response_model=InterpretationResponse,
    responses={
        200: {
            "description": "Successful interpretation / Interpretación exitosa",
            "content": {
                "application/json": {
                    "examples": {
                        "spanish_basic": {
                            "summary": "🇪🇸 Comando básico (ES)",
                            "value": {
                                "success": True,
                                "data": {"intent": "turn_on", "device": "luz_comedor", "negated": False},
                                "original_text": "enciende la luz del comedor",
                                "confidence_note": None
                            }
                        },
                        "english_basic": {
                            "summary": "🇺🇸 Basic command (EN)",
                            "value": {
                                "success": True,
                                "data": {"intent": "turn_on", "device": "luz_salon", "negated": False},
                                "original_text": "turn on the living room light",
                                "confidence_note": None
                            }
                        },
                        "spanish_negated": {
                            "summary": "🇪🇸 Comando negado (ES)",
                            "value": {
                                "success": True,
                                "data": {"intent": "turn_on", "device": "luz_comedor", "negated": True},
                                "original_text": "no enciendas la luz",
                                "confidence_note": None
                            }
                        },
                        "english_negated": {
                            "summary": "🇺🇸 Negated command (EN)",
                            "value": {
                                "success": True,
                                "data": {"intent": "turn_on", "device": "luz_salon", "negated": True},
                                "original_text": "don't turn on the light",
                                "confidence_note": None
                            }
                        },
                        "unknown": {
                            "summary": "❓ Unrecognized / No reconocido",
                            "value": {
                                "success": True,
                                "data": {"intent": "unknown", "device": None, "negated": False},
                                "original_text": "quiero pizza",
                                "confidence_note": "No se pudo identificar una intención válida"
                            }
                        }
                    }
                }
            }
        },
        422: {"description": "Validation error / Error de validación"},
        500: {"description": "Internal server error / Error interno", "model": ErrorResponse}
    },
    tags=["NLP"],
    summary="Interpret natural language command / Interpretar comando"
)
async def interpret_command(command: CommandInput):
    """
    ## 🧠 Interpret Natural Language Command / Interpretar Comando
    
    Processes text in **Spanish** or **English** and extracts **intent**, **device**, and **negation**.
    
    ### Processing Pipeline
    
    1. **Normalization** → lowercase, no accents, no punctuation
    2. **Negation Detection** → "no", "don't", "never", "deja de", etc.
    3. **Intent Matching** → 90+ regex patterns (ES + EN)
    4. **Device Matching** → inverted index O(1)
    5. **Validation** → if confidence < 0.8, uses Ollama/Phi3
    
    ### Detected Negation Types / Tipos de Negaciones
    
    | Type | Spanish | English |
    |------|---------|---------|
    | Direct | "**no** enciendas" | "**don't** turn on" |
    | Never | "**nunca** enciendas" | "**never** turn on" |
    | Stop | "**deja de** encender" | "**stop** turning on" |
    | Prohibitive | "**no quiero que**" | "**do not** turn on" |
    | Implicit | "**mejor no**" | "**please don't**" |
    
    ### Examples / Ejemplos
    
    **Spanish:**
    ```bash
    curl -X POST "http://localhost:8001/interpret" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "enciende la luz del comedor"}'
    ```
    
    **English:**
    ```bash
    curl -X POST "http://localhost:8001/interpret" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "turn on the living room light"}'
    ```
    """
    try:
        logger.info(f"Procesando comando: {command.text}")
        
        # Interpretar el comando usando el pipeline NLP
        result, confidence_note = await nlp_pipeline.interpret(command.text)
        
        logger.info(f"Resultado: intent={result['intent']}, device={result['device']}, negated={result.get('negated', False)}")
        
        return InterpretationResponse(
            success=True,
            data=InterpretationResult(
                intent=result["intent"],
                device=result["device"],
                negated=result.get("negated", False)
            ),
            original_text=command.text,
            confidence_note=confidence_note
        )
        
    except Exception as e:
        logger.error(f"Error procesando comando: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el comando: {str(e)}"
        )


@app.post(
    "/execute",
    tags=["NLP"],
    summary="Interpretar y ejecutar comando (opcional)",
    responses={
        200: {
            "description": "Comando procesado",
            "content": {
                "application/json": {
                    "examples": {
                        "executed": {
                            "summary": "Comando ejecutado exitosamente",
                            "value": {
                                "success": True,
                                "interpretation": {"intent": "turn_on", "device": "luz_comedor", "negated": False},
                                "execution": {
                                    "executed": True,
                                    "endpoint_called": "http://iot-backend/api/devices/luz_comedor/on",
                                    "status_code": 200,
                                    "response": {"status": "ok"}
                                },
                                "original_text": "enciende la luz del comedor"
                            }
                        },
                        "negated_not_executed": {
                            "summary": "Comando negado (NO ejecutado)",
                            "value": {
                                "success": True,
                                "interpretation": {"intent": "turn_on", "device": "luz_comedor", "negated": True},
                                "execution": {
                                    "executed": False,
                                    "reason": "Comando negado - no se ejecuta la acción",
                                    "message": "Entendido, NO se ejecutará turn_on en luz_comedor"
                                },
                                "original_text": "no enciendas la luz del comedor"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def execute_command(command: CommandInput):
    """
    ## ⚡ Interpreta y Ejecuta un Comando
    
    Este endpoint combina interpretación NLP + ejecución de la acción.
    
    ### Flujo de Ejecución
    
    ```
    Texto → NLP Pipeline → Validación → Backend IoT
                              ↓
                    ¿Negado? → NO ejecutar
    ```
    
    ### ⚠️ Comportamiento con Negaciones
    
    Si el comando está **negado** (`negated: true`), la acción **NO se ejecuta**
    y se retorna un mensaje confirmando que se respetó la negación del usuario.
    
    ### Configuración Requerida
    
    Para que la ejecución funcione, configurar en `settings.py`:
    - `IOT_BACKEND_URL`: URL base del backend IoT
    - Endpoints de dispositivos en `devices.json` o base de datos
    
    ### Ejemplo
    
    ```bash
    curl -X POST "http://localhost:8001/execute" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "enciende la luz del comedor"}'
    ```
    """
    import httpx
    from services.device_service import DeviceService
    from database.connection import SessionLocal
    
    try:
        # 1. Interpretar el comando
        result, confidence_note = await nlp_pipeline.interpret(command.text)
        
        interpretation = {
            "intent": result["intent"],
            "device": result["device"],
            "negated": result.get("negated", False)
        }
        
        # 2. Si el comando está negado, no ejecutar
        if result.get("negated", False):
            return {
                "success": True,
                "interpretation": interpretation,
                "execution": {
                    "executed": False,
                    "reason": "Comando negado - no se ejecuta la acción",
                    "message": f"Entendido, NO se ejecutará {result['intent']} en {result['device']}"
                },
                "original_text": command.text
            }
        
        # 3. Si no hay dispositivo o intent desconocido, no ejecutar
        if result["intent"] == "unknown" or not result["device"]:
            return {
                "success": True,
                "interpretation": interpretation,
                "execution": {
                    "executed": False,
                    "reason": "No se pudo identificar dispositivo o intención"
                },
                "original_text": command.text,
                "confidence_note": confidence_note
            }
        
        # 4. Obtener endpoint del dispositivo
        if not settings.IOT_BACKEND_URL:
            return {
                "success": True,
                "interpretation": interpretation,
                "execution": {
                    "executed": False,
                    "reason": "IOT_BACKEND_URL no configurado",
                    "message": "Configure IOT_BACKEND_URL para habilitar ejecución de comandos"
                },
                "original_text": command.text
            }
        
        # Mapear intent a acción
        intent_to_action = {
            "turn_on": "on",
            "turn_off": "off",
            "open": "open",
            "close": "close",
            "status": "status"
        }
        action = intent_to_action.get(result["intent"])
        
        if not action:
            return {
                "success": True,
                "interpretation": interpretation,
                "execution": {
                    "executed": False,
                    "reason": f"Acción '{result['intent']}' no soportada para ejecución"
                },
                "original_text": command.text
            }
        
        # 5. Obtener endpoint de la base de datos
        db = SessionLocal()
        try:
            device_service = DeviceService(db)
            endpoint = device_service.get_endpoint(result["device"], action)
        finally:
            db.close()
        
        if not endpoint:
            # Construir endpoint por defecto
            endpoint = f"{settings.IOT_BACKEND_URL}/api/devices/{result['device']}/{action}"
        
        # 6. Ejecutar llamada al backend IoT
        execution_result = {
            "executed": False,
            "endpoint_called": endpoint
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if action == "status":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint)
                
                execution_result["executed"] = response.status_code in [200, 201, 204]
                execution_result["status_code"] = response.status_code
                
                try:
                    execution_result["response"] = response.json()
                except:
                    execution_result["response"] = response.text[:200] if response.text else None
                    
        except httpx.TimeoutException:
            execution_result["error"] = "Timeout al conectar con el backend IoT"
        except Exception as e:
            execution_result["error"] = str(e)
        
        return {
            "success": True,
            "interpretation": interpretation,
            "execution": execution_result,
            "original_text": command.text,
            "confidence_note": confidence_note
        }
        
    except Exception as e:
        logger.error(f"Error ejecutando comando: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar el comando: {str(e)}"
        )


@app.get(
    "/devices",
    tags=["Dispositivos"],
    summary="Listar dispositivos disponibles"
)
async def list_devices():
    """
    Devuelve la lista de todos los dispositivos configurados en el sistema.
    Útil para debugging y para conocer los device_keys válidos.
    """
    devices = nlp_pipeline.get_available_devices()
    return {
        "success": True,
        "total": len(devices),
        "devices": devices
    }


@app.get(
    "/devices/{device_key}",
    tags=["Dispositivos"],
    summary="Obtener información de un dispositivo"
)
async def get_device(device_key: str):
    """
    Obtiene información detallada de un dispositivo específico.
    """
    device = nlp_pipeline.get_device_info(device_key)
    
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo '{device_key}' no encontrado"
        )
    
    return {
        "success": True,
        "device_key": device_key,
        "device": device
    }


@app.post(
    "/devices/reload",
    tags=["Dispositivos"],
    summary="Recargar configuración de dispositivos"
)
async def reload_devices():
    """
    Recarga el archivo de dispositivos sin reiniciar el servicio.
    Útil para actualizaciones en caliente.
    """
    success = nlp_pipeline.reload_devices()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recargar dispositivos"
        )
    
    devices = nlp_pipeline.get_available_devices()
    return {
        "success": True,
        "message": "Dispositivos recargados exitosamente",
        "total": len(devices)
    }


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

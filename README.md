# NLP Service - Sistema Domótico Inteligente

Microservicio de Procesamiento de Lenguaje Natural (NLP) para interpretación de comandos de voz/texto en un sistema domótico.

## 📋 Descripción

Este microservicio recibe comandos en lenguaje natural (español) y devuelve la intención del usuario junto con el dispositivo identificado. Incluye detección de negaciones y un endpoint opcional para ejecutar acciones.

## ✨ Características Principales

- **Pipeline Híbrido**: Sistema de reglas (~1ms) + Ollama/Phi3 (~2-5s) como fallback
- **Detección de Negaciones**: Reconoce comandos negados ("no enciendas", "no abras")
- **Módulo NLP Modular**: Reglas separadas en archivos dedicados
- **Soporte Regional**: Variaciones del español (España, México, Argentina)
- **Aliases Extensos**: +200 sinónimos para dispositivos y habitaciones
- **Endpoint /execute**: Ejecución opcional de comandos en backend IoT

## 📚 Documentación

| Documento                                               | Descripción                                   |
| ------------------------------------------------------- | --------------------------------------------- |
| 📖 [Documentación NLP Completa](docs/NLP_MODULE.md)     | Arquitectura, componentes, pipeline, ejemplos |
| 🔧 [Especificación OpenAPI 3.0](docs/OPENAPI_SPEC.yaml) | Swagger/OpenAPI extendido                     |
| 🚀 [Guía Rápida](docs/QUICKSTART.md)                    | Inicio rápido con ejemplos                    |
| 📦 [README del Módulo NLP](nlp/README.md)               | Uso directo del módulo                        |

### Documentación Interactiva

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 🏗️ Estructura del Proyecto

```
nlp_ai_house/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuración del servicio
├── data/
│   └── devices.json             # Mapeo de dispositivos
├── database/
│   ├── __init__.py
│   └── connection.py            # Conexión SQLAlchemy
├── docs/                        # 📚 DOCUMENTACIÓN
│   ├── NLP_MODULE.md            # Documentación completa
│   ├── OPENAPI_SPEC.yaml        # Especificación OpenAPI 3.0
│   └── QUICKSTART.md            # Guía rápida
├── models/
│   ├── __init__.py
│   ├── schemas.py               # Esquemas Pydantic API
│   ├── database.py              # Modelos SQLAlchemy
│   └── device_schemas.py        # Esquemas CRUD dispositivos
├── nlp/                         # ⭐ MÓDULO NLP SEPARADO
│   ├── __init__.py              # Exportaciones del módulo
│   ├── README.md                # Documentación del módulo
│   ├── constants.py             # Enums y constantes
│   ├── intents.py               # Patrones de intención
│   ├── aliases.py               # Sinónimos dispositivos/habitaciones
│   ├── negations.py             # Detección de negaciones
│   ├── normalizer.py            # Normalización de texto
│   └── matchers.py              # Motores de coincidencia
├── routers/
│   ├── __init__.py
│   └── devices.py               # API REST de dispositivos
├── services/
│   ├── __init__.py
│   ├── nlp_pipeline.py          # Pipeline principal NLP
│   └── device_service.py        # Servicio de dispositivos
├── main.py                      # Servidor FastAPI
├── requirements.txt             # Dependencias
└── README.md
```

## 🚀 Instalación y Configuración

### Prerrequisitos

1. **Python 3.10+**
2. **Ollama** instalado (opcional pero recomendado)
3. **Modelo Phi3** descargado en Ollama

### Instalación Rápida

```bash
# Clonar o descargar el proyecto
cd nlp_ai_house

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

El servicio estará disponible en: `http://localhost:8001`

### Configurar Ollama (Opcional)

```bash
# Instalar Ollama
winget install Ollama.Ollama

# Descargar modelo Phi3 (2.2GB)
ollama pull phi3

# Verificar
ollama list
```

## 🔌 Endpoints

### Health Check

```http
GET /health
```

### Interpretar Comando (Principal)

```http
POST /interpret
Content-Type: application/json

{
  "text": "enciende la luz del comedor"
}
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "intent": "turn_on",
    "device": "luz_comedor",
    "negated": false
  },
  "original_text": "enciende la luz del comedor",
  "confidence_note": null
}
```

### Interpretar con Negación

```http
POST /interpret
Content-Type: application/json

{
  "text": "no enciendas la luz"
}
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "intent": "turn_on",
    "device": "luz_sala",
    "negated": true
  },
  "original_text": "no enciendas la luz",
  "confidence_note": null
}
```

### Ejecutar Comando (Opcional)

```http
POST /execute
Content-Type: application/json

{
  "text": "enciende la luz del comedor"
}
```

**Respuesta:**

```json
{
  "success": true,
  "interpretation": {
    "intent": "turn_on",
    "device": "luz_comedor",
    "negated": false
  },
  "execution": {
    "executed": true,
    "endpoint_called": "http://iot-backend/api/devices/luz_comedor/on",
    "status_code": 200
  },
  "original_text": "enciende la luz del comedor"
}
```

### Listar Dispositivos

```http
GET /devices
GET /devices/{device_key}
POST /devices/reload
```

## 🎯 Intenciones Soportadas

| Intent     | Descripción       | Palabras clave                             |
| ---------- | ----------------- | ------------------------------------------ |
| `turn_on`  | Encender/activar  | enciende, prende, activa, ilumina, conecta |
| `turn_off` | Apagar/desactivar | apaga, desactiva, desconecta, corta        |
| `open`     | Abrir             | abre, levanta, sube, descorre              |
| `close`    | Cerrar            | cierra, baja, corre, bloquea               |
| `status`   | Consultar estado  | estado, cómo está, revisar, verificar      |
| `toggle`   | Alternar          | alterna, cambia, invierte                  |
| `unknown`  | No reconocido     | -                                          |

## 🚫 Detección de Negaciones

El sistema detecta múltiples formas de negación en español:

| Tipo              | Ejemplo                 | Resultado     |
| ----------------- | ----------------------- | ------------- |
| **Directa**       | "no enciendas la luz"   | negated: true |
| **Con pronombre** | "no la enciendas"       | negated: true |
| **Compuesta**     | "no quiero que se abra" | negated: true |
| **Prohibitiva**   | "deja de encender"      | negated: true |
| **Implícita**     | "mejor no abras"        | negated: true |

### Respuesta para Comandos Negados

Cuando `negated: true`, el endpoint `/execute` NO ejecuta la acción:

```json
{
  "execution": {
    "executed": false,
    "reason": "Comando negado - no se ejecuta la acción",
    "message": "Entendido, NO se ejecutará turn_on en luz_sala"
  }
}
```

## 📦 Módulo NLP

### Estructura Modular

El módulo `nlp/` contiene todas las reglas separadas:

```python
from nlp import (
    # Constantes
    NLPConstants, IntentType, DeviceType,
    # Patrones
    IntentDefinitions, ContextPatterns,
    # Aliases
    DeviceAliases, RoomAliases, ActionAliases,
    # Negaciones
    NegationDetector, NegationResult,
    # Normalización
    TextNormalizer, SpanishTextPreprocessor,
    # Matchers
    IntentMatcher, DeviceMatcher, EntityExtractor,
)
```

### Uso Independiente

```python
from nlp import IntentMatcher, NegationDetector

# Detectar intención
matcher = IntentMatcher()
result = matcher.match("enciende la luz")
print(result.intent)  # "turn_on"
print(result.confidence)  # 0.85

# Detectar negación
detector = NegationDetector()
negation = detector.detect("no enciendas la luz")
print(negation.is_negated)  # True
print(negation.negation_type)  # "direct"
```

## 🧪 Ejemplos de Uso

### Desde curl

```bash
# Encender luz
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "enciende la luz del comedor"}'

# Comando negado
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "no enciendas la luz"}'

# Ejecutar comando
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{"text": "apaga el ventilador de la sala"}'
```

### Desde Python

```python
import httpx

async def interpret(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/interpret",
            json={"text": text}
        )
        return response.json()

# Uso
result = await interpret("enciende la luz del comedor")
if result["success"]:
    intent = result["data"]["intent"]
    device = result["data"]["device"]
    negated = result["data"]["negated"]

    if not negated and intent != "unknown" and device:
        # Ejecutar acción
        print(f"Ejecutar: {intent} en {device}")
```

## 🔧 Configuración

### Variables de Entorno

| Variable          | Descripción         | Valor por defecto                |
| ----------------- | ------------------- | -------------------------------- |
| `APP_NAME`        | Nombre del servicio | NLP Service - Smart Home         |
| `DEBUG`           | Modo debug          | True                             |
| `PORT`            | Puerto del servidor | 8001                             |
| `OLLAMA_BASE_URL` | URL de Ollama       | http://localhost:11434           |
| `OLLAMA_MODEL`    | Modelo a usar       | phi3                             |
| `DATABASE_URL`    | URL base de datos   | sqlite:///./nlp_service.db       |
| `IOT_BACKEND_URL` | URL backend IoT     | (vacío = /execute deshabilitado) |

## 📊 Arquitectura

```
┌──────────────────────────────────────────────────────────┐
│                     CLIENTE                               │
│              (Voz/Texto/App)                             │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│                NLP SERVICE (FastAPI)                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                NLP PIPELINE                          │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │ │
│  │  │Negation │→ │ Intent  │→ │ Device  │              │ │
│  │  │Detector │  │ Matcher │  │ Matcher │              │ │
│  │  └─────────┘  └─────────┘  └─────────┘              │ │
│  │       ↓            ↓            ↓                    │ │
│  │  ┌─────────────────────────────────────┐            │ │
│  │  │  Si confianza < 0.8 → Ollama/Phi3   │            │ │
│  │  └─────────────────────────────────────┘            │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │   RESPUESTA     │
            │ {intent, device,│
            │  negated}       │
            └─────────────────┘
```

## 📝 Licencia

Proyecto personal - Sistema domótico inteligente.

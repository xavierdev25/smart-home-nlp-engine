# 📚 Documentación del Módulo NLP

## Índice

1. [Descripción General](#1-descripción-general)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Pipeline de Procesamiento](#3-pipeline-de-procesamiento)
4. [Componentes del Módulo NLP](#4-componentes-del-módulo-nlp)
5. [API Reference](#5-api-reference)
6. [Ejemplos de Uso](#6-ejemplos-de-uso)
7. [Buenas Prácticas](#7-buenas-prácticas)
8. [Limitaciones Actuales](#8-limitaciones-actuales)
9. [Recomendaciones de Mejora](#9-recomendaciones-de-mejora)

---

## 1. Descripción General

### 1.1 Propósito

El módulo NLP (Natural Language Processing) es el núcleo de interpretación de comandos del sistema domótico inteligente. Su función principal es **transformar comandos en lenguaje natural (español) en estructuras de datos procesables** que identifican:

- **Intent (Intención)**: La acción que el usuario desea realizar
- **Device (Dispositivo)**: El dispositivo IoT objetivo
- **Negation (Negación)**: Si el comando está negado

### 1.2 Filosofía de Diseño

```
"Interpretar, no ejecutar"
```

El microservicio sigue el principio de **responsabilidad única**:

- ✅ Interpreta comandos de voz/texto
- ✅ Identifica intenciones y dispositivos
- ✅ Detecta negaciones y contexto
- ❌ NO ejecuta acciones directamente (excepto `/execute` opcional)
- ❌ NO mantiene estado de dispositivos

### 1.3 Características Principales

| Característica              | Descripción                                       |
| --------------------------- | ------------------------------------------------- |
| **Pipeline Híbrido**        | Reglas (~1ms) + LLM fallback (~2-5s)              |
| **Multiregional**           | Soporte para español de España, México, Argentina |
| **Detección de Negaciones** | 5 tipos de negaciones soportadas                  |
| **Extensible**              | Arquitectura modular para agregar nuevas reglas   |
| **Tolerante a Fallos**      | Funciona sin Ollama usando fallback de reglas     |

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTE                                      │
│                    (App Móvil / Asistente de Voz / Web)                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼ HTTP POST /interpret
┌─────────────────────────────────────────────────────────────────────────┐
│                         NLP SERVICE (FastAPI)                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        NLP PIPELINE                                │  │
│  │                                                                    │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │  │
│  │  │    TEXT      │    │   NEGATION   │    │    INTENT    │        │  │
│  │  │ NORMALIZER   │───▶│   DETECTOR   │───▶│   MATCHER    │        │  │
│  │  └──────────────┘    └──────────────┘    └──────────────┘        │  │
│  │         │                   │                   │                  │  │
│  │         │                   │                   ▼                  │  │
│  │         │                   │            ┌──────────────┐         │  │
│  │         │                   │            │    DEVICE    │         │  │
│  │         │                   │            │   MATCHER    │         │  │
│  │         │                   │            └──────────────┘         │  │
│  │         │                   │                   │                  │  │
│  │         │                   ▼                   ▼                  │  │
│  │         │         ┌─────────────────────────────────────┐         │  │
│  │         │         │     CONFIDENCE CHECK                │         │  │
│  │         │         │  (intent >= 0.8 && device >= 0.7?)  │         │  │
│  │         │         └─────────────────────────────────────┘         │  │
│  │         │                   │                                      │  │
│  │         │         ┌────────┴────────┐                             │  │
│  │         │         │                 │                             │  │
│  │         │        YES               NO                             │  │
│  │         │         │                 │                             │  │
│  │         │         ▼                 ▼                             │  │
│  │         │  ┌───────────┐    ┌───────────────┐                    │  │
│  │         │  │  RETURN   │    │  OLLAMA/PHI3  │                    │  │
│  │         │  │  RESULT   │    │   FALLBACK    │                    │  │
│  │         │  └───────────┘    └───────────────┘                    │  │
│  │         │                          │                              │  │
│  │         │                          ▼                              │  │
│  │         │                   ┌───────────┐                         │  │
│  │         │                   │  RETURN   │                         │  │
│  │         │                   │  RESULT   │                         │  │
│  │         │                   └───────────┘                         │  │
│  └─────────│─────────────────────────────────────────────────────────┘  │
│            │                                                             │
└────────────│─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           RESPUESTA JSON                                 │
│  {                                                                       │
│    "intent": "turn_on",                                                  │
│    "device": "luz_comedor",                                              │
│    "negated": false                                                      │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

| Componente    | Tecnología          | Versión | Propósito                      |
| ------------- | ------------------- | ------- | ------------------------------ |
| Framework Web | FastAPI             | 0.109+  | API REST async                 |
| Validación    | Pydantic            | 2.5+    | Schemas de datos               |
| LLM Local     | Ollama + Phi3       | Latest  | Interpretación avanzada        |
| Base de Datos | SQLAlchemy + SQLite | 2.0+    | Almacenamiento de dispositivos |
| HTTP Client   | HTTPX               | 0.26+   | Comunicación async             |
| Python        | CPython             | 3.10+   | Runtime                        |

### 2.3 Estructura de Archivos

```
nlp_ai_house/
├── nlp/                          # 🧠 MÓDULO NLP PRINCIPAL
│   ├── __init__.py               # Exportaciones públicas
│   ├── constants.py              # Enums, constantes, umbrales
│   ├── intents.py                # Patrones regex de intenciones
│   ├── aliases.py                # Sinónimos dispositivos/habitaciones
│   ├── negations.py              # Detector de negaciones
│   ├── normalizer.py             # Normalización de texto
│   └── matchers.py               # Motores de coincidencia
│
├── services/
│   └── nlp_pipeline.py           # Pipeline principal
│
├── models/
│   └── schemas.py                # Schemas Pydantic
│
├── config/
│   └── settings.py               # Configuración
│
├── data/
│   └── devices.json              # Dispositivos configurados
│
└── main.py                       # Servidor FastAPI
```

---

## 3. Pipeline de Procesamiento

### 3.1 Flujo de Datos

```
INPUT                    PROCESSING                         OUTPUT
─────                    ──────────                         ──────

"no enciendas      ┌─────────────────────┐
 la luz del   ────▶│  1. NORMALIZACIÓN   │
 comedor"          │  • Minúsculas       │
                   │  • Sin acentos      │
                   │  • Sin puntuación   │
                   └─────────┬───────────┘
                             │
                   "no enciendas la luz del comedor"
                             │
                             ▼
                   ┌─────────────────────┐
                   │  2. DETECCIÓN DE    │
                   │     NEGACIÓN        │
                   │  • Buscar "no"      │
                   │  • Identificar tipo │
                   └─────────┬───────────┘
                             │
                   negated=True, type="direct"
                             │
                             ▼
                   ┌─────────────────────┐
                   │  3. REMOVER NEGACIÓN│
                   │  "no enciendas..." │
                   │   → "enciendas..."  │
                   └─────────┬───────────┘
                             │
                   "enciendas la luz del comedor"
                             │
                             ▼
                   ┌─────────────────────┐
                   │  4. INTENT MATCHING │
                   │  • Buscar patrones  │
                   │  • Calcular conf.   │
                   └─────────┬───────────┘
                             │
                   intent="turn_on", confidence=0.86
                             │
                             ▼
                   ┌─────────────────────┐
                   │  5. DEVICE MATCHING │
                   │  • Buscar en índice │
                   │  • Matching parcial │
                   └─────────┬───────────┘
                             │
                   device="luz_comedor", confidence=0.95
                             │
                             ▼
                   ┌─────────────────────┐
                   │  6. VALIDACIÓN      │           ┌───────────────┐
                   │  • Confianza OK?    │──────────▶│   RESPUESTA   │
                   │  • Dispositivo OK?  │           │               │
                   └─────────────────────┘           │ intent:turn_on│
                                                     │ device:luz_..│
                                                     │ negated:true  │
                                                     └───────────────┘
```

### 3.2 Etapas del Pipeline

#### Etapa 1: Normalización de Texto

```python
from nlp import TextNormalizer

normalizer = TextNormalizer()

# Entrada
text = "¡Enciende la LUZ del COMEDOR, por favor!"

# Salida
normalized = normalizer.normalize(text)
# → "enciende la luz del comedor por favor"
```

**Operaciones realizadas:**

- Conversión a minúsculas
- Eliminación de acentos (á→a, é→e, etc.)
- Remoción de signos de puntuación
- Normalización de espacios múltiples
- Expansión de formas coloquiales (xfa → por favor)

#### Etapa 2: Detección de Negaciones

```python
from nlp import NegationDetector

detector = NegationDetector()

# Ejemplos
result = detector.detect("no enciendas la luz")
# → NegationResult(is_negated=True, negation_type="direct", ...)

result = detector.detect("prefiero que no abras")
# → NegationResult(is_negated=True, negation_type="compound", ...)
```

**Tipos de negaciones detectadas:**

| Tipo          | Ejemplo                 | Confianza |
| ------------- | ----------------------- | --------- |
| `direct`      | "no enciendas"          | 0.95      |
| `pronoun`     | "no la enciendas"       | 0.90      |
| `compound`    | "no quiero que se abra" | 0.85      |
| `prohibitive` | "deja de encender"      | 0.85      |
| `implicit`    | "mejor no"              | 0.75      |

#### Etapa 3: Matching de Intención

```python
from nlp import IntentMatcher

matcher = IntentMatcher()

result = matcher.match("enciende la luz")
# → IntentMatch(intent="turn_on", confidence=0.86, matched_pattern="...", ...)
```

**Intenciones soportadas:**

| Intent     | Palabras clave principales                 |
| ---------- | ------------------------------------------ |
| `turn_on`  | enciende, prende, activa, ilumina, conecta |
| `turn_off` | apaga, desactiva, desconecta, corta        |
| `open`     | abre, levanta, sube, descorre              |
| `close`    | cierra, baja, corre, bloquea               |
| `status`   | estado, cómo está, verifica, revisa        |
| `toggle`   | alterna, cambia, invierte                  |

#### Etapa 4: Matching de Dispositivo

```python
from nlp import DeviceMatcher

# Inicializar con lista de dispositivos
devices = [
    {"device_key": "luz_comedor", "name": "Luz del comedor", "aliases": ["luz comedor", "lampara comedor"]}
]
matcher = DeviceMatcher(devices)

result = matcher.match("luz del comedor")
# → DeviceMatch(device_key="luz_comedor", confidence=0.95, ...)
```

**Estrategias de búsqueda:**

1. **Búsqueda exacta por alias** (confianza: 0.95)
2. **Búsqueda por n-gramas** (confianza: 0.85)
3. **Búsqueda parcial** (confianza: 0.70)

#### Etapa 5: Validación y Respuesta

Si la confianza combinada es alta (intent ≥ 0.8 y device ≥ 0.7), se retorna el resultado directamente.

Si la confianza es baja, se utiliza **Ollama/Phi3 como fallback**.

---

## 4. Componentes del Módulo NLP

### 4.1 constants.py

Define enumeraciones y constantes del sistema.

```python
from nlp import IntentType, DeviceType, NLPConstants

# Tipos de intención
IntentType.TURN_ON      # "turn_on"
IntentType.TURN_OFF     # "turn_off"
IntentType.OPEN         # "open"
IntentType.CLOSE        # "close"
IntentType.STATUS       # "status"
IntentType.TOGGLE       # "toggle"
IntentType.UNKNOWN      # "unknown"

# Umbrales de confianza
NLPConstants.HIGH_CONFIDENCE_THRESHOLD    # 0.85
NLPConstants.MEDIUM_CONFIDENCE_THRESHOLD  # 0.70
NLPConstants.LOW_CONFIDENCE_THRESHOLD     # 0.50

# Stopwords
NLPConstants.STOPWORDS  # ["el", "la", "los", "de", ...]
```

### 4.2 intents.py

Define patrones regex para detectar intenciones.

```python
from nlp import IntentDefinitions

# Obtener todos los patrones
patterns = IntentDefinitions.get_all_patterns()
# {
#     "turn_on": [r"\b(enciende|encender|prende|...)\b", ...],
#     "turn_off": [...],
#     ...
# }

# Obtener patrones compilados (mejor rendimiento)
compiled = IntentDefinitions.get_compiled_patterns()
```

**Patrones incluidos por intención:**

- **turn_on**: 15+ patrones (enciende, prende, activa, ilumina, conecta, dale luz, etc.)
- **turn_off**: 12+ patrones (apaga, desactiva, corta, desconecta, etc.)
- **open**: 10+ patrones (abre, levanta, sube, descorre, etc.)
- **close**: 10+ patrones (cierra, baja, corre, bloquea, etc.)
- **status**: 12+ patrones (estado, cómo está, verifica, consulta, etc.)

### 4.3 aliases.py

Define sinónimos para dispositivos, habitaciones y acciones.

```python
from nlp import DeviceAliases, RoomAliases, ActionAliases

# Aliases de dispositivos
DeviceAliases.LIGHTS
# {
#     "luz": ["lámpara", "foco", "bombilla", "velador", ...],
#     "led": ["tira led", "tiras led", ...],
#     ...
# }

# Aliases de habitaciones
RoomAliases.ROOMS
# {
#     "sala": ["living", "salón", "sala de estar", ...],
#     "cocina": ["kitchen", "cocineta", ...],
#     "dormitorio": ["habitación", "cuarto", "recámara", "pieza", ...],
#     ...
# }

# Lookup inverso: alias → canonical
device_lookup = DeviceAliases.build_reverse_lookup()
# {"lampara": "luz", "foco": "luz", "bombilla": "luz", ...}
```

### 4.4 negations.py

Detector de negaciones con múltiples estrategias.

```python
from nlp import NegationDetector, NegationResult

detector = NegationDetector()

# Detectar negación
result: NegationResult = detector.detect("no enciendas la luz")
result.is_negated      # True
result.negation_type   # "direct"
result.original_intent # "turn_on"
result.negation_word   # "no"
result.confidence      # 0.95

# Remover negación del texto
clean_text = detector.remove_negation("no enciendas la luz")
# → "enciendas la luz"

# Obtener respuesta para comando negado
response = detector.get_negated_response("turn_on")
# → "Entendido, NO encenderé el dispositivo."
```

### 4.5 normalizer.py

Procesamiento y normalización de texto en español.

```python
from nlp import TextNormalizer, SpanishTextPreprocessor

normalizer = TextNormalizer(
    remove_accents=True,      # Eliminar acentos
    fix_typos=True,           # Corregir typos comunes
    expand_colloquial=True,   # Expandir "xfa" → "por favor"
    preserve_numbers=True     # Preservar números
)

# Normalización básica
text = normalizer.normalize("¡Enciéndeme la LUZ, porfa!")
# → "enciendeme la luz por favor"

# Tokenización
tokens = normalizer.tokenize("enciende la luz")
# → ["enciende", "la", "luz"]

# Extracción de números
numbers = normalizer.extract_numbers("pon la luz al 50%")
# → ["50%"]

# Preprocesador completo
preprocessor = SpanishTextPreprocessor()
analysis = preprocessor.preprocess("¿Está encendida la luz?")
# {
#     "original": "¿Está encendida la luz?",
#     "normalized": "esta encendida la luz",
#     "tokens": ["esta", "encendida", "la", "luz"],
#     "numbers": [],
#     "word_count": 4,
#     "char_count": 24
# }

# Detección de tipo de oración
preprocessor.is_question("¿cómo está la luz?")  # True
preprocessor.is_command("enciende la luz")       # True
preprocessor.get_sentence_type("la luz está encendida")  # "statement"
```

### 4.6 matchers.py

Motores de coincidencia para intenciones y dispositivos.

```python
from nlp import IntentMatcher, DeviceMatcher, EntityExtractor

# === Intent Matcher ===
intent_matcher = IntentMatcher()

result = intent_matcher.match("enciende la luz del comedor")
result.intent           # "turn_on"
result.confidence       # 0.86
result.matched_pattern  # r"\b(enciende|encender|...)\b"
result.matched_text     # "enciende"

# Obtener TODAS las intenciones que matchean
all_matches = intent_matcher.get_all_matches("enciende y apaga la luz")
# [IntentMatch(intent="turn_on", ...), IntentMatch(intent="turn_off", ...)]


# === Device Matcher ===
devices = [
    {"device_key": "luz_comedor", "name": "Luz Comedor", "type": "light", "room": "comedor", "aliases": ["luz del comedor"]}
]
device_matcher = DeviceMatcher(devices)

result = device_matcher.match("enciende la luz del comedor")
result.device_key   # "luz_comedor"
result.device_type  # "light"
result.confidence   # 0.95
result.room         # "comedor"

# Detectar habitación
room = device_matcher.match_room("en la sala de estar")
# → "sala"


# === Entity Extractor (combina ambos) ===
extractor = EntityExtractor(devices)

result = extractor.extract("enciende la luz del comedor")
result.device          # DeviceMatch(device_key="luz_comedor", ...)
result.room            # "comedor"
result.raw_device_text # "luz del comedor"
result.raw_room_text   # "comedor"

# Buscar dispositivo por habitación y tipo
device = extractor.get_device_by_room("comedor", "light")
# → DeviceMatch(device_key="luz_comedor", ...)
```

---

## 5. API Reference

### 5.1 Endpoints NLP

#### POST /interpret

Interpreta un comando de lenguaje natural.

**Request:**

```http
POST /interpret HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
    "text": "enciende la luz del comedor"
}
```

**Response 200 OK:**

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

**Response con negación:**

```json
{
  "success": true,
  "data": {
    "intent": "turn_on",
    "device": "luz_comedor",
    "negated": true
  },
  "original_text": "no enciendas la luz del comedor",
  "confidence_note": null
}
```

**Response con baja confianza:**

```json
{
  "success": true,
  "data": {
    "intent": "unknown",
    "device": null,
    "negated": false
  },
  "original_text": "quiero pizza",
  "confidence_note": "No se pudo identificar una intención válida"
}
```

---

#### POST /execute

Interpreta y ejecuta un comando (opcional).

**Request:**

```http
POST /execute HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
    "text": "enciende la luz del comedor"
}
```

**Response 200 OK (ejecutado):**

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
    "status_code": 200,
    "response": { "status": "ok" }
  },
  "original_text": "enciende la luz del comedor",
  "confidence_note": null
}
```

**Response con comando negado:**

```json
{
  "success": true,
  "interpretation": {
    "intent": "turn_on",
    "device": "luz_comedor",
    "negated": true
  },
  "execution": {
    "executed": false,
    "reason": "Comando negado - no se ejecuta la acción",
    "message": "Entendido, NO se ejecutará turn_on en luz_comedor"
  },
  "original_text": "no enciendas la luz del comedor"
}
```

---

#### GET /health

Verifica el estado del servicio.

**Response:**

```json
{
  "status": "healthy",
  "service": "NLP Service - Smart Home",
  "version": "1.0.0",
  "ollama_status": "connected"
}
```

---

### 5.2 Endpoints de Dispositivos

#### GET /devices

Lista todos los dispositivos configurados.

**Response:**

```json
{
    "success": true,
    "total": 22,
    "devices": {
        "luz_sala": {
            "name": "Luz de la Sala",
            "type": "light",
            "room": "sala",
            "aliases": ["luz sala", "lámpara sala", "luz del living"]
        },
        ...
    }
}
```

---

#### GET /devices/{device_key}

Obtiene información de un dispositivo específico.

**Response:**

```json
{
  "success": true,
  "device_key": "luz_comedor",
  "device": {
    "name": "Luz del Comedor",
    "type": "light",
    "room": "comedor",
    "aliases": ["luz comedor", "lámpara comedor"]
  }
}
```

---

#### POST /devices/reload

Recarga la configuración de dispositivos.

**Response:**

```json
{
  "success": true,
  "message": "Dispositivos recargados exitosamente",
  "total": 22
}
```

---

## 6. Ejemplos de Uso

### 6.1 Desde cURL

```bash
# Interpretar comando básico
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "enciende la luz del comedor"}'

# Comando con negación
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "no enciendas la luz"}'

# Ejecutar comando
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{"text": "apaga el ventilador de la sala"}'

# Health check
curl "http://localhost:8001/health"

# Listar dispositivos
curl "http://localhost:8001/devices"
```

### 6.2 Desde Python

```python
import httpx
import asyncio

NLP_URL = "http://localhost:8001"

async def interpret(text: str) -> dict:
    """Interpreta un comando de texto."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NLP_URL}/interpret",
            json={"text": text}
        )
        return response.json()

async def execute(text: str) -> dict:
    """Interpreta y ejecuta un comando."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NLP_URL}/execute",
            json={"text": text}
        )
        return response.json()

# Uso
async def main():
    # Interpretar
    result = await interpret("enciende la luz del comedor")
    print(f"Intent: {result['data']['intent']}")
    print(f"Device: {result['data']['device']}")
    print(f"Negated: {result['data']['negated']}")

    # Verificar si es comando válido
    if result['data']['intent'] != 'unknown' and result['data']['device']:
        if not result['data']['negated']:
            # Ejecutar
            exec_result = await execute("enciende la luz del comedor")
            print(f"Executed: {exec_result['execution']['executed']}")

asyncio.run(main())
```

### 6.3 Desde JavaScript

```javascript
const NLP_URL = "http://localhost:8001";

async function interpret(text) {
  const response = await fetch(`${NLP_URL}/interpret`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return response.json();
}

// Uso
interpret("enciende la luz del comedor").then((result) => {
  console.log("Intent:", result.data.intent);
  console.log("Device:", result.data.device);
  console.log("Negated:", result.data.negated);

  if (!result.data.negated && result.data.device) {
    // Procesar comando...
  }
});
```

### 6.4 Usando el Módulo NLP Directamente

```python
from nlp import (
    TextNormalizer,
    NegationDetector,
    IntentMatcher,
    DeviceMatcher,
)

# Inicializar componentes
normalizer = TextNormalizer()
negation_detector = NegationDetector()
intent_matcher = IntentMatcher()

devices = [
    {"device_key": "luz_comedor", "name": "Luz Comedor", "type": "light",
     "room": "comedor", "aliases": ["luz del comedor"]}
]
device_matcher = DeviceMatcher(devices)

def process_command(text: str) -> dict:
    """Procesa un comando de texto manualmente."""

    # 1. Detectar negación
    negation = negation_detector.detect(text)

    # 2. Si hay negación, procesar texto limpio
    if negation.is_negated:
        clean_text = negation_detector.remove_negation(text)
    else:
        clean_text = text

    # 3. Detectar intención
    intent_result = intent_matcher.match(clean_text)

    # 4. Detectar dispositivo
    device_result = device_matcher.match(clean_text)

    return {
        "intent": intent_result.intent,
        "device": device_result.device_key,
        "negated": negation.is_negated,
        "confidence": {
            "intent": intent_result.confidence,
            "device": device_result.confidence
        }
    }

# Uso
result = process_command("no enciendas la luz del comedor")
print(result)
# {
#     "intent": "turn_on",
#     "device": "luz_comedor",
#     "negated": True,
#     "confidence": {"intent": 0.86, "device": 0.95}
# }
```

---

## 7. Buenas Prácticas

### 7.1 Diseño de Comandos de Voz

✅ **Recomendado:**

```
"enciende la luz del comedor"
"apaga el ventilador de la sala"
"abre la puerta del garage"
```

❌ **Evitar:**

```
"luz"                    # Muy ambiguo
"hazlo"                  # Sin contexto
"enciende todo"          # Demasiado general (aún no soportado)
```

### 7.2 Configuración de Dispositivos

```json
{
  "device_key": "luz_comedor", // ✅ Usar snake_case
  "name": "Luz del Comedor", // ✅ Nombre descriptivo
  "type": "light", // ✅ Tipo estándar
  "room": "comedor", // ✅ Habitación normalizada
  "aliases": [
    "luz comedor", // ✅ Sin artículos
    "lámpara del comedor", // ✅ Con acentos
    "lampara comedor", // ✅ Sin acentos también
    "luz dining" // ✅ Variación bilingüe
  ]
}
```

### 7.3 Manejo de Errores

```python
result = await interpret(text)

# Siempre verificar success
if not result["success"]:
    logger.error(f"Error NLP: {result.get('error')}")
    return

# Verificar intent válido
if result["data"]["intent"] == "unknown":
    return "No entendí tu comando. ¿Puedes reformularlo?"

# Verificar dispositivo identificado
if not result["data"]["device"]:
    return "¿A qué dispositivo te refieres?"

# Verificar negación
if result["data"]["negated"]:
    return f"Entendido, NO ejecutaré la acción."
```

### 7.4 Optimización de Rendimiento

```python
# ✅ Reutilizar instancias (singleton)
from services.nlp_pipeline import nlp_pipeline  # Ya es singleton

# ✅ Usar async/await correctamente
result = await nlp_pipeline.interpret(text)

# ✅ Recargar dispositivos solo cuando sea necesario
nlp_pipeline.reload_devices()  # Solo si devices.json cambió

# ❌ Evitar crear instancias por cada request
# pipeline = NLPPipeline()  # NO hacer esto
```

---

## 8. Limitaciones Actuales

### 8.1 Limitaciones de Procesamiento

| Limitación                 | Descripción                                                          | Workaround                                 |
| -------------------------- | -------------------------------------------------------------------- | ------------------------------------------ |
| **Comandos compuestos**    | "enciende la luz y apaga el ventilador" no se divide automáticamente | Enviar comandos separados                  |
| **Contexto previo**        | No recuerda comandos anteriores                                      | Enviar comando completo cada vez           |
| **Múltiples dispositivos** | "enciende todas las luces" no soportado completamente                | Usar alias específico o endpoint por grupo |
| **Intensidad/Nivel**       | "enciende la luz al 50%" no extrae el porcentaje                     | Implementar extracción de niveles          |

### 8.2 Limitaciones de Idioma

| Limitación                  | Descripción                                          |
| --------------------------- | ---------------------------------------------------- |
| **Solo español**            | No soporta inglés u otros idiomas                    |
| **Regionalismos limitados** | Algunas expresiones regionales pueden no reconocerse |
| **Jerga/Slang**             | Expresiones muy coloquiales pueden fallar            |

### 8.3 Limitaciones Técnicas

| Limitación                         | Descripción                               |
| ---------------------------------- | ----------------------------------------- |
| **Ollama requerido para fallback** | Sin Ollama, solo funcionan reglas básicas |
| **Sin caché de resultados**        | Cada request procesa desde cero           |
| **Timeout de Ollama**              | Puede tardar 2-5s si se usa LLM           |

---

## 9. Recomendaciones de Mejora

### 9.1 Corto Plazo (Próximas versiones)

#### 1. Soporte para Comandos Compuestos

```python
# Entrada: "enciende la luz y apaga el ventilador"
# Salida: [
#     {"intent": "turn_on", "device": "luz_sala"},
#     {"intent": "turn_off", "device": "ventilador_sala"}
# ]
```

#### 2. Extracción de Niveles/Intensidad

```python
# Entrada: "pon la luz al 50%"
# Salida: {"intent": "set_level", "device": "luz_sala", "level": 50}
```

#### 3. Caché de Resultados

```python
# Implementar caché para comandos frecuentes
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_interpret(text_hash: str) -> dict:
    ...
```

### 9.2 Mediano Plazo

#### 1. Soporte Multi-idioma

```python
# Detectar idioma automáticamente
# Soportar inglés, portugués, español
```

#### 2. Contexto Conversacional

```python
# Usuario: "enciende la luz de la sala"
# Sistema: "Luz encendida"
# Usuario: "ahora apágala"  # ← Entender referencia
```

#### 3. Aprendizaje de Patrones

```python
# Guardar comandos exitosos para mejorar matching
# Entrenar modelo con datos propios
```

### 9.3 Largo Plazo

#### 1. Modelo NLP Propio

- Fine-tuning de modelo pequeño con datos domóticos
- Eliminar dependencia de Ollama

#### 2. Procesamiento de Voz Integrado

- Whisper para transcripción
- Pipeline end-to-end: audio → texto → interpretación

#### 3. Inferencia de Intención Contextual

- Considerar hora del día
- Considerar ubicación del usuario
- Considerar patrones de uso

---

## 📊 Métricas de Rendimiento

### Tiempos de Respuesta Esperados

| Escenario                         | Tiempo  | Método       |
| --------------------------------- | ------- | ------------ |
| Match por reglas (alta confianza) | ~1-5ms  | Solo CPU     |
| Match por reglas + validación     | ~5-10ms | Solo CPU     |
| Fallback a Ollama/Phi3            | ~2-5s   | GPU RTX 2050 |
| Fallback a Ollama/Phi3            | ~5-15s  | Solo CPU     |

### Precisión Estimada

| Tipo de Comando                          | Precisión         |
| ---------------------------------------- | ----------------- |
| Comandos directos ("enciende luz sala")  | ~95%              |
| Comandos con alias ("prende la lámpara") | ~90%              |
| Comandos con negación ("no enciendas")   | ~92%              |
| Comandos ambiguos                        | ~70% (usa Ollama) |

---

## 📝 Changelog

### v1.0.0 (2025-11-25)

- ✅ Pipeline híbrido reglas + Ollama
- ✅ Detección de negaciones
- ✅ Módulo NLP modular
- ✅ Endpoint /execute opcional
- ✅ Documentación completa

---

_Documentación generada para NLP Service - Smart Home v1.0.0_

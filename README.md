# 🏠 Smart Home NLP Engine

Microservicio de Procesamiento de Lenguaje Natural (NLP) con control por voz para sistemas domóticos inteligentes.

## 📋 Descripción

Este microservicio recibe comandos en lenguaje natural (**español e inglés**) y devuelve la intención del usuario junto con el dispositivo identificado. Incluye:

- **NLP Pipeline**: Interpretación de comandos con reglas + LLM fallback
- **Control por Voz**: Speech-to-Text (STT) y Text-to-Speech (TTS)
- **Detección de Negaciones**: Reconoce comandos negados
- **Bilingüe**: Soporte completo para español e inglés
- **API REST**: Endpoints para integración con cualquier sistema

---

## ✨ Características

| Característica         | Descripción                                                    |
| ---------------------- | -------------------------------------------------------------- |
| **Pipeline Híbrido**   | Reglas regex (~2ms) + Ollama/Phi3 (~2-5s) como fallback        |
| **🎤 Control por Voz** | STT (Google) + TTS (gTTS) integrados                           |
| **🌐 Bilingüe**        | Español e Inglés (comandos, respuestas, TTS)                   |
| **Negaciones**         | 5 tipos: directa, pronombre, compuesta, prohibitiva, implícita |
| **Multiregional**      | ES: España, México, Argentina / EN: US, UK                     |
| **+200 Aliases**       | Sinónimos para dispositivos y habitaciones                     |
| **API Documentada**    | Swagger UI + ReDoc + OpenAPI 3.0                               |

---

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/xavierdev25/smart-home-nlp-engine.git
cd smart-home-nlp-engine

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

**Servidor disponible en:** http://localhost:8001

---

## 🎮 Ejecución Interactiva (Recomendado)

El archivo `run.py` integra todas las funcionalidades en un solo lugar:

```bash
# Menú interactivo completo
python run.py

# Modo texto directo (escribe comandos, respuestas por voz)
python run.py --text

# Modo voz directo (habla comandos, respuestas por voz)
python run.py --voice

# Servidor API
python run.py --server

# Cambiar idioma inicial
python run.py --text --lang en   # Inglés
python run.py --voice --lang es  # Español
```

### Menú Interactivo

```
╔══════════════════════════════════════════════════════════════╗
║   🏠 Smart Home NLP Engine                                   ║
║   Bilingual Voice Controller (ES/EN)                         ║
╚══════════════════════════════════════════════════════════════╝

  1) 📝 Modo Texto     - Escribe comandos, respuestas por voz
  2) 🎤 Modo Voz       - Habla comandos, respuestas por voz
  3) 🔄 Modo Completo  - Texto + Voz simultáneo
  4) 🌐 Servidor API   - Iniciar FastAPI en puerto 8001
  5) ⚙️  Configuración  - Cambiar idioma y voz
  0) 🚪 Salir
```

### Comandos durante la ejecución

| Comando          | Descripción                             |
| ---------------- | --------------------------------------- |
| `lang es`        | Cambiar a español                       |
| `lang en`        | Cambiar a inglés                        |
| `salir` / `exit` | Volver al menú                          |
| `v` / `voice`    | (Modo completo) Activar entrada por voz |

---

### Dependencias de Voz (Opcional)

```bash
pip install SpeechRecognition PyAudio gTTS pygame

# Windows - si PyAudio falla:
pip install pipwin && pipwin install pyaudio
```

### Ollama (Opcional - LLM Fallback)

```bash
# Instalar Ollama
winget install Ollama.Ollama

# Descargar modelo
ollama pull phi3
```

---

## 🏗️ Estructura del Proyecto

```
smart-home-nlp-engine/
├── run.py                   # 🎮 Ejecutor interactivo (texto + voz + API)
├── main.py                  # 🚀 Servidor FastAPI
├── requirements.txt         # Dependencias
├── config/
│   └── settings.py          # Configuración
├── data/
│   └── devices.json         # Dispositivos configurados
├── database/
│   └── connection.py        # SQLAlchemy
├── models/
│   ├── schemas.py           # Pydantic API
│   ├── database.py          # Modelos DB
│   └── device_schemas.py    # CRUD schemas
├── nlp/                     # ⭐ Módulo NLP
│   ├── constants.py         # Enums (IntentType, DeviceType)
│   ├── intents.py           # 50+ patrones regex
│   ├── aliases.py           # +200 sinónimos
│   ├── negations.py         # Detector de negaciones
│   ├── normalizer.py        # Normalización texto
│   └── matchers.py          # IntentMatcher, DeviceMatcher
├── voice/                   # 🎤 Módulo de Voz
│   ├── speech_to_text.py    # STT (Google, Whisper, Vosk)
│   ├── text_to_speech.py    # TTS (gTTS, Edge, pyttsx3)
│   └── voice_assistant.py   # Asistente integrado
├── routers/
│   ├── devices.py           # API dispositivos
│   └── voice.py             # API voz
├── services/
│   ├── nlp_pipeline.py      # Pipeline principal
│   └── device_service.py    # Servicio dispositivos
├── examples/
│   ├── integration_example.py
│   └── voice_demo.py        # Demo control por voz
└── docs/
    └── OPENAPI_SPEC.yaml    # Especificación OpenAPI 3.0
```

---

## 🔌 API Endpoints

### Documentación Interactiva

| URL                                | Descripción  |
| ---------------------------------- | ------------ |
| http://localhost:8001/docs         | Swagger UI   |
| http://localhost:8001/redoc        | ReDoc        |
| http://localhost:8001/openapi.json | OpenAPI JSON |

### Health Check

```bash
curl http://localhost:8001/health
```

### Interpretar Comando (Principal)

```bash
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "enciende la luz del comedor"}'
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
  "original_text": "enciende la luz del comedor"
}
```

### Comando con Negación

```bash
curl -X POST "http://localhost:8001/interpret" \
  -H "Content-Type: application/json" \
  -d '{"text": "no enciendas la luz"}'
```

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "intent": "turn_on",
    "device": "luz_sala",
    "negated": true
  }
}
```

### Ejecutar Comando

```bash
curl -X POST "http://localhost:8001/execute" \
  -H "Content-Type: application/json" \
  -d '{"text": "apaga el ventilador"}'
```

### Dispositivos

```bash
GET  /devices              # Listar todos
GET  /devices/{device_key} # Obtener uno
POST /devices/reload       # Recargar configuración
```

---

## 🎤 Control por Voz

### API de Voz

| Endpoint                      | Método | Descripción                |
| ----------------------------- | ------ | -------------------------- |
| `/voice/interpret`            | POST   | Audio WAV → JSON resultado |
| `/voice/interpret-with-audio` | POST   | Audio WAV → MP3 respuesta  |
| `/voice/synthesize`           | POST   | Texto → MP3                |
| `/voice/transcribe`           | POST   | Audio WAV → Texto          |
| `/voice/voices`               | GET    | Listar voces disponibles   |
| `/voice/status`               | GET    | Estado del módulo          |

### Interpretar Audio

```bash
curl -X POST "http://localhost:8001/voice/interpret" \
  -F "audio=@comando.wav"
```

**Respuesta:**

```json
{
  "success": true,
  "original_text": "enciende la luz",
  "intent": "turn_on",
  "device": "luz_sala",
  "negated": false,
  "response_text": "Listo, luz sala encendido"
}
```

### Sintetizar Texto a Voz

```bash
# Español (default)
curl -X POST "http://localhost:8001/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Luz encendida", "language": "es"}' \
  --output respuesta.mp3

# Inglés
curl -X POST "http://localhost:8001/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Light turned on", "language": "en"}' \
  --output response.mp3
```

### Demo Interactivo

```bash
# Control por voz completo
python examples/voice_demo.py

# Solo probar TTS
python examples/voice_demo.py --mode test_tts

# Solo probar STT
python examples/voice_demo.py --mode test_stt
```

### Motores Disponibles

**STT (Speech-to-Text):**
| Motor | Tipo | Calidad |
|-------|------|---------|
| `google` | Online | ⭐⭐⭐⭐ (DEFAULT) |
| `whisper` | Offline | ⭐⭐⭐⭐⭐ |
| `vosk` | Offline | ⭐⭐⭐ |

**TTS (Text-to-Speech):**
| Motor | Tipo | Calidad |
|-------|------|---------|
| `gtts` | Online | ⭐⭐⭐⭐ (DEFAULT) |
| `edge_tts` | Online | ⭐⭐⭐⭐⭐ |
| `pyttsx3` | Offline | ⭐⭐ |

---

## 🎯 Intenciones Soportadas

| Intent     | Descripción   | Español                           | English                       |
| ---------- | ------------- | --------------------------------- | ----------------------------- |
| `turn_on`  | Encender      | enciende, prende, activa, ilumina | turn on, switch on, enable    |
| `turn_off` | Apagar        | apaga, desactiva, desconecta      | turn off, switch off, disable |
| `open`     | Abrir         | abre, levanta, sube, descorre     | open, unlock, raise           |
| `close`    | Cerrar        | cierra, baja, corre, bloquea      | close, shut, lock, lower      |
| `status`   | Estado        | ¿cómo está?, revisa, verifica     | status, check, how is         |
| `toggle`   | Alternar      | alterna, cambia, invierte         | toggle, switch, flip          |
| `unknown`  | No reconocido | -                                 | -                             |

---

## 🚫 Detección de Negaciones

| Tipo            | Español                 | English                   | Resultado       |
| --------------- | ----------------------- | ------------------------- | --------------- |
| **Directa**     | "no enciendas la luz"   | "don't turn on the light" | `negated: true` |
| **Pronombre**   | "no la enciendas"       | -                         | `negated: true` |
| **Compuesta**   | "no quiero que se abra" | "I don't want to open"    | `negated: true` |
| **Prohibitiva** | "deja de encender"      | "stop turning on"         | `negated: true` |
| **Implícita**   | "mejor no abras"        | "never open"              | `negated: true` |

Cuando `negated: true`, el endpoint `/execute` **NO ejecuta** la acción.

---

## 📦 Uso del Módulo NLP

```python
from nlp import IntentMatcher, DeviceMatcher, NegationDetector

# Detectar intención (Spanish)
matcher = IntentMatcher()
result = matcher.match("enciende la luz")
print(result.intent)      # "turn_on"
print(result.confidence)  # 0.85

# Detectar intención (English)
result_en = matcher.match("turn on the light")
print(result_en.intent)   # "turn_on"

# Detectar dispositivo
devices = {"luz_sala": {...}, "ventilador": {...}}
device_matcher = DeviceMatcher(devices)
device = device_matcher.match("prende la luz de la sala")
print(device)  # "luz_sala"

# Detectar negación (Spanish & English)
detector = NegationDetector()
neg_es = detector.detect("no enciendas la luz")
print(neg_es.is_negated)      # True
neg_en = detector.detect("don't turn on the light")
print(neg_en.is_negated)      # True
```

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
APP_NAME=NLP Service - Smart Home
DEBUG=True
PORT=8001
HOST=0.0.0.0

# Ollama (opcional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3

# Base de datos
DATABASE_URL=sqlite:///./nlp_smart_home.db

# Backend IoT (para /execute)
IOT_BACKEND_URL=http://iot-backend:8000
```

---

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE                                   │
│            (Voz / Texto / App / API)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              NLP SERVICE (FastAPI :8001)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   VOICE MODULE                          │ │
│  │   ┌─────────┐              ┌─────────┐                 │ │
│  │   │   STT   │──── text ───▶│   TTS   │                 │ │
│  │   │ (Google)│              │ (gTTS)  │                 │ │
│  │   └─────────┘              └─────────┘                 │ │
│  └──────────┬─────────────────────────────────────────────┘ │
│             │                                                │
│  ┌──────────▼─────────────────────────────────────────────┐ │
│  │                   NLP PIPELINE                          │ │
│  │                                                         │ │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐           │ │
│  │  │Normalize │──▶│ Negation │──▶│  Intent  │           │ │
│  │  │  Text    │   │ Detector │   │ Matcher  │           │ │
│  │  └──────────┘   └──────────┘   └────┬─────┘           │ │
│  │                                      │                  │ │
│  │                               ┌──────▼─────┐           │ │
│  │                               │  Device    │           │ │
│  │                               │  Matcher   │           │ │
│  │                               └──────┬─────┘           │ │
│  │                                      │                  │ │
│  │         ┌────────────────────────────▼───────────┐     │ │
│  │         │  Si confianza < 0.8 → Ollama/Phi3      │     │ │
│  │         └────────────────────────────────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    RESPUESTA    │
              │ {intent, device,│
              │  negated}       │
              └─────────────────┘
```

---

## 🧪 Ejemplos de Uso

### Python (httpx)

```python
import httpx
import asyncio

async def interpret(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/interpret",
            json={"text": text}
        )
        return response.json()

# Uso
result = asyncio.run(interpret("enciende la luz del comedor"))
print(result)
```

### JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8001/interpret", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "enciende la luz" }),
});
const data = await response.json();
console.log(data);
```

### cURL

```bash
# Interpretar
curl -X POST http://localhost:8001/interpret \
  -H "Content-Type: application/json" \
  -d '{"text": "apaga el ventilador"}'

# Ejecutar
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "abre la puerta del garage"}'

# Voz a texto
curl -X POST http://localhost:8001/voice/interpret \
  -F "audio=@mi_comando.wav"
```

---

## 📝 Licencia

MIT License - Proyecto de código abierto para sistemas domóticos inteligentes.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, abre un issue o pull request.

---

**Desarrollado con ❤️ para la comunidad de domótica**

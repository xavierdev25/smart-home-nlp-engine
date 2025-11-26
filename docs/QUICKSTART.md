# 📖 Guía Rápida de Uso - NLP Smart Home API

## Inicio Rápido

### 1. Iniciar el Servidor

```powershell
# Con Python
cd c:\Users\David\Desktop\nlp_ai_house
python main.py

# O con Uvicorn (recomendado)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Verificar que Funciona

```powershell
# Health check
curl http://localhost:8001/health
```

### 3. Interpretar tu Primer Comando

```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8001/interpret" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"text": "enciende la luz del comedor"}'
```

---

## Ejemplos por Tipo de Comando

### Encender/Apagar

```json
// Encender
{"text": "enciende la luz del comedor"}
{"text": "prende el foco de la sala"}
{"text": "activa el aire acondicionado"}

// Apagar
{"text": "apaga la luz de la cocina"}
{"text": "desactiva el ventilador"}
{"text": "corta la calefacción"}
```

### Abrir/Cerrar

```json
// Abrir
{"text": "abre la puerta del garage"}
{"text": "sube la persiana"}
{"text": "descorre las cortinas"}

// Cerrar
{"text": "cierra la ventana"}
{"text": "baja la persiana"}
{"text": "corre las cortinas"}
```

### Estado

```json
{"text": "¿cómo está la luz de la sala?"}
{"text": "estado del aire acondicionado"}
{"text": "verifica la puerta del garage"}
```

### Negaciones

```json
{"text": "no enciendas la luz"}
// → {"intent": "turn_on", "device": "luz_*", "negated": true}

{"text": "nunca abras esa puerta"}
// → {"intent": "open", "device": "puerta_*", "negated": true}

{"text": "deja de encender el ventilador"}
// → {"intent": "turn_on", "device": "ventilador_*", "negated": true}
```

---

## Swagger UI

Accede a la documentación interactiva:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

---

## Flujo de Integración Típico

```
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Asistente  │      │   NLP Service   │      │  Backend IoT    │
│   de Voz    │      │  (Este servicio)│      │   (Tu sistema)  │
└──────┬──────┘      └────────┬────────┘      └────────┬────────┘
       │                      │                        │
       │ 1. "enciende luz"    │                        │
       │─────────────────────▶│                        │
       │                      │                        │
       │ 2. {intent, device}  │                        │
       │◀─────────────────────│                        │
       │                      │                        │
       │                      │ 3. POST /luz_comedor/on│
       │                      │ (tu app lo ejecuta)    │
       │                      │ ───────────────────────▶
       │                      │                        │
       │                      │              4. 200 OK │
       │                      │ ◀───────────────────────
       │                      │                        │
       │ 5. "Luz encendida"   │                        │
       │◀─────────────────────│                        │
       │                      │                        │
```

---

## Códigos de Respuesta Comunes

| Resultado          | intent    | device        | negated | Significado               |
| ------------------ | --------- | ------------- | ------- | ------------------------- |
| ✅ Comando válido  | `turn_on` | `luz_comedor` | `false` | Ejecutar acción           |
| ✅ Comando negado  | `turn_on` | `luz_comedor` | `true`  | NO ejecutar               |
| ⚠️ Sin dispositivo | `turn_on` | `null`        | `false` | Preguntar qué dispositivo |
| ❌ No entendido    | `unknown` | `null`        | `false` | Pedir reformulación       |

---

## Tips de Uso

1. **Siempre verificar `negated`** antes de ejecutar acciones
2. **Usar `/interpret` para sistemas críticos** (solo interpretación)
3. **Usar `/execute` para prototipos** (interpretación + ejecución)
4. **Agregar aliases en `devices.json`** para mejorar reconocimiento
5. **Monitorear `/health`** para detectar problemas con Ollama

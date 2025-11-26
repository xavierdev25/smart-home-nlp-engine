# 🧠 Módulo NLP - Casa Inteligente

Módulo de Procesamiento de Lenguaje Natural para el sistema domótico.

## Estructura

```
nlp/
├── __init__.py          # Exportaciones públicas
├── constants.py         # Enums, constantes, umbrales
├── intents.py           # 50+ patrones regex de intenciones
├── aliases.py           # 200+ sinónimos dispositivos/habitaciones
├── negations.py         # Detector de 5 tipos de negaciones
├── normalizer.py        # Normalización de texto español
└── matchers.py          # Motores de matching
```

## Uso Rápido

```python
from nlp import (
    TextNormalizer,
    NegationDetector,
    IntentMatcher,
    DeviceMatcher,
)

# Normalizar texto
normalizer = TextNormalizer()
text = normalizer.normalize("¡Enciende la LUZ!")  # → "enciende la luz"

# Detectar negación
detector = NegationDetector()
result = detector.detect("no enciendas la luz")
print(result.is_negated)  # True

# Detectar intención
intent_matcher = IntentMatcher()
match = intent_matcher.match("enciende la luz")
print(match.intent)  # "turn_on"

# Detectar dispositivo
devices = [{"device_key": "luz_sala", "name": "Luz Sala", "aliases": ["luz de la sala"]}]
device_matcher = DeviceMatcher(devices)
match = device_matcher.match("enciende la luz de la sala")
print(match.device_key)  # "luz_sala"
```

## Componentes

### IntentType (Enum)

- `turn_on` - Encender
- `turn_off` - Apagar
- `open` - Abrir
- `close` - Cerrar
- `status` - Estado
- `toggle` - Alternar
- `unknown` - Desconocido

### DeviceType (Enum)

- `light`, `fan`, `door`, `window`, `curtain`, `lock`, `alarm`, `sensor`, `climate`, `other`

### NegationResult (Dataclass)

```python
@dataclass
class NegationResult:
    is_negated: bool
    negation_type: str  # "direct", "pronoun", "compound", "prohibitive", "implicit"
    negation_word: str
    confidence: float
```

## Documentación Completa

Ver [`docs/NLP_MODULE.md`](../docs/NLP_MODULE.md) para documentación detallada.

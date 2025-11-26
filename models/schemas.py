"""
Esquemas Pydantic para validación de datos de entrada y salida
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class IntentType(str, Enum):
    """Tipos de intenciones soportadas"""
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    OPEN = "open"
    CLOSE = "close"
    STATUS = "status"
    TOGGLE = "toggle"
    UNKNOWN = "unknown"


class CommandInput(BaseModel):
    """Esquema de entrada para el comando de usuario"""
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Comando en lenguaje natural del usuario",
        examples=["enciende la luz del comedor", "apaga el ventilador de la sala"]
    )


class InterpretationResult(BaseModel):
    """Esquema de salida con la interpretación del comando"""
    intent: Literal["turn_on", "turn_off", "open", "close", "status", "toggle", "unknown"] = Field(
        ...,
        description="Intención identificada del comando"
    )
    device: Optional[str] = Field(
        None,
        description="Clave del dispositivo identificado"
    )
    negated: bool = Field(
        False,
        description="Indica si el comando fue negado (ej: 'no enciendas')"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "intent": "turn_on",
                    "device": "luz_comedor",
                    "negated": False
                },
                {
                    "intent": "turn_off",
                    "device": "ventilador_sala",
                    "negated": False
                },
                {
                    "intent": "turn_on",
                    "device": "luz_sala",
                    "negated": True
                },
                {
                    "intent": "unknown",
                    "device": None,
                    "negated": False
                }
            ]
        }


class InterpretationResponse(BaseModel):
    """Respuesta completa del endpoint de interpretación"""
    success: bool = Field(..., description="Indica si la interpretación fue exitosa")
    data: InterpretationResult = Field(..., description="Resultado de la interpretación")
    original_text: str = Field(..., description="Texto original enviado por el usuario")
    confidence_note: Optional[str] = Field(
        None, 
        description="Nota adicional sobre la interpretación"
    )


class HealthResponse(BaseModel):
    """Respuesta del health check"""
    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
    ollama_status: str = Field(..., description="Estado de conexión con Ollama")


class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    success: bool = False
    error: str = Field(..., description="Mensaje de error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")

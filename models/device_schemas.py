"""
Esquemas Pydantic para dispositivos y endpoints
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum


class DeviceType(str, Enum):
    """Tipos de dispositivos"""
    LIGHT = "light"
    FAN = "fan"
    DOOR = "door"
    WINDOW = "window"
    CURTAIN = "curtain"
    ALARM = "alarm"
    SENSOR = "sensor"
    SWITCH = "switch"
    OTHER = "other"


class DeviceCreate(BaseModel):
    """Esquema para crear un dispositivo"""
    device_key: str = Field(..., min_length=1, max_length=100, description="Identificador único del dispositivo")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre descriptivo")
    type: str = Field(..., description="Tipo de dispositivo: light, fan, door, window, curtain, alarm")
    room: str = Field(..., description="Habitación donde está el dispositivo")
    
    # Endpoints opcionales
    endpoint_on: Optional[str] = Field(None, description="URL endpoint para encender/activar")
    endpoint_off: Optional[str] = Field(None, description="URL endpoint para apagar/desactivar")
    endpoint_open: Optional[str] = Field(None, description="URL endpoint para abrir")
    endpoint_close: Optional[str] = Field(None, description="URL endpoint para cerrar")
    endpoint_status: Optional[str] = Field(None, description="URL endpoint para consultar estado")
    
    # Aliases para reconocimiento NLP
    aliases: Optional[List[str]] = Field(default=[], description="Aliases para reconocimiento por voz/texto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_key": "luz_sala",
                "name": "Luz de la sala",
                "type": "light",
                "room": "sala",
                "endpoint_on": "http://192.168.1.100/api/lights/sala/on",
                "endpoint_off": "http://192.168.1.100/api/lights/sala/off",
                "endpoint_status": "http://192.168.1.100/api/lights/sala/status",
                "aliases": ["luz sala", "lampara sala", "foco sala"]
            }
        }


class DeviceUpdate(BaseModel):
    """Esquema para actualizar un dispositivo"""
    name: Optional[str] = None
    type: Optional[str] = None
    room: Optional[str] = None
    endpoint_on: Optional[str] = None
    endpoint_off: Optional[str] = None
    endpoint_open: Optional[str] = None
    endpoint_close: Optional[str] = None
    endpoint_status: Optional[str] = None
    aliases: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EndpointsUpdate(BaseModel):
    """Esquema para actualizar solo los endpoints de un dispositivo"""
    endpoint_on: Optional[str] = Field(None, description="URL para encender")
    endpoint_off: Optional[str] = Field(None, description="URL para apagar")
    endpoint_open: Optional[str] = Field(None, description="URL para abrir")
    endpoint_close: Optional[str] = Field(None, description="URL para cerrar")
    endpoint_status: Optional[str] = Field(None, description="URL para estado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "endpoint_on": "http://192.168.1.100/relay/1/on",
                "endpoint_off": "http://192.168.1.100/relay/1/off",
                "endpoint_status": "http://192.168.1.100/relay/1/status"
            }
        }


class DeviceResponse(BaseModel):
    """Esquema de respuesta con información del dispositivo"""
    device_key: str
    name: str
    type: str
    room: str
    endpoint_on: Optional[str]
    endpoint_off: Optional[str]
    endpoint_open: Optional[str]
    endpoint_close: Optional[str]
    endpoint_status: Optional[str]
    aliases: List[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Respuesta con lista de dispositivos"""
    success: bool
    total: int
    devices: List[DeviceResponse]


class RoomCreate(BaseModel):
    """Esquema para crear una habitación"""
    room_key: str = Field(..., description="Identificador único de la habitación")
    name: str = Field(..., description="Nombre de la habitación")
    aliases: Optional[List[str]] = Field(default=[], description="Aliases para reconocimiento")


class BulkDeviceCreate(BaseModel):
    """Esquema para crear múltiples dispositivos"""
    devices: List[DeviceCreate]

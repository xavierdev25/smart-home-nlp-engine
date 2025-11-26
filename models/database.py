"""
Modelos de base de datos para el sistema domótico
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from enum import Enum

Base = declarative_base()


class DeviceType(str, Enum):
    """Tipos de dispositivos soportados"""
    LIGHT = "light"
    FAN = "fan"
    DOOR = "door"
    WINDOW = "window"
    CURTAIN = "curtain"
    ALARM = "alarm"
    SENSOR = "sensor"
    SWITCH = "switch"
    OTHER = "other"


class Device(Base):
    """
    Modelo de dispositivo IoT con sus endpoints
    
    Tabla: devices
    """
    __tablename__ = "devices"
    
    # Identificador único del dispositivo
    device_key = Column(String(100), primary_key=True, index=True)
    
    # Información básica
    name = Column(String(200), nullable=False)  # Nombre descriptivo
    type = Column(String(50), nullable=False)   # light, fan, door, etc.
    room = Column(String(100), nullable=False)  # sala, cocina, etc.
    
    # Endpoints de control
    endpoint_on = Column(String(500), nullable=True)      # URL para encender/activar
    endpoint_off = Column(String(500), nullable=True)     # URL para apagar/desactivar
    endpoint_open = Column(String(500), nullable=True)    # URL para abrir
    endpoint_close = Column(String(500), nullable=True)   # URL para cerrar
    endpoint_status = Column(String(500), nullable=True)  # URL para consultar estado
    
    # Aliases para reconocimiento NLP (JSON array como string)
    aliases = Column(String(1000), nullable=True)  # ["luz sala", "lampara sala"]
    
    # Metadatos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Device {self.device_key}: {self.name}>"


class Room(Base):
    """
    Modelo de habitación con sus aliases
    
    Tabla: rooms
    """
    __tablename__ = "rooms"
    
    room_key = Column(String(100), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    aliases = Column(String(500), nullable=True)  # JSON array: ["sala", "living"]
    
    def __repr__(self):
        return f"<Room {self.room_key}: {self.name}>"

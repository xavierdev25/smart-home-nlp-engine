"""
Router de API para gestión de dispositivos
Endpoints CRUD para dispositivos y sus endpoints IoT
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from services.device_service import DeviceService, RoomService
from models.device_schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    EndpointsUpdate,
    RoomCreate,
    BulkDeviceCreate
)

router = APIRouter(prefix="/api/devices", tags=["Gestión de Dispositivos"])


# =============================================================================
# ENDPOINTS DE DISPOSITIVOS
# =============================================================================

@router.get("", response_model=DeviceListResponse)
def list_devices(
    room: str = None,
    device_type: str = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los dispositivos.
    Opcionalmente filtra por habitación o tipo.
    """
    service = DeviceService(db)
    
    if room:
        devices = service.get_devices_by_room(room)
    elif device_type:
        devices = service.get_devices_by_type(device_type)
    else:
        devices = service.get_all_devices()
    
    # Convertir a response format
    devices_response = []
    for device in devices:
        aliases = json.loads(device.aliases) if device.aliases else []
        devices_response.append(DeviceResponse(
            device_key=device.device_key,
            name=device.name,
            type=device.type,
            room=device.room,
            endpoint_on=device.endpoint_on,
            endpoint_off=device.endpoint_off,
            endpoint_open=device.endpoint_open,
            endpoint_close=device.endpoint_close,
            endpoint_status=device.endpoint_status,
            aliases=aliases,
            is_active=device.is_active
        ))
    
    return DeviceListResponse(
        success=True,
        total=len(devices_response),
        devices=devices_response
    )


@router.get("/{device_key}", response_model=DeviceResponse)
def get_device(device_key: str, db: Session = Depends(get_db)):
    """Obtiene un dispositivo por su key"""
    service = DeviceService(db)
    device = service.get_device(device_key)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo '{device_key}' no encontrado"
        )
    
    aliases = json.loads(device.aliases) if device.aliases else []
    return DeviceResponse(
        device_key=device.device_key,
        name=device.name,
        type=device.type,
        room=device.room,
        endpoint_on=device.endpoint_on,
        endpoint_off=device.endpoint_off,
        endpoint_open=device.endpoint_open,
        endpoint_close=device.endpoint_close,
        endpoint_status=device.endpoint_status,
        aliases=aliases,
        is_active=device.is_active
    )


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    """Crea un nuevo dispositivo"""
    service = DeviceService(db)
    
    # Verificar si ya existe
    existing = service.get_device(device_data.device_key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El dispositivo '{device_data.device_key}' ya existe"
        )
    
    device = service.create_device(device_data.model_dump())
    aliases = json.loads(device.aliases) if device.aliases else []
    
    return DeviceResponse(
        device_key=device.device_key,
        name=device.name,
        type=device.type,
        room=device.room,
        endpoint_on=device.endpoint_on,
        endpoint_off=device.endpoint_off,
        endpoint_open=device.endpoint_open,
        endpoint_close=device.endpoint_close,
        endpoint_status=device.endpoint_status,
        aliases=aliases,
        is_active=device.is_active
    )


@router.put("/{device_key}", response_model=DeviceResponse)
def update_device(
    device_key: str, 
    device_data: DeviceUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un dispositivo existente"""
    service = DeviceService(db)
    
    # Filtrar solo campos con valor
    update_data = {k: v for k, v in device_data.model_dump().items() if v is not None}
    
    device = service.update_device(device_key, update_data)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo '{device_key}' no encontrado"
        )
    
    aliases = json.loads(device.aliases) if device.aliases else []
    return DeviceResponse(
        device_key=device.device_key,
        name=device.name,
        type=device.type,
        room=device.room,
        endpoint_on=device.endpoint_on,
        endpoint_off=device.endpoint_off,
        endpoint_open=device.endpoint_open,
        endpoint_close=device.endpoint_close,
        endpoint_status=device.endpoint_status,
        aliases=aliases,
        is_active=device.is_active
    )


@router.patch("/{device_key}/endpoints")
def update_device_endpoints(
    device_key: str,
    endpoints: EndpointsUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza solo los endpoints de un dispositivo.
    Útil para configurar las URLs de control.
    """
    service = DeviceService(db)
    
    device = service.update_endpoints(
        device_key,
        endpoint_on=endpoints.endpoint_on,
        endpoint_off=endpoints.endpoint_off,
        endpoint_open=endpoints.endpoint_open,
        endpoint_close=endpoints.endpoint_close,
        endpoint_status=endpoints.endpoint_status
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo '{device_key}' no encontrado"
        )
    
    return {
        "success": True,
        "message": f"Endpoints actualizados para '{device_key}'",
        "device_key": device_key,
        "endpoints": {
            "on": device.endpoint_on,
            "off": device.endpoint_off,
            "open": device.endpoint_open,
            "close": device.endpoint_close,
            "status": device.endpoint_status
        }
    }


@router.delete("/{device_key}")
def delete_device(
    device_key: str, 
    permanent: bool = False,
    db: Session = Depends(get_db)
):
    """
    Elimina un dispositivo.
    Por defecto hace soft delete (is_active=False).
    Usar permanent=true para eliminar permanentemente.
    """
    service = DeviceService(db)
    
    success = service.delete_device(device_key, soft_delete=not permanent)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo '{device_key}' no encontrado"
        )
    
    return {
        "success": True,
        "message": f"Dispositivo '{device_key}' {'eliminado permanentemente' if permanent else 'desactivado'}"
    }


# =============================================================================
# ENDPOINTS BULK
# =============================================================================

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_devices(data: BulkDeviceCreate, db: Session = Depends(get_db)):
    """Crea múltiples dispositivos de una vez"""
    service = DeviceService(db)
    
    devices_data = [d.model_dump() for d in data.devices]
    created = service.bulk_create_devices(devices_data)
    
    return {
        "success": True,
        "message": f"Creados {len(created)} dispositivos",
        "device_keys": [d.device_key for d in created]
    }


@router.post("/import-json")
def import_from_json(db: Session = Depends(get_db)):
    """
    Importa dispositivos desde el archivo devices.json a la base de datos.
    No sobrescribe dispositivos existentes.
    """
    from pathlib import Path
    from config.settings import settings
    
    json_path = Path(__file__).parent.parent / settings.DEVICES_FILE
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo {settings.DEVICES_FILE} no encontrado"
        )
    
    service = DeviceService(db)
    count = service.import_from_json(json_data)
    
    return {
        "success": True,
        "message": f"Importados {count} dispositivos desde JSON",
        "source": str(json_path)
    }


# =============================================================================
# ENDPOINTS DE CONSULTA
# =============================================================================

@router.get("/{device_key}/endpoint/{action}")
def get_device_endpoint(
    device_key: str, 
    action: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el endpoint para una acción específica de un dispositivo.
    Acciones válidas: on, off, open, close, status
    """
    service = DeviceService(db)
    
    endpoint = service.get_endpoint(device_key, action)
    if endpoint is None:
        device = service.get_device(device_key)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dispositivo '{device_key}' no encontrado"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay endpoint configurado para acción '{action}' en '{device_key}'"
        )
    
    return {
        "device_key": device_key,
        "action": action,
        "endpoint": endpoint
    }

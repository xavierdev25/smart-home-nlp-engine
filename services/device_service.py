"""
Servicio para gestión de dispositivos IoT
Maneja la lógica de negocio y acceso a base de datos
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models.database import Device, Room


class DeviceService:
    """Servicio para operaciones CRUD de dispositivos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # OPERACIONES DE LECTURA
    # =========================================================================
    
    def get_device(self, device_key: str) -> Optional[Device]:
        """Obtiene un dispositivo por su key"""
        return self.db.query(Device).filter(
            Device.device_key == device_key,
            Device.is_active == True
        ).first()
    
    def get_all_devices(self) -> List[Device]:
        """Obtiene todos los dispositivos activos"""
        return self.db.query(Device).filter(Device.is_active == True).all()
    
    def get_devices_by_room(self, room: str) -> List[Device]:
        """Obtiene dispositivos de una habitación"""
        return self.db.query(Device).filter(
            Device.room == room,
            Device.is_active == True
        ).all()
    
    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Obtiene dispositivos de un tipo específico"""
        return self.db.query(Device).filter(
            Device.type == device_type,
            Device.is_active == True
        ).all()
    
    def get_endpoint(self, device_key: str, action: str) -> Optional[str]:
        """
        Obtiene el endpoint para una acción específica de un dispositivo.
        
        Args:
            device_key: Clave del dispositivo
            action: Acción (on, off, open, close, status)
            
        Returns:
            URL del endpoint o None
        """
        device = self.get_device(device_key)
        if not device:
            return None
        
        endpoint_map = {
            "on": device.endpoint_on,
            "off": device.endpoint_off,
            "open": device.endpoint_open,
            "close": device.endpoint_close,
            "status": device.endpoint_status,
            # Mapeo de intents a acciones
            "turn_on": device.endpoint_on,
            "turn_off": device.endpoint_off,
        }
        
        return endpoint_map.get(action)
    
    def get_devices_for_nlp(self) -> Dict[str, Any]:
        """
        Obtiene los dispositivos en formato compatible con el NLP pipeline.
        Esto permite que el NLP cargue datos desde la BD en lugar del JSON.
        """
        devices = self.get_all_devices()
        rooms = self.db.query(Room).all()
        
        # Construir estructura compatible con el JSON original
        devices_dict = {}
        for device in devices:
            aliases = json.loads(device.aliases) if device.aliases else []
            devices_dict[device.device_key] = {
                "name": device.name,
                "type": device.type,
                "room": device.room,
                "aliases": aliases,
                "endpoints": {
                    "on": device.endpoint_on,
                    "off": device.endpoint_off,
                    "open": device.endpoint_open,
                    "close": device.endpoint_close,
                    "status": device.endpoint_status,
                }
            }
        
        rooms_dict = {}
        for room in rooms:
            aliases = json.loads(room.aliases) if room.aliases else []
            rooms_dict[room.room_key] = aliases
        
        # Tipos de dispositivos (estático)
        device_types = {
            "light": ["luz", "luces", "lámpara", "lampara", "foco", "focos", "iluminación"],
            "fan": ["ventilador", "ventiladores", "abanico", "extractor"],
            "door": ["puerta", "puertas", "portón", "porton"],
            "window": ["ventana", "ventanas", "ventanal"],
            "curtain": ["cortina", "cortinas", "persiana", "persianas"],
            "alarm": ["alarma", "alarmas", "sistema de alarma"],
        }
        
        return {
            "devices": devices_dict,
            "rooms": rooms_dict,
            "device_types": device_types
        }
    
    # =========================================================================
    # OPERACIONES DE ESCRITURA
    # =========================================================================
    
    def create_device(self, device_data: Dict[str, Any]) -> Device:
        """Crea un nuevo dispositivo"""
        # Convertir aliases a JSON string si es lista
        if isinstance(device_data.get("aliases"), list):
            device_data["aliases"] = json.dumps(device_data["aliases"], ensure_ascii=False)
        
        device = Device(**device_data)
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def update_device(self, device_key: str, device_data: Dict[str, Any]) -> Optional[Device]:
        """Actualiza un dispositivo existente"""
        device = self.get_device(device_key)
        if not device:
            return None
        
        # Convertir aliases a JSON string si es lista
        if isinstance(device_data.get("aliases"), list):
            device_data["aliases"] = json.dumps(device_data["aliases"], ensure_ascii=False)
        
        for key, value in device_data.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def delete_device(self, device_key: str, soft_delete: bool = True) -> bool:
        """
        Elimina un dispositivo.
        
        Args:
            device_key: Clave del dispositivo
            soft_delete: Si True, solo marca como inactivo. Si False, elimina de la BD.
        """
        device = self.db.query(Device).filter(Device.device_key == device_key).first()
        if not device:
            return False
        
        if soft_delete:
            device.is_active = False
            self.db.commit()
        else:
            self.db.delete(device)
            self.db.commit()
        
        return True
    
    def update_endpoints(
        self, 
        device_key: str, 
        endpoint_on: str = None,
        endpoint_off: str = None,
        endpoint_open: str = None,
        endpoint_close: str = None,
        endpoint_status: str = None
    ) -> Optional[Device]:
        """Actualiza solo los endpoints de un dispositivo"""
        device = self.get_device(device_key)
        if not device:
            return None
        
        if endpoint_on is not None:
            device.endpoint_on = endpoint_on
        if endpoint_off is not None:
            device.endpoint_off = endpoint_off
        if endpoint_open is not None:
            device.endpoint_open = endpoint_open
        if endpoint_close is not None:
            device.endpoint_close = endpoint_close
        if endpoint_status is not None:
            device.endpoint_status = endpoint_status
        
        self.db.commit()
        self.db.refresh(device)
        return device
    
    # =========================================================================
    # OPERACIONES BULK
    # =========================================================================
    
    def bulk_create_devices(self, devices_list: List[Dict[str, Any]]) -> List[Device]:
        """Crea múltiples dispositivos de una vez"""
        created = []
        for device_data in devices_list:
            if isinstance(device_data.get("aliases"), list):
                device_data["aliases"] = json.dumps(device_data["aliases"], ensure_ascii=False)
            device = Device(**device_data)
            self.db.add(device)
            created.append(device)
        
        self.db.commit()
        for device in created:
            self.db.refresh(device)
        
        return created
    
    def import_from_json(self, json_data: Dict[str, Any]) -> int:
        """
        Importa dispositivos desde el formato JSON del archivo devices.json
        Retorna el número de dispositivos importados.
        """
        devices = json_data.get("devices", {})
        count = 0
        
        for device_key, device_info in devices.items():
            existing = self.db.query(Device).filter(Device.device_key == device_key).first()
            if existing:
                continue  # Skip si ya existe
            
            device = Device(
                device_key=device_key,
                name=device_info.get("name", device_key),
                type=device_info.get("type", "other"),
                room=device_info.get("room", "general"),
                aliases=json.dumps(device_info.get("aliases", []), ensure_ascii=False),
            )
            self.db.add(device)
            count += 1
        
        self.db.commit()
        return count


class RoomService:
    """Servicio para operaciones de habitaciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_room(self, room_key: str) -> Optional[Room]:
        return self.db.query(Room).filter(Room.room_key == room_key).first()
    
    def get_all_rooms(self) -> List[Room]:
        return self.db.query(Room).all()
    
    def create_room(self, room_key: str, name: str, aliases: List[str] = None) -> Room:
        room = Room(
            room_key=room_key,
            name=name,
            aliases=json.dumps(aliases or [], ensure_ascii=False)
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

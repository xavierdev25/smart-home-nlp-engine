"""
Configuración del microservicio NLP
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración general del servicio NLP"""
    
    # Configuración del servidor
    APP_NAME: str = "NLP Service - Smart Home"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # Configuración de Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "phi3"
    OLLAMA_TIMEOUT: int = 60
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./nlp_smart_home.db"
    # Para PostgreSQL: "postgresql://user:password@localhost/dbname"
    # Para MySQL: "mysql+pymysql://user:password@localhost/dbname"
    
    # Fuente de datos para dispositivos: "json" o "database"
    DEVICES_SOURCE: str = "json"
    
    # Rutas de archivos
    DEVICES_FILE: str = "data/devices.json"
    
    # Backend IoT (URL base de tu backend de control)
    IOT_BACKEND_URL: str = "http://localhost:3000"
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

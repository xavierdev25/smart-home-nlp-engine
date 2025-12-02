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
    
    # ============================================
    # Configuración de Modo Offline
    # ============================================
    # Si es True, usará motores locales que no requieren internet
    OFFLINE_MODE: bool = False
    
    # Motor de reconocimiento de voz (STT)
    # Opciones: "google" (online), "whisper" (offline), "vosk" (offline)
    STT_ENGINE: str = "google"
    
    # Motor de síntesis de voz (TTS)
    # Opciones: "edge_tts" (online), "gtts" (online), "pyttsx3" (offline), "espeak" (offline)
    TTS_ENGINE: str = "edge_tts"
    
    # Modelo de Whisper (si STT_ENGINE="whisper")
    # Opciones: "tiny", "base", "small", "medium", "large"
    # tiny/base: rápidos, menos precisos | medium/large: lentos, muy precisos
    WHISPER_MODEL: str = "base"
    
    # Ruta al modelo Vosk (si STT_ENGINE="vosk")
    # Descarga modelos de: https://alphacephei.com/vosk/models
    VOSK_MODEL_PATH: str = "models/vosk-model-es"
    
    # Idioma para reconocimiento de voz
    # es-ES (España), es-MX (México), en-US (USA), en-GB (UK)
    VOICE_LANGUAGE: str = "es-ES"
    
    # Voz para TTS (solo Edge TTS)
    TTS_VOICE: str = "es-MX-DaliaNeural"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

"""
Router para endpoints de control por voz (STT/TTS)
Permite enviar audio y recibir respuestas de voz
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import io

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/voice",
    tags=["Voz"],
    responses={
        500: {"description": "Error interno del servidor"}
    }
)


# ============================================
# Schemas
# ============================================

class TextToSpeechRequest(BaseModel):
    """Request para síntesis de voz"""
    text: str = Field(..., description="Texto a convertir en voz", min_length=1, max_length=1000)
    voice: str = Field(
        default="es-MX-DaliaNeural",
        description="Voz a utilizar (ver /voice/voices para opciones)"
    )


class VoiceCommandResponse(BaseModel):
    """Respuesta de un comando de voz"""
    success: bool
    original_text: str = Field(..., description="Texto reconocido del audio")
    intent: Optional[str] = Field(None, description="Intención detectada")
    device: Optional[str] = Field(None, description="Dispositivo identificado")
    negated: bool = Field(False, description="Si el comando está negado")
    response_text: str = Field(..., description="Respuesta en texto natural")
    confidence_note: Optional[str] = Field(None, description="Nota de confianza")
    error: Optional[str] = Field(None, description="Mensaje de error si aplica")


class VoiceInfo(BaseModel):
    """Información de una voz disponible"""
    name: str
    locale: str
    gender: str
    short_name: str


class STTResult(BaseModel):
    """Resultado de reconocimiento de voz"""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None


# ============================================
# Instancia global del asistente
# ============================================

_voice_assistant = None


def get_voice_assistant():
    """Obtiene o crea la instancia del asistente de voz"""
    global _voice_assistant
    if _voice_assistant is None:
        from voice import VoiceAssistant
        from voice.speech_to_text import STTEngine
        from voice.text_to_speech import TTSEngine, TTSVoice
        
        _voice_assistant = VoiceAssistant(
            stt_engine=STTEngine.GOOGLE,
            tts_engine=TTSEngine.GTTS  # gTTS es más estable que Edge TTS
        )
        logger.info("Asistente de voz inicializado")
    
    return _voice_assistant


# ============================================
# Endpoints
# ============================================

@router.post(
    "/interpret",
    response_model=VoiceCommandResponse,
    summary="Interpretar comando de voz",
    description="""
    Recibe un archivo de audio WAV y lo interpreta como comando domótico.
    
    ## Formato de Audio Soportado
    - **Formato**: WAV (PCM)
    - **Sample Rate**: 16000 Hz (recomendado) o 44100 Hz
    - **Canales**: Mono (1 canal)
    - **Bits**: 16-bit
    
    ## Ejemplo con cURL
    ```bash
    curl -X POST "http://localhost:8001/voice/interpret" \\
      -F "audio=@comando.wav"
    ```
    """
)
async def interpret_voice_command(
    audio: UploadFile = File(..., description="Archivo de audio WAV"),
    include_audio_response: bool = Query(
        False, 
        description="Si incluir audio de respuesta en header X-Audio-Response-URL"
    )
):
    """Interpreta un comando de voz desde archivo de audio"""
    
    # Validar tipo de archivo
    if not audio.filename.lower().endswith(('.wav', '.wave')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos WAV. Convierte tu audio a WAV primero."
        )
    
    try:
        # Leer contenido del audio
        audio_bytes = await audio.read()
        
        if len(audio_bytes) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo de audio demasiado pequeño o vacío"
            )
        
        # Procesar con el asistente
        assistant = get_voice_assistant()
        response = await assistant.process_audio_bytes(
            audio_bytes=audio_bytes,
            is_wav=True,
            speak_response=False
        )
        
        return VoiceCommandResponse(
            success=response.success,
            original_text=response.original_text,
            intent=response.intent,
            device=response.device,
            negated=response.negated,
            response_text=response.response_text,
            confidence_note=response.confidence_note,
            error=response.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando audio: {str(e)}"
        )


@router.post(
    "/interpret-with-audio",
    summary="Interpretar comando y obtener respuesta de audio",
    description="""
    Interpreta un comando de voz y devuelve la respuesta como audio MP3.
    
    La respuesta es directamente el archivo de audio con la respuesta hablada.
    Los metadatos del comando se incluyen en los headers de respuesta.
    """
)
async def interpret_voice_with_audio_response(
    audio: UploadFile = File(..., description="Archivo de audio WAV")
):
    """Interpreta comando y devuelve audio de respuesta"""
    
    if not audio.filename.lower().endswith(('.wav', '.wave')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos WAV"
        )
    
    try:
        audio_bytes = await audio.read()
        
        assistant = get_voice_assistant()
        response = await assistant.process_audio_bytes(
            audio_bytes=audio_bytes,
            is_wav=True,
            speak_response=False
        )
        
        # Generar audio de respuesta
        response_audio = await assistant.get_response_audio(response.response_text)
        
        if not response_audio:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo generar audio de respuesta"
            )
        
        # Devolver audio con metadatos en headers
        headers = {
            "X-Original-Text": response.original_text or "",
            "X-Intent": response.intent or "unknown",
            "X-Device": response.device or "",
            "X-Negated": str(response.negated).lower(),
            "X-Response-Text": response.response_text,
            "X-Success": str(response.success).lower()
        }
        
        return StreamingResponse(
            io.BytesIO(response_audio),
            media_type="audio/mpeg",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/transcribe",
    response_model=STTResult,
    summary="Transcribir audio a texto (solo STT)",
    description="Convierte audio WAV a texto sin interpretar el comando"
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Archivo de audio WAV")
):
    """Solo transcribe audio a texto, sin procesar NLP"""
    
    if not audio.filename.lower().endswith(('.wav', '.wave')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos WAV"
        )
    
    try:
        audio_bytes = await audio.read()
        
        assistant = get_voice_assistant()
        text, error = assistant.stt.recognize_from_wav_bytes(audio_bytes)
        
        return STTResult(
            success=text is not None,
            text=text,
            error=error
        )
        
    except Exception as e:
        logger.error(f"Error transcribiendo: {e}")
        return STTResult(success=False, error=str(e))


@router.post(
    "/synthesize",
    summary="Sintetizar texto a voz (TTS)",
    description="""
    Convierte texto a audio MP3 usando síntesis de voz.
    
    ## Voces Disponibles
    - `es-MX-DaliaNeural` - Dalia (México, femenina) - DEFAULT
    - `es-MX-JorgeNeural` - Jorge (México, masculina)
    - `es-ES-ElviraNeural` - Elvira (España, femenina)
    - `es-ES-AlvaroNeural` - Álvaro (España, masculina)
    - `es-AR-ElenaNeural` - Elena (Argentina, femenina)
    - `es-AR-TomasNeural` - Tomás (Argentina, masculina)
    
    ## Ejemplo
    ```bash
    curl -X POST "http://localhost:8001/voice/synthesize" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "Luz del comedor encendida"}' \\
      --output respuesta.mp3
    ```
    """
)
async def synthesize_speech(request: TextToSpeechRequest):
    """Convierte texto a audio"""
    
    try:
        from voice.text_to_speech import TextToSpeech, TTSEngine
        
        tts = TextToSpeech(
            engine=TTSEngine.EDGE_TTS,
            voice=request.voice
        )
        
        audio_bytes = await tts.synthesize_to_bytes(request.text)
        
        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo sintetizar el audio"
            )
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"Error sintetizando: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/voices",
    summary="Listar voces disponibles",
    description="Retorna las voces de síntesis disponibles para español"
)
async def list_voices():
    """Lista las voces de TTS disponibles"""
    
    try:
        from voice.text_to_speech import TextToSpeech
        
        voices = TextToSpeech.list_edge_voices(language="es")
        
        return {
            "success": True,
            "total": len(voices),
            "voices": [
                {
                    "name": v.get("FriendlyName", v["ShortName"]),
                    "short_name": v["ShortName"],
                    "locale": v["Locale"],
                    "gender": v["Gender"]
                }
                for v in voices
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listando voces: {e}")
        return {
            "success": False,
            "error": str(e),
            "voices": []
        }


@router.get(
    "/engines",
    summary="Listar motores disponibles",
    description="Retorna información sobre los motores STT y TTS disponibles"
)
async def list_engines():
    """Lista los motores de voz disponibles"""
    
    return {
        "stt_engines": [
            {
                "id": "google",
                "name": "Google Speech Recognition",
                "type": "online",
                "free": True,
                "quality": "alta",
                "description": "Reconocimiento online gratuito de Google"
            },
            {
                "id": "google_cloud",
                "name": "Google Cloud Speech",
                "type": "online",
                "free": False,
                "quality": "muy alta",
                "description": "API de pago de Google Cloud"
            },
            {
                "id": "whisper",
                "name": "OpenAI Whisper",
                "type": "offline",
                "free": True,
                "quality": "muy alta",
                "description": "Modelo local de OpenAI (requiere instalación adicional)"
            },
            {
                "id": "vosk",
                "name": "Vosk",
                "type": "offline",
                "free": True,
                "quality": "buena",
                "description": "Modelo ligero offline (requiere modelo español)"
            }
        ],
        "tts_engines": [
            {
                "id": "edge_tts",
                "name": "Microsoft Edge TTS",
                "type": "online",
                "free": True,
                "quality": "muy alta",
                "description": "Voces neurales de Microsoft (RECOMENDADO)"
            },
            {
                "id": "gtts",
                "name": "Google TTS",
                "type": "online",
                "free": True,
                "quality": "buena",
                "description": "Google Text-to-Speech"
            },
            {
                "id": "pyttsx3",
                "name": "pyttsx3",
                "type": "offline",
                "free": True,
                "quality": "básica",
                "description": "Motor offline del sistema operativo"
            }
        ],
        "default": {
            "stt": "google",
            "tts": "edge_tts",
            "voice": "es-MX-DaliaNeural"
        }
    }


@router.get(
    "/status",
    summary="Estado del módulo de voz",
    description="Verifica si los componentes de voz están disponibles"
)
async def voice_status():
    """Verifica el estado del módulo de voz"""
    
    status_info = {
        "speech_recognition": False,
        "edge_tts": False,
        "gtts": False,
        "pyttsx3": False,
        "pygame": False,
        "pyaudio": False
    }
    
    # Verificar dependencias
    try:
        import speech_recognition
        status_info["speech_recognition"] = True
    except ImportError:
        pass
    
    try:
        import edge_tts
        status_info["edge_tts"] = True
    except ImportError:
        pass
    
    try:
        import gtts
        status_info["gtts"] = True
    except ImportError:
        pass
    
    try:
        import pyttsx3
        status_info["pyttsx3"] = True
    except ImportError:
        pass
    
    try:
        import pygame
        status_info["pygame"] = True
    except ImportError:
        pass
    
    try:
        import pyaudio
        status_info["pyaudio"] = True
    except ImportError:
        pass
    
    # Determinar si el módulo está operativo
    stt_ready = status_info["speech_recognition"]
    tts_ready = status_info["edge_tts"] or status_info["gtts"] or status_info["pyttsx3"]
    
    return {
        "operational": stt_ready and tts_ready,
        "stt_ready": stt_ready,
        "tts_ready": tts_ready,
        "components": status_info,
        "message": "Módulo de voz operativo" if (stt_ready and tts_ready) 
                   else "Instala dependencias: pip install SpeechRecognition PyAudio edge-tts pygame"
    }

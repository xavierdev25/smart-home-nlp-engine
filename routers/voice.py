"""
Router para endpoints de control por voz (STT/TTS)
Bilingual voice control - Spanish and English support
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
        500: {"description": "Internal server error / Error interno del servidor"}
    }
)


# ============================================
# Schemas
# ============================================

class TextToSpeechRequest(BaseModel):
    """Request for voice synthesis / Solicitud de síntesis de voz"""
    text: str = Field(..., description="Text to convert to speech", min_length=1, max_length=1000)
    voice: str = Field(
        default="es-MX-DaliaNeural",
        description="Voice to use (see /voice/voices for options). ES: es-MX-DaliaNeural, EN: en-US-JennyNeural"
    )
    language: str = Field(
        default="es",
        description="Text language: 'es' (Spanish) or 'en' (English)"
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
    summary="Interpret voice command / Interpretar comando de voz",
    description="""
    Receives a WAV audio file and interprets it as a smart home command.
    Supports **Spanish** and **English** commands.
    
    ## Supported Audio Format
    - **Format**: WAV (PCM)
    - **Sample Rate**: 16000 Hz (recommended) or 44100 Hz
    - **Channels**: Mono (1 channel)
    - **Bits**: 16-bit
    
    ## Example Commands / Comandos de Ejemplo
    
    | Language | Command |
    |----------|---------|
    | 🇪🇸 Spanish | "enciende la luz del salón" |
    | 🇺🇸 English | "turn on the living room light" |
    
    ## Example with cURL
    ```bash
    curl -X POST "http://localhost:8001/voice/interpret" \\
      -F "audio=@command.wav"
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
    summary="Synthesize text to speech (TTS) / Sintetizar texto a voz",
    description="""
    Converts text to MP3 audio using voice synthesis. **Bilingual: Spanish and English**.
    
    ## Spanish Voices / Voces en Español
    | Voice | Region | Gender |
    |-------|--------|--------|
    | `es-MX-DaliaNeural` | México | Female (DEFAULT) |
    | `es-MX-JorgeNeural` | México | Male |
    | `es-ES-ElviraNeural` | España | Female |
    | `es-ES-AlvaroNeural` | España | Male |
    | `es-AR-ElenaNeural` | Argentina | Female |
    | `es-AR-TomasNeural` | Argentina | Male |
    
    ## English Voices / Voces en Inglés
    | Voice | Region | Gender |
    |-------|--------|--------|
    | `en-US-JennyNeural` | US | Female |
    | `en-US-GuyNeural` | US | Male |
    | `en-GB-SoniaNeural` | UK | Female |
    | `en-GB-RyanNeural` | UK | Male |
    | `en-AU-NatashaNeural` | Australia | Female |
    
    ## Examples / Ejemplos
    
    **Spanish:**
    ```bash
    curl -X POST "http://localhost:8001/voice/synthesize" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "Luz del salón encendida", "language": "es"}' \\
      --output respuesta.mp3
    ```
    
    **English:**
    ```bash
    curl -X POST "http://localhost:8001/voice/synthesize" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "Living room light turned on", "language": "en", "voice": "en-US-JennyNeural"}' \\
      --output response.mp3
    ```
    """
)
async def synthesize_speech(request: TextToSpeechRequest):
    """Convierte texto a audio"""
    
    try:
        from voice.text_to_speech import TextToSpeech, TTSEngine
        
        tts = TextToSpeech(
            engine=TTSEngine.GTTS,
            voice=request.voice,
            language=request.language
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
    summary="List available voices / Listar voces disponibles",
    description="Returns available TTS voices for Spanish and English synthesis"
)
async def list_voices(
    language: str = Query("es", description="Filter by language: 'es' (Spanish) or 'en' (English)")
):
    """Lista las voces de TTS disponibles"""
    
    try:
        from voice.text_to_speech import TextToSpeech
        
        voices = TextToSpeech.list_edge_voices(language=language)
        
        return {
            "success": True,
            "language": language,
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
    summary="List available engines / Listar motores disponibles",
    description="Returns information about available STT and TTS engines for voice control"
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

"""
Asistente de voz completo
Integra STT + NLP Pipeline + TTS para control por voz
"""
import logging
import asyncio
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .speech_to_text import SpeechToText, STTEngine
from .text_to_speech import TextToSpeech, TTSEngine, TTSVoice

logger = logging.getLogger(__name__)


class AssistantState(str, Enum):
    """Estados del asistente de voz"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceResponse:
    """Respuesta del asistente de voz"""
    success: bool
    original_text: str
    intent: Optional[str] = None
    device: Optional[str] = None
    negated: bool = False
    response_text: str = ""
    error: Optional[str] = None
    confidence_note: Optional[str] = None


class ResponseGenerator:
    """Genera respuestas en lenguaje natural para el usuario (ES/EN)"""
    
    RESPONSES_ES = {
        # Respuestas para acciones exitosas
        "turn_on": {
            "normal": [
                "Listo, {device} encendido",
                "He encendido {device}",
                "Encendiendo {device}",
                "{device} activado",
            ],
            "negated": [
                "Entendido, no encenderé {device}",
                "De acuerdo, {device} seguirá apagado",
                "Ok, no activo {device}",
            ]
        },
        "turn_off": {
            "normal": [
                "Listo, {device} apagado",
                "He apagado {device}",
                "Apagando {device}",
                "{device} desactivado",
            ],
            "negated": [
                "Entendido, no apagaré {device}",
                "De acuerdo, {device} seguirá encendido",
                "Ok, dejo {device} activo",
            ]
        },
        "open": {
            "normal": [
                "Abriendo {device}",
                "Listo, {device} abierta",
                "He abierto {device}",
            ],
            "negated": [
                "Entendido, no abriré {device}",
                "De acuerdo, {device} permanecerá cerrada",
            ]
        },
        "close": {
            "normal": [
                "Cerrando {device}",
                "Listo, {device} cerrada",
                "He cerrado {device}",
            ],
            "negated": [
                "Entendido, no cerraré {device}",
                "De acuerdo, {device} permanecerá abierta",
            ]
        },
        "status": {
            "normal": [
                "Consultando estado de {device}",
                "Verificando {device}",
            ],
            "negated": [
                "Entendido, no consultaré el estado",
            ]
        },
        "toggle": {
            "normal": [
                "Cambiando estado de {device}",
                "Alternando {device}",
            ],
            "negated": [
                "Entendido, no cambiaré el estado de {device}",
            ]
        },
        "unknown": {
            "normal": [
                "No entendí el comando. ¿Puedes repetirlo?",
                "Lo siento, no reconocí esa instrucción",
                "¿Podrías decirlo de otra forma?",
            ],
            "negated": [
                "No entendí el comando",
            ]
        },
        # Respuestas de error
        "no_device": [
            "No identifiqué a qué dispositivo te refieres",
            "¿A qué dispositivo quieres que aplique la acción?",
        ],
        "error": [
            "Ocurrió un error al procesar tu solicitud",
            "Lo siento, hubo un problema",
        ],
        # Respuestas del asistente
        "greeting": [
            "¡Hola! ¿En qué puedo ayudarte?",
            "Asistente listo. ¿Qué necesitas?",
        ],
        "goodbye": [
            "¡Hasta luego!",
            "Adiós, que tengas buen día",
        ],
        "listening": [
            "Te escucho",
            "Dime",
        ],
        "no_audio": [
            "No escuché nada. ¿Puedes repetir?",
            "No capté audio. Intenta de nuevo.",
        ],
    }
    
    RESPONSES_EN = {
        # Responses for successful actions
        "turn_on": {
            "normal": [
                "Done, {device} is now on",
                "I've turned on {device}",
                "Turning on {device}",
                "{device} activated",
            ],
            "negated": [
                "Got it, I won't turn on {device}",
                "Okay, {device} will stay off",
                "Understood, not activating {device}",
            ]
        },
        "turn_off": {
            "normal": [
                "Done, {device} is now off",
                "I've turned off {device}",
                "Turning off {device}",
                "{device} deactivated",
            ],
            "negated": [
                "Got it, I won't turn off {device}",
                "Okay, {device} will stay on",
                "Understood, keeping {device} active",
            ]
        },
        "open": {
            "normal": [
                "Opening {device}",
                "Done, {device} is now open",
                "I've opened {device}",
            ],
            "negated": [
                "Got it, I won't open {device}",
                "Okay, {device} will remain closed",
            ]
        },
        "close": {
            "normal": [
                "Closing {device}",
                "Done, {device} is now closed",
                "I've closed {device}",
            ],
            "negated": [
                "Got it, I won't close {device}",
                "Okay, {device} will remain open",
            ]
        },
        "status": {
            "normal": [
                "Checking status of {device}",
                "Verifying {device}",
            ],
            "negated": [
                "Got it, I won't check the status",
            ]
        },
        "toggle": {
            "normal": [
                "Toggling {device}",
                "Switching {device} state",
            ],
            "negated": [
                "Got it, I won't toggle {device}",
            ]
        },
        "unknown": {
            "normal": [
                "I didn't understand that. Could you repeat?",
                "Sorry, I didn't recognize that command",
                "Could you say it differently?",
            ],
            "negated": [
                "I didn't understand the command",
            ]
        },
        # Error responses
        "no_device": [
            "I couldn't identify which device you mean",
            "Which device should I apply that action to?",
        ],
        "error": [
            "An error occurred while processing your request",
            "Sorry, there was a problem",
        ],
        # Assistant responses
        "greeting": [
            "Hello! How can I help you?",
            "Assistant ready. What do you need?",
        ],
        "goodbye": [
            "Goodbye!",
            "See you later!",
        ],
        "listening": [
            "I'm listening",
            "Go ahead",
        ],
        "no_audio": [
            "I didn't hear anything. Could you repeat?",
            "No audio detected. Please try again.",
        ],
    }
    
    # Default language
    _language = "es"
    
    @classmethod
    def set_language(cls, language: str):
        """Set response language ('es' or 'en')"""
        cls._language = language if language in ["es", "en"] else "es"
    
    @classmethod
    def get_responses(cls) -> dict:
        """Get responses for current language"""
        return cls.RESPONSES_EN if cls._language == "en" else cls.RESPONSES_ES
    
    @classmethod
    def generate(
        cls, 
        intent: str, 
        device: Optional[str] = None,
        negated: bool = False,
        category: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta contextual.
        
        Args:
            intent: La intención detectada
            device: El dispositivo (opcional)
            negated: Si el comando fue negado
            category: Categoría especial de respuesta
            language: Idioma ('es' o 'en'), usa el default si None
            
        Returns:
            Texto de respuesta
        """
        import random
        
        # Use specified language or default
        if language:
            responses = cls.RESPONSES_EN if language == "en" else cls.RESPONSES_ES
        else:
            responses = cls.get_responses()
        
        # Categorías especiales
        if category and category in responses:
            return random.choice(responses[category])
        
        # Respuestas por intent
        if intent in responses:
            key = "negated" if negated else "normal"
            intent_responses = responses[intent].get(key, responses[intent]["normal"])
            response = random.choice(intent_responses)
            
            if device:
                # Formatear nombre de dispositivo para speech
                device_formatted = cls._format_device_name(device)
                response = response.format(device=device_formatted)
            
            return response
        
        return "Command processed" if cls._language == "en" else "Comando procesado"
    
    @staticmethod
    def _format_device_name(device_key: str) -> str:
        """Formatea el device_key para que suene natural"""
        # Reemplazar guiones bajos por espacios
        name = device_key.replace("_", " ")
        # Capitalizar primera letra
        return name


class VoiceAssistant:
    """
    Asistente de voz completo para control domótico.
    Integra reconocimiento de voz, procesamiento NLP y síntesis de voz.
    Soporta español e inglés.
    """
    
    def __init__(
        self,
        stt_engine: STTEngine = STTEngine.GOOGLE,
        tts_engine: TTSEngine = TTSEngine.GTTS,
        tts_voice: TTSVoice = TTSVoice.MX_DALIA,
        language: str = "es-ES",
        wake_words: Optional[list] = None,
        nlp_pipeline = None
    ):
        """
        Inicializa el asistente de voz.
        
        Args:
            stt_engine: Motor de reconocimiento de voz
            tts_engine: Motor de síntesis de voz
            tts_voice: Voz a usar para respuestas
            language: Código de idioma para STT (es-ES, en-US, etc.)
            wake_words: Palabras de activación (ej: ["hey casa", "hola casa"])
            nlp_pipeline: Pipeline NLP personalizado (opcional)
        """
        # Detect base language from locale
        self.base_language = "en" if language.startswith("en") else "es"
        
        self.stt = SpeechToText(engine=stt_engine, language=language)
        self.tts = TextToSpeech(engine=tts_engine, voice=tts_voice, language=self.base_language)
        
        # Set wake words based on language
        if wake_words:
            self.wake_words = wake_words
        else:
            self.wake_words = ["home", "assistant", "hey home"] if self.base_language == "en" else ["casa", "asistente", "oye casa"]
        
        self.state = AssistantState.IDLE
        self._nlp_pipeline = nlp_pipeline
        self._running = False
        self._on_state_change: Optional[Callable] = None
        self._on_command: Optional[Callable] = None
        
        # Set response generator language
        ResponseGenerator.set_language(self.base_language)
    
    @property
    def nlp_pipeline(self):
        """Obtiene el pipeline NLP (lazy loading)"""
        if self._nlp_pipeline is None:
            from services.nlp_pipeline import nlp_pipeline
            self._nlp_pipeline = nlp_pipeline
        return self._nlp_pipeline
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[AssistantState], None]] = None,
        on_command: Optional[Callable[[VoiceResponse], None]] = None
    ):
        """
        Configura callbacks para eventos del asistente.
        
        Args:
            on_state_change: Callback cuando cambia el estado
            on_command: Callback cuando se procesa un comando
        """
        self._on_state_change = on_state_change
        self._on_command = on_command
    
    def _set_state(self, new_state: AssistantState):
        """Cambia el estado y notifica"""
        self.state = new_state
        if self._on_state_change:
            self._on_state_change(new_state)
        logger.debug(f"Estado del asistente: {new_state.value}")
    
    async def process_voice_command(
        self,
        timeout: float = 5.0,
        phrase_time_limit: float = 10.0,
        speak_response: bool = True
    ) -> VoiceResponse:
        """
        Escucha un comando de voz y lo procesa.
        
        Args:
            timeout: Tiempo máximo de espera para comenzar
            phrase_time_limit: Duración máxima del comando
            speak_response: Si debe responder por voz
            
        Returns:
            VoiceResponse con el resultado
        """
        # 1. Escuchar
        self._set_state(AssistantState.LISTENING)
        text, error = self.stt.recognize_from_microphone(
            timeout=timeout,
            phrase_time_limit=phrase_time_limit
        )
        
        if error or not text:
            self._set_state(AssistantState.ERROR)
            response = VoiceResponse(
                success=False,
                original_text="",
                error=error or "No se capturó audio",
                response_text=ResponseGenerator.generate(None, category="no_audio")
            )
            if speak_response:
                self.tts.speak(response.response_text)
            return response
        
        # 2. Procesar con NLP
        return await self.process_text_command(text, speak_response)
    
    async def process_text_command(
        self,
        text: str,
        speak_response: bool = True
    ) -> VoiceResponse:
        """
        Procesa un comando de texto.
        
        Args:
            text: Comando en texto
            speak_response: Si debe responder por voz
            
        Returns:
            VoiceResponse con el resultado
        """
        self._set_state(AssistantState.PROCESSING)
        
        try:
            # Interpretar con NLP
            result, confidence_note = await self.nlp_pipeline.interpret(text)
            
            intent = result.get("intent", "unknown")
            device = result.get("device")
            negated = result.get("negated", False)
            
            # Generar respuesta
            if intent == "unknown":
                response_text = ResponseGenerator.generate("unknown")
            elif not device and intent not in ["status"]:
                response_text = ResponseGenerator.generate(None, category="no_device")
            else:
                response_text = ResponseGenerator.generate(intent, device, negated)
            
            response = VoiceResponse(
                success=True,
                original_text=text,
                intent=intent,
                device=device,
                negated=negated,
                response_text=response_text,
                confidence_note=confidence_note
            )
            
        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            response = VoiceResponse(
                success=False,
                original_text=text,
                error=str(e),
                response_text=ResponseGenerator.generate(None, category="error")
            )
        
        # 3. Responder por voz
        if speak_response:
            self._set_state(AssistantState.SPEAKING)
            self.tts.speak(response.response_text)
        
        self._set_state(AssistantState.IDLE)
        
        # Notificar callback
        if self._on_command:
            self._on_command(response)
        
        return response
    
    async def process_audio_bytes(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        is_wav: bool = True,
        speak_response: bool = False
    ) -> VoiceResponse:
        """
        Procesa bytes de audio (útil para API).
        
        Args:
            audio_bytes: Datos de audio
            sample_rate: Frecuencia de muestreo
            is_wav: Si es formato WAV completo
            speak_response: Si debe generar respuesta de voz
            
        Returns:
            VoiceResponse con el resultado
        """
        self._set_state(AssistantState.PROCESSING)
        
        # Reconocer audio
        if is_wav:
            text, error = self.stt.recognize_from_wav_bytes(audio_bytes)
        else:
            text, error = self.stt.recognize_from_audio_data(
                audio_bytes, 
                sample_rate=sample_rate
            )
        
        if error or not text:
            response = VoiceResponse(
                success=False,
                original_text="",
                error=error or "No se pudo reconocer el audio",
                response_text=ResponseGenerator.generate(None, category="no_audio")
            )
            self._set_state(AssistantState.IDLE)
            return response
        
        # Procesar comando
        return await self.process_text_command(text, speak_response)
    
    async def get_response_audio(self, text: str) -> Optional[bytes]:
        """
        Genera audio de respuesta para el texto dado.
        
        Args:
            text: Texto a convertir en audio
            
        Returns:
            Bytes del audio MP3 o None
        """
        return await self.tts.synthesize_to_bytes(text)
    
    def start_continuous_listening(
        self,
        use_wake_word: bool = True,
        on_command: Optional[Callable[[VoiceResponse], None]] = None
    ):
        """
        Inicia escucha continua (modo asistente).
        
        Args:
            use_wake_word: Si debe esperar palabra de activación
            on_command: Callback cuando se procesa un comando
        """
        if on_command:
            self._on_command = on_command
        
        self._running = True
        
        async def listen_loop():
            while self._running:
                try:
                    if use_wake_word:
                        # Esperar wake word
                        logger.info("Esperando palabra de activación...")
                        text, _ = self.stt.recognize_from_microphone(
                            timeout=None,  # Esperar indefinidamente
                            phrase_time_limit=3.0
                        )
                        
                        if text and any(w in text.lower() for w in self.wake_words):
                            # Wake word detectada, escuchar comando
                            self.tts.speak(ResponseGenerator.generate(None, category="listening"))
                            response = await self.process_voice_command()
                        
                    else:
                        # Procesar directamente
                        response = await self.process_voice_command()
                        
                except Exception as e:
                    logger.error(f"Error en loop de escucha: {e}")
                    await asyncio.sleep(1)
        
        asyncio.run(listen_loop())
    
    def stop_listening(self):
        """Detiene la escucha continua"""
        self._running = False
        logger.info("Escucha detenida")
    
    def say(self, text: str) -> bool:
        """
        Hace que el asistente diga algo.
        
        Args:
            text: Texto a pronunciar
            
        Returns:
            True si se reprodujo correctamente
        """
        self._set_state(AssistantState.SPEAKING)
        result = self.tts.speak(text)
        self._set_state(AssistantState.IDLE)
        return result
    
    def greet(self):
        """Saludo del asistente"""
        self.say(ResponseGenerator.generate(None, category="greeting"))
    
    def goodbye(self):
        """Despedida del asistente"""
        self.say(ResponseGenerator.generate(None, category="goodbye"))

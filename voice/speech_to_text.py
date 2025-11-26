"""
Speech-to-Text (STT) - Reconocimiento de voz
Convierte audio a texto usando múltiples backends
"""
import logging
import io
import wave
import tempfile
import os
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class STTEngine(str, Enum):
    """Motores de reconocimiento de voz disponibles"""
    GOOGLE = "google"           # Google Speech Recognition (gratis, online)
    GOOGLE_CLOUD = "google_cloud"  # Google Cloud Speech (API key requerida)
    WHISPER = "whisper"         # OpenAI Whisper (local, offline)
    VOSK = "vosk"               # Vosk (local, offline, ligero)
    SPHINX = "sphinx"           # CMU Sphinx (local, offline)


class SpeechToText:
    """
    Clase para convertir audio a texto.
    Soporta múltiples motores de reconocimiento.
    """
    
    def __init__(self, engine: STTEngine = STTEngine.GOOGLE, language: str = "es-ES"):
        """
        Inicializa el reconocedor de voz.
        
        Args:
            engine: Motor de reconocimiento a usar
            language: Código de idioma (es-ES, es-MX, es-AR)
        """
        self.engine = engine
        self.language = language
        self._recognizer = None
        self._whisper_model = None
        self._vosk_model = None
        
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Inicializa el reconocedor según el motor seleccionado"""
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            
            # Ajustar configuración para mejor reconocimiento en español
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            
            logger.info(f"Reconocedor de voz inicializado con motor: {self.engine}")
            
        except ImportError:
            logger.error("SpeechRecognition no instalado. Ejecuta: pip install SpeechRecognition")
            raise
    
    def _init_whisper(self):
        """Inicializa el modelo Whisper si es necesario"""
        if self._whisper_model is None:
            try:
                import whisper
                # Modelo 'base' es un buen balance entre velocidad y precisión
                # Opciones: tiny, base, small, medium, large
                self._whisper_model = whisper.load_model("base")
                logger.info("Modelo Whisper cargado correctamente")
            except ImportError:
                logger.error("Whisper no instalado. Ejecuta: pip install openai-whisper")
                raise
    
    def _init_vosk(self):
        """Inicializa el modelo Vosk si es necesario"""
        if self._vosk_model is None:
            try:
                from vosk import Model
                import os
                
                # Buscar modelo en directorio local
                model_path = os.environ.get("VOSK_MODEL_PATH", "models/vosk-model-es")
                
                if not os.path.exists(model_path):
                    logger.warning(f"Modelo Vosk no encontrado en {model_path}")
                    logger.info("Descarga un modelo de: https://alphacephei.com/vosk/models")
                    raise FileNotFoundError(f"Modelo Vosk no encontrado: {model_path}")
                
                self._vosk_model = Model(model_path)
                logger.info("Modelo Vosk cargado correctamente")
            except ImportError:
                logger.error("Vosk no instalado. Ejecuta: pip install vosk")
                raise
    
    def recognize_from_microphone(
        self, 
        timeout: float = 5.0,
        phrase_time_limit: float = 10.0
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Escucha del micrófono y convierte a texto.
        
        Args:
            timeout: Tiempo máximo de espera para comenzar a hablar
            phrase_time_limit: Duración máxima de la frase
            
        Returns:
            Tupla (texto_reconocido, error_message)
        """
        import speech_recognition as sr
        
        try:
            with sr.Microphone() as source:
                logger.info("Ajustando al ruido ambiente...")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                logger.info("Escuchando...")
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                return self._process_audio(audio)
                
        except sr.WaitTimeoutError:
            return None, "Timeout: No se detectó voz"
        except Exception as e:
            logger.error(f"Error capturando audio: {e}")
            return None, str(e)
    
    def recognize_from_audio_data(
        self, 
        audio_data: bytes,
        sample_rate: int = 16000,
        sample_width: int = 2
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Reconoce texto desde datos de audio raw.
        
        Args:
            audio_data: Bytes del audio
            sample_rate: Frecuencia de muestreo (Hz)
            sample_width: Ancho de muestra (bytes)
            
        Returns:
            Tupla (texto_reconocido, error_message)
        """
        import speech_recognition as sr
        
        try:
            audio = sr.AudioData(audio_data, sample_rate, sample_width)
            return self._process_audio(audio)
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            return None, str(e)
    
    def recognize_from_wav(self, wav_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Reconoce texto desde un archivo WAV.
        
        Args:
            wav_path: Ruta al archivo WAV
            
        Returns:
            Tupla (texto_reconocido, error_message)
        """
        import speech_recognition as sr
        
        try:
            with sr.AudioFile(wav_path) as source:
                audio = self._recognizer.record(source)
                return self._process_audio(audio)
        except FileNotFoundError:
            return None, f"Archivo no encontrado: {wav_path}"
        except Exception as e:
            logger.error(f"Error leyendo archivo WAV: {e}")
            return None, str(e)
    
    def recognize_from_wav_bytes(self, wav_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
        """
        Reconoce texto desde bytes de un archivo WAV.
        
        Args:
            wav_bytes: Contenido del archivo WAV en bytes
            
        Returns:
            Tupla (texto_reconocido, error_message)
        """
        import speech_recognition as sr
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(wav_bytes)
                tmp_path = tmp.name
            
            try:
                with sr.AudioFile(tmp_path) as source:
                    audio = self._recognizer.record(source)
                    return self._process_audio(audio)
            finally:
                # Limpiar archivo temporal
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"Error procesando bytes WAV: {e}")
            return None, str(e)
    
    def _process_audio(self, audio) -> Tuple[Optional[str], Optional[str]]:
        """
        Procesa el audio usando el motor configurado.
        
        Args:
            audio: Objeto AudioData de SpeechRecognition
            
        Returns:
            Tupla (texto_reconocido, error_message)
        """
        import speech_recognition as sr
        
        try:
            if self.engine == STTEngine.GOOGLE:
                text = self._recognizer.recognize_google(audio, language=self.language)
                
            elif self.engine == STTEngine.GOOGLE_CLOUD:
                # Requiere credenciales de Google Cloud
                credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                text = self._recognizer.recognize_google_cloud(
                    audio, 
                    language=self.language,
                    credentials_json=credentials_json
                )
                
            elif self.engine == STTEngine.WHISPER:
                text = self._recognize_whisper(audio)
                
            elif self.engine == STTEngine.VOSK:
                text = self._recognize_vosk(audio)
                
            elif self.engine == STTEngine.SPHINX:
                # Sphinx no tiene buen soporte para español
                text = self._recognizer.recognize_sphinx(audio)
                
            else:
                return None, f"Motor no soportado: {self.engine}"
            
            logger.info(f"Texto reconocido: {text}")
            return text, None
            
        except sr.UnknownValueError:
            return None, "No se pudo entender el audio"
        except sr.RequestError as e:
            return None, f"Error de servicio: {e}"
        except Exception as e:
            logger.error(f"Error en reconocimiento: {e}")
            return None, str(e)
    
    def _recognize_whisper(self, audio) -> str:
        """Reconoce audio usando Whisper"""
        self._init_whisper()
        
        # Convertir AudioData a archivo temporal WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            tmp_path = tmp.name
        
        try:
            result = self._whisper_model.transcribe(
                tmp_path,
                language="es",
                fp16=False  # Desactivar para CPU
            )
            return result["text"].strip()
        finally:
            os.unlink(tmp_path)
    
    def _recognize_vosk(self, audio) -> str:
        """Reconoce audio usando Vosk"""
        self._init_vosk()
        
        from vosk import KaldiRecognizer
        import json
        
        # Configurar reconocedor
        rec = KaldiRecognizer(self._vosk_model, 16000)
        rec.SetWords(True)
        
        # Procesar audio
        wav_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
        
        # Saltar cabecera WAV (44 bytes)
        rec.AcceptWaveform(wav_data[44:])
        result = json.loads(rec.FinalResult())
        
        return result.get("text", "")
    
    def list_microphones(self) -> list:
        """Lista los micrófonos disponibles"""
        import speech_recognition as sr
        return sr.Microphone.list_microphone_names()
    
    def set_microphone(self, device_index: int):
        """Configura el micrófono a usar por índice"""
        self._mic_device_index = device_index

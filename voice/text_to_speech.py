"""
Text-to-Speech (TTS) - Síntesis de voz
Convierte texto a audio usando múltiples backends
Soporta modo OFFLINE con pyttsx3 o eSpeak
"""
import logging
import io
import os
import tempfile
from typing import Optional, Union
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSEngine(str, Enum):
    """Motores de síntesis de voz disponibles"""
    PYTTSX3 = "pyttsx3"         # Offline, multiplataforma
    GTTS = "gtts"               # Google TTS (online, gratis)
    EDGE_TTS = "edge_tts"       # Microsoft Edge TTS (online, alta calidad)
    ESPEAK = "espeak"           # eSpeak (offline, ligero)
    
    @classmethod
    def get_offline_engines(cls) -> list:
        """Retorna lista de motores que funcionan offline"""
        return [cls.PYTTSX3, cls.ESPEAK]
    
    @classmethod
    def get_online_engines(cls) -> list:
        """Retorna lista de motores que requieren internet"""
        return [cls.GTTS, cls.EDGE_TTS]
    
    @classmethod
    def is_offline(cls, engine: 'TTSEngine') -> bool:
        """Verifica si un motor funciona offline"""
        return engine in cls.get_offline_engines()


class TTSVoice(str, Enum):
    """Voces disponibles para Edge TTS"""
    # Spanish - España
    ES_ALVARO = "es-ES-AlvaroNeural"
    ES_ELVIRA = "es-ES-ElviraNeural"
    # Spanish - México  
    MX_DALIA = "es-MX-DaliaNeural"
    MX_JORGE = "es-MX-JorgeNeural"
    # Spanish - Argentina
    AR_ELENA = "es-AR-ElenaNeural"
    AR_TOMAS = "es-AR-TomasNeural"
    # Spanish - Colombia
    CO_SALOME = "es-CO-SalomeNeural"
    CO_GONZALO = "es-CO-GonzaloNeural"
    # English - US
    EN_US_JENNY = "en-US-JennyNeural"
    EN_US_GUY = "en-US-GuyNeural"
    EN_US_ARIA = "en-US-AriaNeural"
    # English - UK
    EN_GB_SONIA = "en-GB-SoniaNeural"
    EN_GB_RYAN = "en-GB-RyanNeural"
    # English - Australia
    EN_AU_NATASHA = "en-AU-NatashaNeural"
    EN_AU_WILLIAM = "en-AU-WilliamNeural"


class TextToSpeech:
    """
    Clase para convertir texto a voz.
    Soporta múltiples motores de síntesis e idiomas (ES/EN).
    Incluye soporte completo para modo OFFLINE.
    """
    
    def __init__(
        self, 
        engine: TTSEngine = TTSEngine.EDGE_TTS,
        voice: Union[TTSVoice, str] = TTSVoice.MX_DALIA,
        rate: int = 150,
        volume: float = 1.0,
        language: str = "es"
    ):
        """
        Inicializa el sintetizador de voz.
        
        Args:
            engine: Motor de síntesis a usar
            voice: Voz a utilizar (depende del motor)
            rate: Velocidad de habla (palabras por minuto)
            volume: Volumen (0.0 a 1.0)
            language: Idioma ('es' o 'en')
        """
        self.engine = engine
        self.voice = voice.value if isinstance(voice, TTSVoice) else voice
        self.rate = rate
        self.volume = volume
        self.language = language
        self._tts_engine = None
        
        if engine == TTSEngine.PYTTSX3:
            self._init_pyttsx3()
    
    def is_offline_capable(self) -> bool:
        """Verifica si el motor actual puede funcionar sin internet"""
        return TTSEngine.is_offline(self.engine)
    
    def get_engine_info(self) -> dict:
        """Retorna información sobre el motor actual"""
        return {
            "engine": self.engine.value,
            "offline": self.is_offline_capable(),
            "language": self.language,
            "voice": self.voice,
            "rate": self.rate,
            "status": "ready"
        }
    
    def _init_pyttsx3(self):
        """Inicializa el motor pyttsx3 (OFFLINE)"""
        try:
            import pyttsx3
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty('rate', self.rate)
            self._tts_engine.setProperty('volume', self.volume)
            
            # Intentar configurar voz en español o inglés según idioma
            voices = self._tts_engine.getProperty('voices')
            target_lang = 'spanish' if self.language == 'es' else 'english'
            
            for v in voices:
                if target_lang in v.name.lower() or 'español' in v.name.lower():
                    self._tts_engine.setProperty('voice', v.id)
                    logger.info(f"Voz configurada: {v.name}")
                    break
            
            logger.info("✅ Motor pyttsx3 inicializado (OFFLINE)")
        except ImportError:
            logger.error("pyttsx3 no instalado. Ejecuta: pip install pyttsx3")
            raise
        except Exception as e:
            logger.error(f"Error inicializando pyttsx3: {e}")
            raise
    
    def speak(self, text: str) -> bool:
        """
        Reproduce el texto como audio.
        
        Args:
            text: Texto a convertir en voz
            
        Returns:
            True si se reprodujo exitosamente
        """
        if self.engine == TTSEngine.PYTTSX3:
            return self._speak_pyttsx3(text)
        elif self.engine == TTSEngine.GTTS:
            return self._speak_gtts(text)
        elif self.engine == TTSEngine.EDGE_TTS:
            return self._speak_edge_tts(text)
        elif self.engine == TTSEngine.ESPEAK:
            return self._speak_espeak(text)
        else:
            logger.error(f"Motor no soportado: {self.engine}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Reproduce texto usando pyttsx3"""
        try:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Error en pyttsx3: {e}")
            return False
    
    def _speak_gtts(self, text: str) -> bool:
        """Reproduce texto usando Google TTS"""
        try:
            from gtts import gTTS
            import pygame
            
            # Determinar idioma para gTTS
            lang = 'en' if self.language == 'en' else 'es'
            
            # Generar audio
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Guardar en memoria
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Reproducir con pygame
            pygame.mixer.init()
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            return True
            
        except ImportError:
            logger.error("gTTS o pygame no instalado. Ejecuta: pip install gtts pygame")
            return False
        except Exception as e:
            logger.error(f"Error en gTTS: {e}")
            return False
    
    def _speak_edge_tts(self, text: str) -> bool:
        """Reproduce texto usando Microsoft Edge TTS"""
        try:
            import asyncio
            import edge_tts
            import pygame
            
            async def synthesize():
                communicate = edge_tts.Communicate(text, self.voice)
                
                # Guardar en archivo temporal
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp_path = tmp.name
                
                await communicate.save(tmp_path)
                return tmp_path
            
            # Ejecutar síntesis - manejar si ya hay un event loop
            try:
                loop = asyncio.get_running_loop()
                # Ya hay un loop corriendo, usar nest_asyncio o crear tarea
                import nest_asyncio
                nest_asyncio.apply()
                tmp_path = asyncio.run(synthesize())
            except RuntimeError:
                # No hay loop corriendo, usar asyncio.run normal
                tmp_path = asyncio.run(synthesize())
            except ImportError:
                # nest_asyncio no disponible, usar método alternativo
                import threading
                result = [None, None]
                
                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(synthesize())
                        new_loop.close()
                    except Exception as e:
                        result[1] = e
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if result[1]:
                    raise result[1]
                tmp_path = result[0]
            
            try:
                # Reproducir con pygame
                pygame.mixer.init()
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.quit()
            finally:
                # Limpiar archivo temporal
                os.unlink(tmp_path)
            
            return True
            
        except ImportError:
            logger.error("edge-tts o pygame no instalado. Ejecuta: pip install edge-tts pygame")
            return False
        except Exception as e:
            logger.error(f"Error en Edge TTS: {e}")
            return False
    
    def _speak_espeak(self, text: str) -> bool:
        """Reproduce texto usando eSpeak (OFFLINE)"""
        try:
            import subprocess
            # Configurar idioma según preferencia
            lang_code = "en" if self.language == "en" else "es"
            subprocess.run(
                ["espeak", "-v", lang_code, text],
                check=True,
                capture_output=True
            )
            return True
        except FileNotFoundError:
            logger.error("eSpeak no instalado. Instálalo desde: http://espeak.sourceforge.net/")
            logger.error("En Windows: choco install espeak")
            logger.error("En Ubuntu/Debian: sudo apt install espeak")
            return False
        except Exception as e:
            logger.error(f"Error en eSpeak: {e}")
            return False
    
    async def synthesize_to_bytes(self, text: str) -> Optional[bytes]:
        """
        Genera audio y retorna como bytes (MP3 para Edge TTS, WAV para otros).
        Útil para APIs que devuelven audio.
        
        Args:
            text: Texto a sintetizar
            
        Returns:
            Bytes del audio generado o None si falla
        """
        if self.engine == TTSEngine.EDGE_TTS:
            return await self._synthesize_edge_tts_bytes(text)
        elif self.engine == TTSEngine.GTTS:
            return self._synthesize_gtts_bytes(text)
        elif self.engine == TTSEngine.PYTTSX3:
            return self._synthesize_pyttsx3_bytes(text)
        elif self.engine == TTSEngine.ESPEAK:
            return self._synthesize_espeak_bytes(text)
        else:
            logger.error(f"Motor no soporta síntesis a bytes: {self.engine}")
            return None
    
    def _synthesize_espeak_bytes(self, text: str) -> Optional[bytes]:
        """Sintetiza a bytes usando eSpeak (OFFLINE)"""
        try:
            import subprocess
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            lang_code = "en" if self.language == "en" else "es"
            subprocess.run(
                ["espeak", "-v", lang_code, "-w", tmp_path, text],
                check=True,
                capture_output=True
            )
            
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            os.unlink(tmp_path)
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error sintetizando con eSpeak: {e}")
            return None
    
    async def _synthesize_edge_tts_bytes(self, text: str) -> Optional[bytes]:
        """Sintetiza a bytes usando Edge TTS"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(text, self.voice)
            
            # Recopilar chunks de audio
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            
            return b"".join(audio_chunks)
            
        except Exception as e:
            logger.error(f"Error sintetizando con Edge TTS: {e}")
            return None
    
    def _synthesize_gtts_bytes(self, text: str) -> Optional[bytes]:
        """Sintetiza a bytes usando gTTS"""
        try:
            from gtts import gTTS
            
            # Determinar idioma para gTTS
            lang = 'en' if self.language == 'en' else 'es'
            
            tts = gTTS(text=text, lang=lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            return fp.read()
            
        except Exception as e:
            logger.error(f"Error sintetizando con gTTS: {e}")
            return None
    
    def _synthesize_pyttsx3_bytes(self, text: str) -> Optional[bytes]:
        """Sintetiza a bytes usando pyttsx3"""
        try:
            # pyttsx3 no soporta directamente guardar a bytes
            # Guardamos a archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            self._tts_engine.save_to_file(text, tmp_path)
            self._tts_engine.runAndWait()
            
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            os.unlink(tmp_path)
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error sintetizando con pyttsx3: {e}")
            return None
    
    def save_to_file(self, text: str, output_path: str) -> bool:
        """
        Guarda el audio generado a un archivo.
        
        Args:
            text: Texto a sintetizar
            output_path: Ruta del archivo de salida
            
        Returns:
            True si se guardó exitosamente
        """
        import asyncio
        
        try:
            if self.engine == TTSEngine.EDGE_TTS:
                async def save():
                    import edge_tts
                    communicate = edge_tts.Communicate(text, self.voice)
                    await communicate.save(output_path)
                asyncio.run(save())
                
            elif self.engine == TTSEngine.GTTS:
                from gtts import gTTS
                lang = 'en' if self.language == 'en' else 'es'
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(output_path)
                
            elif self.engine == TTSEngine.PYTTSX3:
                self._tts_engine.save_to_file(text, output_path)
                self._tts_engine.runAndWait()
            
            else:
                logger.error(f"Motor no soporta guardar a archivo: {self.engine}")
                return False
            
            logger.info(f"Audio guardado en: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando audio: {e}")
            return False
    
    @staticmethod
    def list_edge_voices(language: str = "es") -> list:
        """
        Lista las voces disponibles de Edge TTS.
        
        Args:
            language: Filtrar por código de idioma (es, en, etc.)
            
        Returns:
            Lista de voces disponibles
        """
        import asyncio
        import edge_tts
        
        async def get_voices():
            voices = await edge_tts.list_voices()
            if language:
                voices = [v for v in voices if v["Locale"].startswith(language)]
            return voices
        
        return asyncio.run(get_voices())
    
    def list_pyttsx3_voices(self) -> list:
        """Lista las voces disponibles de pyttsx3"""
        if self._tts_engine:
            return self._tts_engine.getProperty('voices')
        return []
    
    @classmethod
    def create_offline_instance(cls, language: str = "es", engine: str = "pyttsx3", rate: int = 150) -> 'TextToSpeech':
        """
        Crea una instancia configurada para modo offline.
        
        Args:
            language: Idioma ('es' o 'en')
            engine: "pyttsx3" o "espeak"
            rate: Velocidad de habla
            
        Returns:
            Instancia de TextToSpeech configurada para offline
        """
        engine_enum = TTSEngine.PYTTSX3 if engine.lower() == "pyttsx3" else TTSEngine.ESPEAK
        return cls(
            engine=engine_enum,
            language=language,
            rate=rate
        )

#!/usr/bin/env python3
"""
🏠 Smart Home NLP Engine - Interactive Runner
==============================================
Ejecuta el asistente domótico completo con:
- Modo texto: Escribe comandos y recibe respuestas por voz
- Modo voz: Habla y recibe respuestas por voz
- Servidor API: Inicia el servidor FastAPI

Uso:
    python run.py              # Menú interactivo
    python run.py --text       # Solo modo texto
    python run.py --voice      # Solo modo voz
    python run.py --server     # Solo servidor API
"""

import sys
import os
import asyncio
import argparse
import logging
from typing import Optional

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Muestra el banner de bienvenida"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║   {Colors.BOLD}🏠 Smart Home NLP Engine{Colors.ENDC}{Colors.CYAN}                                  ║
║   {Colors.GREEN}Bilingual Voice Controller (ES/EN){Colors.CYAN}                         ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def print_menu():
    """Muestra el menú principal"""
    menu = f"""
{Colors.YELLOW}Selecciona un modo:{Colors.ENDC}

  {Colors.BOLD}1{Colors.ENDC}) 📝 Modo Texto     - Escribe comandos, respuestas por voz
  {Colors.BOLD}2{Colors.ENDC}) 🎤 Modo Voz       - Habla comandos, respuestas por voz  
  {Colors.BOLD}3{Colors.ENDC}) 🔄 Modo Completo  - Texto + Voz simultáneo
  {Colors.BOLD}4{Colors.ENDC}) 🌐 Servidor API   - Iniciar FastAPI en puerto 8001
  {Colors.BOLD}5{Colors.ENDC}) ⚙️  Configuración  - Cambiar idioma y voz
  {Colors.BOLD}0{Colors.ENDC}) 🚪 Salir

{Colors.CYAN}Idiomas soportados:{Colors.ENDC}
  🇪🇸 Español: "enciende la luz", "apaga el ventilador"
  🇺🇸 English: "turn on the light", "turn off the fan"
"""
    print(menu)


class SmartHomeAssistant:
    """Asistente domótico integrado con NLP y voz"""
    
    def __init__(self, language: str = "es"):
        self.language = language
        self.voice_assistant = None
        self.nlp_pipeline = None
        self._initialized = False
    
    async def initialize(self):
        """Inicializa los componentes"""
        if self._initialized:
            return
        
        print(f"\n{Colors.YELLOW}⏳ Inicializando componentes...{Colors.ENDC}")
        
        try:
            # Importar componentes
            from config.settings import settings
            from services.nlp_pipeline import nlp_pipeline
            from voice.voice_assistant import VoiceAssistant, ResponseGenerator
            from voice.text_to_speech import TTSEngine, TTSVoice
            from voice.speech_to_text import STTEngine
            
            self.nlp_pipeline = nlp_pipeline
            
            # Configurar idioma
            stt_lang = "en-US" if self.language == "en" else settings.VOICE_LANGUAGE
            tts_voice = TTSVoice.EN_US_JENNY if self.language == "en" else settings.TTS_VOICE
            
            # Mapear configuración de settings a enums
            stt_engine_map = {
                "google": STTEngine.GOOGLE,
                "google_cloud": STTEngine.GOOGLE_CLOUD,
                "whisper": STTEngine.WHISPER,
                "vosk": STTEngine.VOSK,
                "sphinx": STTEngine.SPHINX,
            }
            
            tts_engine_map = {
                "edge_tts": TTSEngine.EDGE_TTS,
                "gtts": TTSEngine.GTTS,
                "pyttsx3": TTSEngine.PYTTSX3,
                "espeak": TTSEngine.ESPEAK,
            }
            
            # Usar configuración de settings.py (que lee de .env)
            stt_engine = stt_engine_map.get(settings.STT_ENGINE.lower(), STTEngine.GOOGLE)
            tts_engine = tts_engine_map.get(settings.TTS_ENGINE.lower(), TTSEngine.GTTS)
            
            # Crear asistente de voz con configuración de .env
            self.voice_assistant = VoiceAssistant(
                stt_engine=stt_engine,
                tts_engine=tts_engine,
                tts_voice=tts_voice,
                language=stt_lang,
                nlp_pipeline=nlp_pipeline,
                offline_mode=settings.OFFLINE_MODE,
                whisper_model=settings.WHISPER_MODEL,
                vosk_model_path=settings.VOSK_MODEL_PATH
            )
            
            # Configurar idioma de respuestas
            ResponseGenerator.set_language(self.language)
            
            self._initialized = True
            
            # Mostrar modo activo
            mode = "OFFLINE 🔌" if settings.OFFLINE_MODE else "ONLINE 🌐"
            print(f"{Colors.GREEN}✅ Componentes inicializados ({mode}){Colors.ENDC}")
            print(f"{Colors.CYAN}   Idioma: {'English' if self.language == 'en' else 'Español'}{Colors.ENDC}")
            print(f"{Colors.CYAN}   STT: {settings.STT_ENGINE} (offline: {self.voice_assistant.stt.is_offline_capable()}){Colors.ENDC}")
            print(f"{Colors.CYAN}   TTS: {settings.TTS_ENGINE} (offline: {self.voice_assistant.tts.is_offline_capable()}){Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error inicializando: {e}{Colors.ENDC}")
            raise
    
    def set_language(self, language: str):
        """Cambia el idioma del asistente"""
        self.language = language
        self._initialized = False  # Forzar reinicialización
    
    async def process_text(self, text: str, speak: bool = True) -> dict:
        """
        Procesa un comando de texto y responde por voz.
        
        Args:
            text: Comando en texto
            speak: Si debe responder por voz
            
        Returns:
            Diccionario con el resultado
        """
        await self.initialize()
        
        response = await self.voice_assistant.process_text_command(text, speak_response=speak)
        
        return {
            "success": response.success,
            "text": response.original_text,
            "intent": response.intent,
            "device": response.device,
            "negated": response.negated,
            "response": response.response_text,
            "error": response.error
        }
    
    async def process_voice(self, speak: bool = True) -> dict:
        """
        Escucha un comando de voz y responde por voz.
        
        Args:
            speak: Si debe responder por voz
            
        Returns:
            Diccionario con el resultado
        """
        await self.initialize()
        
        print(f"\n{Colors.CYAN}🎤 Escuchando... (habla ahora){Colors.ENDC}")
        
        response = await self.voice_assistant.process_voice_command(
            timeout=5.0,
            phrase_time_limit=8.0,
            speak_response=speak
        )
        
        return {
            "success": response.success,
            "text": response.original_text,
            "intent": response.intent,
            "device": response.device,
            "negated": response.negated,
            "response": response.response_text,
            "error": response.error
        }
    
    def speak(self, text: str):
        """Sintetiza y reproduce texto por voz"""
        if self.voice_assistant:
            self.voice_assistant.tts.speak(text)


def print_result(result: dict):
    """Muestra el resultado de forma bonita"""
    if result["success"]:
        print(f"\n{Colors.GREEN}✅ Comando procesado:{Colors.ENDC}")
        print(f"   📝 Texto: {result['text']}")
        print(f"   🎯 Intent: {Colors.BOLD}{result['intent']}{Colors.ENDC}")
        if result['device']:
            print(f"   📱 Dispositivo: {result['device']}")
        if result['negated']:
            print(f"   ⛔ Negado: {Colors.RED}Sí{Colors.ENDC}")
        print(f"   💬 Respuesta: {Colors.CYAN}{result['response']}{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}❌ Error: {result.get('error', 'Unknown error')}{Colors.ENDC}")


async def text_mode(assistant: SmartHomeAssistant):
    """Modo de entrada por texto con respuesta por voz"""
    print(f"\n{Colors.HEADER}═══ MODO TEXTO ═══{Colors.ENDC}")
    print(f"{Colors.YELLOW}Escribe comandos en español o inglés.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Escribe 'salir' o 'exit' para volver al menú.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Escribe 'lang es' o 'lang en' para cambiar idioma.{Colors.ENDC}\n")
    
    await assistant.initialize()
    
    # Mensaje de bienvenida por voz
    welcome = "Ready. Tell me what to do." if assistant.language == "en" else "Listo. Dime qué hacer."
    assistant.speak(welcome)
    
    while True:
        try:
            prompt = f"{Colors.GREEN}Tú>{Colors.ENDC} " if assistant.language == "es" else f"{Colors.GREEN}You>{Colors.ENDC} "
            text = input(prompt).strip()
            
            if not text:
                continue
            
            # Comandos especiales
            if text.lower() in ['salir', 'exit', 'quit', 'q']:
                goodbye = "See you later!" if assistant.language == "en" else "¡Hasta luego!"
                assistant.speak(goodbye)
                break
            
            if text.lower().startswith('lang '):
                new_lang = text.split()[1].lower()
                if new_lang in ['es', 'en']:
                    assistant.set_language(new_lang)
                    await assistant.initialize()
                    msg = f"Language changed to {'English' if new_lang == 'en' else 'Spanish'}"
                    print(f"{Colors.CYAN}{msg}{Colors.ENDC}")
                    assistant.speak(msg if new_lang == 'en' else "Idioma cambiado a español")
                continue
            
            # Procesar comando
            result = await assistant.process_text(text, speak=True)
            print_result(result)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrumpido.{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")


async def voice_mode(assistant: SmartHomeAssistant):
    """Modo de entrada por voz con respuesta por voz"""
    print(f"\n{Colors.HEADER}═══ MODO VOZ ═══{Colors.ENDC}")
    print(f"{Colors.YELLOW}Habla comandos en español o inglés.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Di 'salir' o 'exit' para volver al menú.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Presiona Ctrl+C para interrumpir.{Colors.ENDC}\n")
    
    await assistant.initialize()
    
    # Mensaje de bienvenida
    welcome = "Voice mode activated. I'm listening." if assistant.language == "en" else "Modo voz activado. Te escucho."
    assistant.speak(welcome)
    
    while True:
        try:
            result = await assistant.process_voice(speak=True)
            
            if result["success"]:
                print_result(result)
                
                # Verificar comando de salida
                text_lower = (result["text"] or "").lower()
                if any(word in text_lower for word in ['salir', 'exit', 'quit', 'terminar', 'stop']):
                    goodbye = "See you later!" if assistant.language == "en" else "¡Hasta luego!"
                    assistant.speak(goodbye)
                    break
            else:
                print(f"{Colors.YELLOW}⚠️ No se entendió. Intenta de nuevo.{Colors.ENDC}")
            
            # Pequeña pausa entre comandos
            await asyncio.sleep(0.5)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrumpido.{Colors.ENDC}")
            goodbye = "See you!" if assistant.language == "en" else "¡Hasta luego!"
            assistant.speak(goodbye)
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")


async def full_mode(assistant: SmartHomeAssistant):
    """Modo completo: texto y voz disponibles"""
    print(f"\n{Colors.HEADER}═══ MODO COMPLETO ═══{Colors.ENDC}")
    print(f"{Colors.YELLOW}Opciones:{Colors.ENDC}")
    print(f"  - Escribe un comando y presiona Enter")
    print(f"  - Escribe 'v' o 'voice' para hablar un comando")
    print(f"  - Escribe 'salir' o 'exit' para volver\n")
    
    await assistant.initialize()
    
    welcome = "Ready. Write or speak your command." if assistant.language == "en" else "Listo. Escribe o habla tu comando."
    assistant.speak(welcome)
    
    while True:
        try:
            prompt = f"{Colors.GREEN}[texto/v]>{Colors.ENDC} "
            text = input(prompt).strip()
            
            if not text:
                continue
            
            if text.lower() in ['salir', 'exit', 'quit', 'q']:
                goodbye = "Goodbye!" if assistant.language == "en" else "¡Adiós!"
                assistant.speak(goodbye)
                break
            
            if text.lower() in ['v', 'voice', 'voz']:
                result = await assistant.process_voice(speak=True)
            elif text.lower().startswith('lang '):
                new_lang = text.split()[1].lower()
                if new_lang in ['es', 'en']:
                    assistant.set_language(new_lang)
                    await assistant.initialize()
                    msg = "Language changed" if new_lang == 'en' else "Idioma cambiado"
                    print(f"{Colors.CYAN}{msg}{Colors.ENDC}")
                    assistant.speak(msg)
                continue
            else:
                result = await assistant.process_text(text, speak=True)
            
            print_result(result)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrumpido.{Colors.ENDC}")
            break


def run_server():
    """Inicia el servidor FastAPI"""
    print(f"\n{Colors.HEADER}═══ SERVIDOR API ═══{Colors.ENDC}")
    print(f"{Colors.CYAN}Iniciando servidor en http://localhost:8001{Colors.ENDC}")
    print(f"{Colors.CYAN}Documentación: http://localhost:8001/docs{Colors.ENDC}")
    print(f"{Colors.YELLOW}Presiona Ctrl+C para detener.{Colors.ENDC}\n")
    
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )


async def configuration_menu(assistant: SmartHomeAssistant) -> bool:
    """Menú de configuración"""
    print(f"\n{Colors.HEADER}═══ CONFIGURACIÓN ═══{Colors.ENDC}")
    print(f"\n{Colors.YELLOW}Idioma actual: {'English' if assistant.language == 'en' else 'Español'}{Colors.ENDC}")
    print(f"\n  1) 🇪🇸 Español")
    print(f"  2) 🇺🇸 English")
    print(f"  0) Volver\n")
    
    choice = input(f"{Colors.GREEN}Opción>{Colors.ENDC} ").strip()
    
    if choice == "1":
        assistant.set_language("es")
        print(f"{Colors.GREEN}✅ Idioma cambiado a Español{Colors.ENDC}")
    elif choice == "2":
        assistant.set_language("en")
        print(f"{Colors.GREEN}✅ Language changed to English{Colors.ENDC}")
    
    return True


async def main_menu():
    """Menú principal interactivo"""
    print_banner()
    
    assistant = SmartHomeAssistant(language="es")
    
    while True:
        print_menu()
        choice = input(f"{Colors.GREEN}Opción>{Colors.ENDC} ").strip()
        
        try:
            if choice == "1":
                await text_mode(assistant)
            elif choice == "2":
                await voice_mode(assistant)
            elif choice == "3":
                await full_mode(assistant)
            elif choice == "4":
                run_server()
            elif choice == "5":
                await configuration_menu(assistant)
            elif choice == "0":
                print(f"\n{Colors.CYAN}👋 ¡Hasta pronto!{Colors.ENDC}\n")
                break
            else:
                print(f"{Colors.RED}Opción no válida{Colors.ENDC}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Volviendo al menú...{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
            logger.exception("Error en menú principal")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description="🏠 Smart Home NLP Engine - Bilingual Voice Controller"
    )
    parser.add_argument(
        "--text", "-t", 
        action="store_true", 
        help="Iniciar directamente en modo texto"
    )
    parser.add_argument(
        "--voice", "-v", 
        action="store_true", 
        help="Iniciar directamente en modo voz"
    )
    parser.add_argument(
        "--server", "-s", 
        action="store_true", 
        help="Iniciar servidor API"
    )
    parser.add_argument(
        "--lang", "-l",
        choices=["es", "en"],
        default="es",
        help="Idioma inicial (es=español, en=english)"
    )
    
    args = parser.parse_args()
    
    if args.server:
        print_banner()
        run_server()
    elif args.text:
        print_banner()
        assistant = SmartHomeAssistant(language=args.lang)
        asyncio.run(text_mode(assistant))
    elif args.voice:
        print_banner()
        assistant = SmartHomeAssistant(language=args.lang)
        asyncio.run(voice_mode(assistant))
    else:
        asyncio.run(main_menu())


if __name__ == "__main__":
    main()

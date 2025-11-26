#!/usr/bin/env python3
"""
Demo de Control por Voz para Smart Home NLP
============================================

Este script demuestra el uso del asistente de voz para controlar
dispositivos del hogar inteligente usando comandos de voz.

Requisitos:
-----------
1. Instalar dependencias:
   pip install SpeechRecognition PyAudio edge-tts pygame

2. Tener un micrófono conectado

3. (Opcional) Tener el servidor NLP corriendo:
   python main.py

Uso:
----
python examples/voice_demo.py [--mode MODE]

Modos:
- interactive: Control por voz en tiempo real (default)
- test_tts: Prueba solo síntesis de voz
- test_stt: Prueba solo reconocimiento de voz
- api: Usa la API HTTP en lugar de módulo local
"""

import sys
import os
import asyncio
import argparse

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_banner():
    """Imprime el banner del demo"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🏠 SMART HOME - Control por Voz                           ║
║                                                              ║
║   Comandos de ejemplo:                                       ║
║   • "Enciende la luz del comedor"                           ║
║   • "Apaga el ventilador"                                   ║
║   • "Abre la puerta del garage"                             ║
║   • "¿Cómo está la alarma?"                                 ║
║   • "No enciendas la luz" (negación)                        ║
║                                                              ║
║   Presiona Ctrl+C para salir                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    missing = []
    
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    
    try:
        import edge_tts
    except ImportError:
        missing.append("edge-tts")
    
    try:
        import pygame
    except ImportError:
        missing.append("pygame")
    
    # PyAudio es especial
    try:
        import pyaudio
    except ImportError:
        missing.append("PyAudio")
    
    if missing:
        print("❌ Dependencias faltantes:")
        print(f"   pip install {' '.join(missing)}")
        print()
        if "PyAudio" in missing:
            print("   Nota: En Windows, PyAudio puede requerir:")
            print("   pip install pipwin")
            print("   pipwin install pyaudio")
        return False
    
    print("✅ Todas las dependencias instaladas")
    return True


async def test_tts():
    """Prueba la síntesis de voz"""
    print("\n🔊 Probando Text-to-Speech...\n")
    
    from voice.text_to_speech import TextToSpeech, TTSEngine, TTSVoice
    
    tts = TextToSpeech(
        engine=TTSEngine.GTTS,  # Usar gTTS que es más estable
        voice=TTSVoice.MX_DALIA
    )
    
    frases = [
        "Hola, soy tu asistente de hogar inteligente",
        "Luz del comedor encendida",
        "Entendido, no apagaré el ventilador",
        "¿En qué más puedo ayudarte?"
    ]
    
    for frase in frases:
        print(f"   Diciendo: \"{frase}\"")
        tts.speak(frase)
        await asyncio.sleep(0.5)
    
    print("\n✅ TTS funcionando correctamente")


def test_stt():
    """Prueba el reconocimiento de voz"""
    print("\n🎤 Probando Speech-to-Text...\n")
    
    from voice.speech_to_text import SpeechToText, STTEngine
    
    stt = SpeechToText(engine=STTEngine.GOOGLE, language="es-ES")
    
    # Listar micrófonos
    print("   Micrófonos disponibles:")
    for i, mic in enumerate(stt.list_microphones()):
        print(f"   [{i}] {mic}")
    print()
    
    print("   🎤 Di algo (tienes 5 segundos)...")
    text, error = stt.recognize_from_microphone(timeout=5, phrase_time_limit=5)
    
    if text:
        print(f"\n   ✅ Reconocido: \"{text}\"")
    else:
        print(f"\n   ❌ Error: {error}")


async def interactive_mode():
    """Modo interactivo de control por voz"""
    print_banner()
    
    from voice import VoiceAssistant
    from voice.speech_to_text import STTEngine
    from voice.text_to_speech import TTSEngine, TTSVoice
    from voice.voice_assistant import AssistantState
    
    # Crear asistente con gTTS (más estable que Edge TTS)
    assistant = VoiceAssistant(
        stt_engine=STTEngine.GOOGLE,
        tts_engine=TTSEngine.GTTS,
        language="es-ES"
    )
    
    # Callback para mostrar estado
    def on_state_change(state: AssistantState):
        icons = {
            AssistantState.IDLE: "💤",
            AssistantState.LISTENING: "🎤",
            AssistantState.PROCESSING: "🧠",
            AssistantState.SPEAKING: "🔊",
            AssistantState.ERROR: "❌"
        }
        print(f"\r   Estado: {icons.get(state, '❓')} {state.value}          ", end="")
    
    assistant.set_callbacks(on_state_change=on_state_change)
    
    # Saludo inicial
    print("\n🤖 Iniciando asistente de voz...\n")
    assistant.greet()
    
    print("\n" + "─" * 60)
    print("   Presiona ENTER para dar un comando de voz")
    print("   Escribe 'salir' para terminar")
    print("─" * 60 + "\n")
    
    try:
        while True:
            user_input = input("\n   → ").strip().lower()
            
            if user_input in ['salir', 'exit', 'quit', 'q']:
                assistant.goodbye()
                print("\n👋 ¡Hasta luego!\n")
                break
            
            # Procesar comando de voz
            print()
            response = await assistant.process_voice_command(
                timeout=5,
                phrase_time_limit=8,
                speak_response=True
            )
            
            # Mostrar resultado
            print(f"\n\n   {'─' * 50}")
            print(f"   📝 Texto: \"{response.original_text}\"")
            if response.success:
                print(f"   🎯 Intent: {response.intent}")
                print(f"   📱 Device: {response.device or 'N/A'}")
                print(f"   🚫 Negado: {'Sí' if response.negated else 'No'}")
            else:
                print(f"   ❌ Error: {response.error}")
            print(f"   💬 Respuesta: \"{response.response_text}\"")
            print(f"   {'─' * 50}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...\n")


async def api_mode():
    """Modo usando la API HTTP"""
    import httpx
    import tempfile
    import wave
    
    print("\n🌐 Modo API - Conectando a http://localhost:8001\n")
    
    # Verificar conexión
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=5)
            if response.status_code != 200:
                print("❌ El servidor no está respondiendo")
                print("   Inicia el servidor con: python main.py")
                return
            print("✅ Servidor conectado\n")
    except Exception as e:
        print(f"❌ No se pudo conectar al servidor: {e}")
        print("   Inicia el servidor con: python main.py")
        return
    
    # Verificar estado del módulo de voz
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/voice/status")
        status = response.json()
        if not status.get("operational"):
            print(f"⚠️  Módulo de voz no completamente operativo")
            print(f"   {status.get('message', '')}\n")
    
    from voice.speech_to_text import SpeechToText, STTEngine
    
    stt = SpeechToText(engine=STTEngine.GOOGLE, language="es-ES")
    
    print("─" * 60)
    print("   Presiona ENTER para dar un comando de voz")
    print("   Escribe 'salir' para terminar")
    print("─" * 60 + "\n")
    
    try:
        while True:
            user_input = input("\n   → ").strip().lower()
            
            if user_input in ['salir', 'exit', 'quit', 'q']:
                print("\n👋 ¡Hasta luego!\n")
                break
            
            # Capturar audio
            print("\n   🎤 Escuchando...")
            
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    print("   ❌ No se detectó audio")
                    continue
            
            # Guardar como WAV temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio.get_wav_data())
                tmp_path = tmp.name
            
            try:
                # Enviar a la API
                print("   🧠 Procesando...")
                
                async with httpx.AsyncClient() as client:
                    with open(tmp_path, "rb") as f:
                        files = {"audio": ("comando.wav", f, "audio/wav")}
                        response = await client.post(
                            "http://localhost:8001/voice/interpret",
                            files=files,
                            timeout=30
                        )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"\n   {'─' * 50}")
                    print(f"   📝 Texto: \"{result['original_text']}\"")
                    print(f"   🎯 Intent: {result['intent']}")
                    print(f"   📱 Device: {result['device'] or 'N/A'}")
                    print(f"   🚫 Negado: {'Sí' if result['negated'] else 'No'}")
                    print(f"   💬 Respuesta: \"{result['response_text']}\"")
                    print(f"   {'─' * 50}")
                    
                    # Reproducir respuesta de voz
                    from voice.text_to_speech import TextToSpeech, TTSEngine, TTSVoice
                    tts = TextToSpeech(engine=TTSEngine.EDGE_TTS, voice=TTSVoice.MX_DALIA)
                    tts.speak(result['response_text'])
                    
                else:
                    print(f"   ❌ Error de API: {response.status_code}")
                    print(f"   {response.text}")
                    
            finally:
                os.unlink(tmp_path)
                
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...\n")


def main():
    parser = argparse.ArgumentParser(
        description="Demo de Control por Voz para Smart Home NLP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python voice_demo.py                    # Modo interactivo (default)
  python voice_demo.py --mode test_tts    # Probar síntesis de voz
  python voice_demo.py --mode test_stt    # Probar reconocimiento de voz
  python voice_demo.py --mode api         # Usar API HTTP
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["interactive", "test_tts", "test_stt", "api"],
        default="interactive",
        help="Modo de ejecución"
    )
    
    args = parser.parse_args()
    
    print("\n🏠 Smart Home NLP - Demo de Control por Voz\n")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Ejecutar modo seleccionado
    if args.mode == "interactive":
        asyncio.run(interactive_mode())
    elif args.mode == "test_tts":
        asyncio.run(test_tts())
    elif args.mode == "test_stt":
        test_stt()
    elif args.mode == "api":
        asyncio.run(api_mode())


if __name__ == "__main__":
    main()

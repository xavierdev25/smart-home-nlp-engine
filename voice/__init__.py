"""
Módulo de control por voz para el sistema domótico
Incluye STT (Speech-to-Text) y TTS (Text-to-Speech)
"""
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .voice_assistant import VoiceAssistant

__all__ = ["SpeechToText", "TextToSpeech", "VoiceAssistant"]

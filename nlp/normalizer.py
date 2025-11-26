"""
Normalizador de Texto
=====================

Procesa y normaliza texto en español para mejorar el matching NLP.
Incluye eliminación de acentos, normalización de espacios, etc.
"""
import re
import unicodedata
from typing import List, Optional


class TextNormalizer:
    """
    Normaliza texto en español para procesamiento NLP.
    
    Operaciones:
    - Conversión a minúsculas
    - Eliminación de acentos (opcional)
    - Normalización de espacios
    - Eliminación de signos de puntuación no relevantes
    - Corrección de errores comunes de escritura
    """
    
    # Mapeo de caracteres especiales a su forma normalizada
    CHAR_REPLACEMENTS = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        # Mantener ñ como carácter especial pero normalizado
        'ñ': 'ñ',
    }
    
    # Errores comunes de escritura/tipeo en español
    COMMON_TYPOS = {
        'ensender': 'encender',
        'ensendido': 'encendido',
        'apagado ': 'apagado',
        'presder': 'prender',
        'preder': 'prender',
        'abier': 'abrir',
        'cerarr': 'cerrar',
        'lus': 'luz',
        'puertta': 'puerta',
        'ventanna': 'ventana',
        'cocinaa': 'cocina',
        'cuuarto': 'cuarto',
        'dormitiorio': 'dormitorio',
        'habiitacion': 'habitacion',
        'vanio': 'baño',
        'bano': 'baño',
        'cala': 'sala',
        'slaa': 'sala',
    }
    
    # Contracciones y formas coloquiales
    COLLOQUIAL_FORMS = {
        "porfa": "por favor",
        "porfavor": "por favor",
        "xfa": "por favor",
        "xfavor": "por favor",
        "q": "que",
        "k": "que",
        "xq": "porque",
        "pq": "porque",
        "tb": "también",
        "tmb": "también",
        "x": "por",
        "d": "de",
        "dl": "del",
        "pa": "para",
        "pal": "para el",
        "toy": "estoy",
        "ta": "está",
        "tan": "están",
    }
    
    def __init__(self, 
                 remove_accents: bool = True,
                 fix_typos: bool = True,
                 expand_colloquial: bool = True,
                 preserve_numbers: bool = True):
        """
        Inicializa el normalizador.
        
        Args:
            remove_accents: Si True, elimina acentos (excepto ñ)
            fix_typos: Si True, corrige errores comunes
            expand_colloquial: Si True, expande formas coloquiales
            preserve_numbers: Si True, preserva números en el texto
        """
        self.remove_accents = remove_accents
        self.fix_typos = fix_typos
        self.expand_colloquial = expand_colloquial
        self.preserve_numbers = preserve_numbers
    
    def normalize(self, text: str) -> str:
        """
        Normaliza el texto aplicando todas las transformaciones configuradas.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
        
        # 1. Convertir a minúsculas
        result = text.lower()
        
        # 2. Normalizar espacios y saltos de línea
        result = self._normalize_whitespace(result)
        
        # 3. Eliminar puntuación no relevante (preservar algunos)
        result = self._remove_punctuation(result)
        
        # 4. Expandir formas coloquiales
        if self.expand_colloquial:
            result = self._expand_colloquial(result)
        
        # 5. Corregir errores comunes
        if self.fix_typos:
            result = self._fix_typos(result)
        
        # 6. Eliminar acentos
        if self.remove_accents:
            result = self._remove_accents(result)
        
        # 7. Normalización final de espacios
        result = self._normalize_whitespace(result)
        
        return result.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espacios múltiples y saltos de línea"""
        # Reemplazar saltos de línea y tabs por espacios
        text = re.sub(r'[\n\r\t]+', ' ', text)
        # Reemplazar espacios múltiples por uno solo
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _remove_punctuation(self, text: str) -> str:
        """Elimina puntuación no relevante, preservando algunos caracteres"""
        # Preservar: letras, números, espacios, ñ
        # Eliminar: signos de puntuación, símbolos especiales
        
        # Primero, reemplazar signos de interrogación/exclamación con espacio
        text = re.sub(r'[¿?¡!]+', ' ', text)
        
        # Eliminar otros signos de puntuación
        text = re.sub(r'[.,;:\'"()\[\]{}«»""''—–-]+', ' ', text)
        
        # Preservar % si está junto a un número
        if not self.preserve_numbers:
            text = re.sub(r'%', '', text)
        
        return text
    
    def _expand_colloquial(self, text: str) -> str:
        """Expande formas coloquiales a su forma completa"""
        words = text.split()
        expanded = []
        
        for word in words:
            # Buscar en el diccionario de formas coloquiales
            if word in self.COLLOQUIAL_FORMS:
                expanded.append(self.COLLOQUIAL_FORMS[word])
            else:
                expanded.append(word)
        
        return ' '.join(expanded)
    
    def _fix_typos(self, text: str) -> str:
        """Corrige errores de escritura comunes"""
        for typo, correction in self.COMMON_TYPOS.items():
            text = text.replace(typo, correction)
        return text
    
    def _remove_accents(self, text: str) -> str:
        """
        Elimina acentos del texto usando normalización Unicode.
        Preserva la ñ.
        """
        # Preservar ñ temporalmente
        text = text.replace('ñ', '__ENE__')
        text = text.replace('Ñ', '__ENE__')
        
        # Normalizar y eliminar marcas de acento
        nfkd_form = unicodedata.normalize('NFKD', text)
        result = ''.join(
            char for char in nfkd_form 
            if not unicodedata.combining(char)
        )
        
        # Restaurar ñ
        result = result.replace('__ENE__', 'ñ')
        
        return result
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza el texto en palabras individuales.
        
        Args:
            text: Texto a tokenizar
            
        Returns:
            Lista de tokens/palabras
        """
        # Primero normalizar
        normalized = self.normalize(text)
        
        # Dividir por espacios
        tokens = normalized.split()
        
        # Filtrar tokens vacíos
        return [t for t in tokens if t]
    
    def extract_numbers(self, text: str) -> List[str]:
        """
        Extrae números del texto.
        
        Args:
            text: Texto a procesar
            
        Returns:
            Lista de números encontrados (como strings)
        """
        # Buscar números con posible símbolo de porcentaje
        pattern = r'\d+(?:\.\d+)?(?:\s*%)?'
        return re.findall(pattern, text)
    
    def remove_stopwords(self, text: str, stopwords: Optional[List[str]] = None) -> str:
        """
        Elimina palabras vacías (stopwords) del texto.
        
        Args:
            text: Texto a procesar
            stopwords: Lista de stopwords (usa default si None)
            
        Returns:
            Texto sin stopwords
        """
        if stopwords is None:
            from .constants import NLPConstants
            stopwords = NLPConstants.STOPWORDS
        
        words = text.split()
        filtered = [w for w in words if w.lower() not in stopwords]
        return ' '.join(filtered)


class SpanishTextPreprocessor:
    """
    Preprocesador especializado para texto en español.
    Combina normalización con análisis lingüístico básico.
    """
    
    def __init__(self):
        self.normalizer = TextNormalizer()
    
    def preprocess(self, text: str) -> dict:
        """
        Preprocesa texto y retorna análisis completo.
        
        Returns:
            Dict con texto normalizado, tokens, números, etc.
        """
        return {
            'original': text,
            'normalized': self.normalizer.normalize(text),
            'tokens': self.normalizer.tokenize(text),
            'numbers': self.normalizer.extract_numbers(text),
            'word_count': len(self.normalizer.tokenize(text)),
            'char_count': len(text),
        }
    
    def is_question(self, text: str) -> bool:
        """Detecta si el texto es una pregunta"""
        question_patterns = [
            r'^¿',
            r'\?$',
            r'\b(cómo|como|qué|que|cuál|cual|dónde|donde|cuándo|cuando|quién|quien)\b',
            r'\b(está|esta|están|estan|es|son)\s+(encendid|apagad|abiert|cerrad)',
        ]
        
        text_lower = text.lower()
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def is_command(self, text: str) -> bool:
        """Detecta si el texto es un comando/imperativo"""
        command_patterns = [
            r'\b(enciende|apaga|abre|cierra|prende|activa|desactiva)\b',
            r'\b(por\s+favor|porfa|xfa)\s+(enciende|apaga|abre|cierra)\b',
            r'^(enciende|apaga|abre|cierra|prende)',
        ]
        
        text_lower = text.lower()
        for pattern in command_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def get_sentence_type(self, text: str) -> str:
        """
        Clasifica el tipo de oración.
        
        Returns:
            'question', 'command', 'statement', o 'unknown'
        """
        if self.is_question(text):
            return 'question'
        elif self.is_command(text):
            return 'command'
        elif text.strip():
            return 'statement'
        return 'unknown'

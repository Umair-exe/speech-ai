from translate import Translator
from fastapi import HTTPException
from typing import Dict
from langdetect import detect, LangDetectException


class TranslationService:
    """Service for text translation using translate library"""

    def __init__(self):
        # We'll create translators on demand
        pass

    async def translate_text(
        self,
        text: str,
        source_lang: str = 'auto',
        target_lang: str = 'en'
    ) -> Dict:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_lang: Source language code (auto for auto-detection)
            target_lang: Target language code

        Returns:
            Dict with translation results
        """
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )

        if len(text) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Text is too long (maximum 5000 characters)"
            )

        try:
            # Handle auto-detection
            actual_source_lang = source_lang
            if source_lang.lower() == 'auto':
                try:
                    detected_lang = detect(text)
                    actual_source_lang = detected_lang
                    print(f"Detected language: {detected_lang}")
                except LangDetectException:
                    # If detection fails, default to English
                    actual_source_lang = 'en'
                    print("Language detection failed, defaulting to English")

            # Create translator for the language pair
            translator = Translator(from_lang=actual_source_lang, to_lang=target_lang)
            translation = translator.translate(text)

            return {
                "success": True,
                "original_text": text,
                "translated_text": translation,
                "source_language": actual_source_lang,
                "target_language": target_lang
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Translation failed: {str(e)}"
            )

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages for translation

        Returns:
            Dict mapping language codes to names
        """
        # Common languages supported by translate library
        languages = {
            'af': 'Afrikaans',
            'sq': 'Albanian',
            'ar': 'Arabic',
            'hy': 'Armenian',
            'az': 'Azerbaijani',
            'eu': 'Basque',
            'be': 'Belarusian',
            'bn': 'Bengali',
            'bs': 'Bosnian',
            'bg': 'Bulgarian',
            'ca': 'Catalan',
            'ceb': 'Cebuano',
            'ny': 'Chichewa',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'hr': 'Croatian',
            'cs': 'Czech',
            'da': 'Danish',
            'nl': 'Dutch',
            'en': 'English',
            'eo': 'Esperanto',
            'et': 'Estonian',
            'tl': 'Filipino',
            'fi': 'Finnish',
            'fr': 'French',
            'fy': 'Frisian',
            'gl': 'Galician',
            'ka': 'Georgian',
            'de': 'German',
            'el': 'Greek',
            'gu': 'Gujarati',
            'ht': 'Haitian Creole',
            'ha': 'Hausa',
            'haw': 'Hawaiian',
            'iw': 'Hebrew',
            'hi': 'Hindi',
            'hmn': 'Hmong',
            'hu': 'Hungarian',
            'is': 'Icelandic',
            'ig': 'Igbo',
            'id': 'Indonesian',
            'ga': 'Irish',
            'it': 'Italian',
            'ja': 'Japanese',
            'jw': 'Javanese',
            'kn': 'Kannada',
            'kk': 'Kazakh',
            'km': 'Khmer',
            'ko': 'Korean',
            'ku': 'Kurdish (Kurmanji)',
            'ky': 'Kyrgyz',
            'lo': 'Lao',
            'la': 'Latin',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'lb': 'Luxembourgish',
            'mk': 'Macedonian',
            'mg': 'Malagasy',
            'ms': 'Malay',
            'ml': 'Malayalam',
            'mt': 'Maltese',
            'mi': 'Maori',
            'mr': 'Marathi',
            'mn': 'Mongolian',
            'my': 'Myanmar (Burmese)',
            'ne': 'Nepali',
            'no': 'Norwegian',
            'or': 'Odia',
            'ps': 'Pashto',
            'fa': 'Persian',
            'pl': 'Polish',
            'pt': 'Portuguese',
            'pa': 'Punjabi',
            'ro': 'Romanian',
            'ru': 'Russian',
            'sm': 'Samoan',
            'gd': 'Scots Gaelic',
            'sr': 'Serbian',
            'st': 'Sesotho',
            'sn': 'Shona',
            'sd': 'Sindhi',
            'si': 'Sinhala',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'so': 'Somali',
            'es': 'Spanish',
            'su': 'Sundanese',
            'sw': 'Swahili',
            'sv': 'Swedish',
            'tg': 'Tajik',
            'ta': 'Tamil',
            'te': 'Telugu',
            'th': 'Thai',
            'tr': 'Turkish',
            'uk': 'Ukrainian',
            'ur': 'Urdu',
            'ug': 'Uyghur',
            'uz': 'Uzbek',
            'vi': 'Vietnamese',
            'cy': 'Welsh',
            'xh': 'Xhosa',
            'yi': 'Yiddish',
            'yo': 'Yoruba',
            'zu': 'Zulu'
        }
        return languages


# Global instance
translation_service = TranslationService()


# Simple translate function for OCR service
async def simple_translate(text: str, source_lang: str, target_lang: str) -> str:
    """
    Simple translation function for use with OCR service.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
    
    Returns:
        Translated text string
    """
    try:
        translator = Translator(from_lang=source_lang, to_lang=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails
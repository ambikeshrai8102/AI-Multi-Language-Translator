"""
Translation engine using Deep Translator (free, no API key needed).
"""
from deep_translator import GoogleTranslator

LANGUAGE_CODES = {
    'af': 'Afrikaans',    'sq': 'Albanian',     'am': 'Amharic',
    'ar': 'Arabic',       'hy': 'Armenian',     'az': 'Azerbaijani',
    'eu': 'Basque',       'be': 'Belarusian',   'bn': 'Bengali',
    'bs': 'Bosnian',      'bg': 'Bulgarian',    'ca': 'Catalan',
    'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
    'hr': 'Croatian',     'cs': 'Czech',        'da': 'Danish',
    'nl': 'Dutch',        'en': 'English',      'eo': 'Esperanto',
    'et': 'Estonian',     'fi': 'Finnish',      'fr': 'French',
    'gl': 'Galician',     'ka': 'Georgian',     'de': 'German',
    'el': 'Greek',        'gu': 'Gujarati',     'ht': 'Haitian Creole',
    'ha': 'Hausa',        'he': 'Hebrew',       'hi': 'Hindi',
    'hu': 'Hungarian',    'is': 'Icelandic',    'id': 'Indonesian',
    'ga': 'Irish',        'it': 'Italian',      'ja': 'Japanese',
    'kn': 'Kannada',      'kk': 'Kazakh',       'km': 'Khmer',
    'ko': 'Korean',       'ku': 'Kurdish',      'ky': 'Kyrgyz',
    'lo': 'Lao',          'la': 'Latin',        'lv': 'Latvian',
    'lt': 'Lithuanian',   'mk': 'Macedonian',   'ms': 'Malay',
    'ml': 'Malayalam',    'mt': 'Maltese',      'mi': 'Maori',
    'mr': 'Marathi',      'mn': 'Mongolian',    'my': 'Myanmar',
    'ne': 'Nepali',       'no': 'Norwegian',    'fa': 'Persian',
    'pl': 'Polish',       'pt': 'Portuguese',   'pa': 'Punjabi',
    'ro': 'Romanian',     'ru': 'Russian',      'sr': 'Serbian',
    'si': 'Sinhala',      'sk': 'Slovak',       'sl': 'Slovenian',
    'so': 'Somali',       'es': 'Spanish',      'sw': 'Swahili',
    'sv': 'Swedish',      'tl': 'Filipino',     'ta': 'Tamil',
    'te': 'Telugu',       'th': 'Thai',         'tr': 'Turkish',
    'uk': 'Ukrainian',    'ur': 'Urdu',         'uz': 'Uzbek',
    'vi': 'Vietnamese',   'cy': 'Welsh',        'xh': 'Xhosa',
    'yi': 'Yiddish',      'yo': 'Yoruba',       'zu': 'Zulu',
}

LANGUAGE_FLAGS = {
    'af': '🇿🇦', 'sq': '🇦🇱', 'am': '🇪🇹', 'ar': '🇸🇦', 'hy': '🇦🇲',
    'az': '🇦🇿', 'be': '🇧🇾', 'bn': '🇧🇩', 'bs': '🇧🇦', 'bg': '🇧🇬',
    'zh-cn': '🇨🇳', 'zh-tw': '🇹🇼', 'hr': '🇭🇷', 'cs': '🇨🇿', 'da': '🇩🇰',
    'nl': '🇳🇱', 'en': '🇬🇧', 'et': '🇪🇪', 'fi': '🇫🇮', 'fr': '🇫🇷',
    'ka': '🇬🇪', 'de': '🇩🇪', 'el': '🇬🇷', 'gu': '🇮🇳', 'ht': '🇭🇹',
    'he': '🇮🇱', 'hi': '🇮🇳', 'hu': '🇭🇺', 'is': '🇮🇸', 'id': '🇮🇩',
    'ga': '🇮🇪', 'it': '🇮🇹', 'ja': '🇯🇵', 'kn': '🇮🇳', 'kk': '🇰🇿',
    'km': '🇰🇭', 'ko': '🇰🇷', 'ky': '🇰🇬', 'lo': '🇱🇦', 'lv': '🇱🇻',
    'lt': '🇱🇹', 'mk': '🇲🇰', 'ms': '🇲🇾', 'ml': '🇮🇳', 'mt': '🇲🇹',
    'mr': '🇮🇳', 'mn': '🇲🇳', 'my': '🇲🇲', 'ne': '🇳🇵', 'no': '🇳🇴',
    'fa': '🇮🇷', 'pl': '🇵🇱', 'pt': '🇵🇹', 'pa': '🇮🇳', 'ro': '🇷🇴',
    'ru': '🇷🇺', 'sr': '🇷🇸', 'si': '🇱🇰', 'sk': '🇸🇰', 'sl': '🇸🇮',
    'so': '🇸🇴', 'es': '🇪🇸', 'sw': '🇰🇪', 'sv': '🇸🇪', 'tl': '🇵🇭',
    'ta': '🇮🇳', 'te': '🇮🇳', 'th': '🇹🇭', 'tr': '🇹🇷', 'uk': '🇺🇦',
    'ur': '🇵🇰', 'uz': '🇺🇿', 'vi': '🇻🇳', 'cy': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'yi': '✡️',
    'yo': '🇳🇬', 'zu': '🇿🇦', 'eu': '🏴', 'ca': '🏴', 'la': '🏛️',
    'eo': '🌍', 'haw': '🌺', 'xh': '🇿🇦',
}


def claude_translate(text: str, source_lang: str, target_lang: str) -> dict:
    """Translate text using Deep Translator (free)."""
    src = 'auto' if source_lang == 'auto' else source_lang

    translated = GoogleTranslator(source=src, target=target_lang).translate(text)

    detected_code = source_lang if source_lang != 'auto' else 'en'
    detected_name = LANGUAGE_CODES.get(detected_code, detected_code)

    return {
        "translated_text": translated,
        "detected_lang_code": detected_code,
        "detected_lang_name": detected_name,
    }
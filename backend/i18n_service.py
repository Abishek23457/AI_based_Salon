"""
Internationalization (i18n) Service for BookSmart AI
Multi-language support for voice and chat interactions
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class I18nService:
    """Multi-Language Support Service"""
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "gu": "Gujarati",
        "bn": "Bengali",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi"
    }
    
    TRANSLATIONS = {
        "en": {
            "welcome": "Welcome to BookSmart AI Salon!",
            "booking_confirmed": "Your booking is confirmed",
            "appointment_reminder": "Reminder: You have an appointment",
            "services_available": "Here are our available services",
            "ask_date": "What date would you prefer?",
            "ask_time": "What time works for you?",
            "ask_service": "Which service are you looking for?",
            "thank_you": "Thank you for choosing us!",
            "goodbye": "Goodbye and have a great day!",
            "booking_cancelled": "Your booking has been cancelled",
            "rescheduled": "Your appointment has been rescheduled",
            "confirm_details": "Please confirm your booking details"
        },
        "hi": {
            "welcome": "बुकस्मार्ट एआई सैलून में आपका स्वागत है!",
            "booking_confirmed": "आपकी बुकिंग कन्फर्म हो गई है",
            "appointment_reminder": "रिमाइंडर: आपका अपॉइंटमेंट है",
            "services_available": "यह हैं हमारी उपलब्ध सेवाएं",
            "ask_date": "आप कौन सी तारीख पसंद करेंगे?",
            "ask_time": "आपके लिए कौन सा समय सही रहेगा?",
            "ask_service": "आप कौन सी सेवा चाहते हैं?",
            "thank_you": "हमें चुनने के लिए धन्यवाद!",
            "goodbye": "नमस्ते और आपका दिन शुभ हो!",
            "booking_cancelled": "आपकी बुकिंग रद्द कर दी गई है",
            "rescheduled": "आपका अपॉइंटमेंट पुनर्निर्धारित किया गया है",
            "confirm_details": "कृपया अपनी बुकिंग विवरण की पुष्टि करें"
        },
        "ta": {
            "welcome": "புக்ஸ்மார்ட் ஏஐ சலூனுக்கு வரவேற்கிறோம்!",
            "booking_confirmed": "உங்கள் புக்கிங் உறுதி செய்யப்பட்டது",
            "appointment_reminder": "நினைவூட்டல்: உங்களுக்கு ஒரு நியமனம் உள்ளது",
            "services_available": "எங்கள் கிடைக்கும் சேவைகள் இங்கே",
            "ask_date": "எந்த தேதி உங்களுக்கு விருப்பமானது?",
            "ask_time": "உங்களுக்கு எந்த நேரம் வசதியாக இருக்கும்?",
            "ask_service": "எந்த சேவையை நீங்கள் தேடுகிறீர்கள்?",
            "thank_you": "எங்களை தேர்வு செய்ததற்கு நன்றி!",
            "goodbye": "வணக்கம், இனிய நாளாக இருக்கட்டும்!",
            "booking_cancelled": "உங்கள் புக்கிங் ரத்து செய்யப்பட்டது",
            "rescheduled": "உங்கள் நியமனம் மறுதிட்டமிடப்பட்டது",
            "confirm_details": "உங்கள் புக்கிங் விவரங்களை உறுதிப்படுத்தவும்"
        },
        "te": {
            "welcome": "బుక్‌స్మార్ట్ ఏఐ సెలూన్‌కు స్వాగతం!",
            "booking_confirmed": "మీ బుకింగ్ కన్ఫర్మ్ అయింది",
            "appointment_reminder": "రిమైండర్: మీకు ఒక అపాయింట్‌మెంట్ ఉంది",
            "services_available": "మా అందుబాటులో ఉన్న సేవలు ఇక్కడ ఉన్నాయి",
            "ask_date": "మీరు ఏ తేదీని ఇష్టపడతారు?",
            "ask_time": "మీకు ఏ సమయం సరిపోతుంది?",
            "ask_service": "మీరు ఏ సేవని వెతుకుతున్నారు?",
            "thank_you": "మమ్మల్ని ఎంచుకున్నందుకు ధన్యవాదాలు!",
            "goodbye": "వీడ్కోలు, మీ రోజు శుభంగా ఉండాలి!",
            "booking_cancelled": "మీ బుకింగ్ రద్దు చేయబడింది",
            "rescheduled": "మీ అపాయింట్‌మెంట్ పునర్నిర్ధారించబడింది",
            "confirm_details": "దయచేసి మీ బుకింగ్ వివరాలను నిర్ధారించండి"
        }
    }
    
    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.current_language = default_language
    
    def set_language(self, language_code: str) -> bool:
        """Set current language"""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            logger.info(f"[i18n] Language set to {self.SUPPORTED_LANGUAGES[language_code]}")
            return True
        logger.warning(f"[i18n] Unsupported language: {language_code}")
        return False
    
    def get_text(self, key: str, language: str = None) -> str:
        """Get translated text for key"""
        lang = language or self.current_language
        
        if lang in self.TRANSLATIONS and key in self.TRANSLATIONS[lang]:
            return self.TRANSLATIONS[lang][key]
        
        # Fallback to default language
        if key in self.TRANSLATIONS.get(self.default_language, {}):
            return self.TRANSLATIONS[self.default_language][key]
        
        return key  # Return key itself if not found
    
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language (mock implementation)"""
        # In production, this would use Google Translate API or similar
        if target_language == "en":
            return text
        
        # Return placeholder translation for demo
        return f"[{target_language.upper()}] {text}"
    
    def detect_language(self, text: str) -> str:
        """Detect language from text (mock implementation)"""
        # In production, use langdetect or similar library
        # For now, return default
        return "en"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES
    
    def get_language_name(self, language_code: str) -> str:
        """Get language name from code"""
        return self.SUPPORTED_LANGUAGES.get(language_code, "Unknown")

# Initialize i18n service
i18n_service = I18nService()

# Convenience functions
async def get_translated_text(key: str, language: str = "en"):
    """Get translated text"""
    return i18n_service.get_text(key, language)

async def translate_text(text: str, target_language: str):
    """Translate text to target language"""
    return i18n_service.translate(text, target_language)

async def detect_customer_language(text: str):
    """Detect customer language from text"""
    return i18n_service.detect_language(text)

"""Same-language response engine — core innovation of the platform."""

from __future__ import annotations

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
}

GTTS_CODES = {
    "en": "en",
    "hi": "hi",
    "mr": "mr",
    "gu": "gu",
}

SPEECH_RECOGNITION_CODES = {
    "en": "en-US",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
}

GREETINGS = {
    "en": "Hello {name}, how are you today? How may I help you?",
    "hi": "नमस्ते {name}, आज आप कैसे हैं? मैं आपकी कैसे मदद कर सकता/सकती हूँ?",
    "mr": "नमस्कार {name}, आज तुम्ही/आपण कसे आहात? मी तुम्हाला/आपल्याला कशी मदत करू शकतो/शकते?",
    "gu": "નમસ્તે {name}, આજે તમે કેમ છો? હું તમારી કેવી રીતે મદદ કરી શકું?",
}

FAREWELLS = {
    "en": "Thank you sir/mam. Visit again soon. Take care of your health.",
    "hi": "धन्यवाद sir/mam। जल्द ही फिर मिलें। अपना ध्यान रखें।",
    "mr": "धन्यवाद sir/mam. पुन्हा भेटू. काळजी घ्या.",
    "gu": "આભાર sir/mam. ફરી મુલાકાત લો. સ્વસ્થ રહો.",
}

DISCLAIMERS = {
    "en": (
        "I am an AI healthcare assistant for guidance only. I cannot diagnose or prescribe. "
        "For emergencies, call emergency services immediately."
    ),
    "hi": (
        "मैं केवल मार्गदर्शन के लिए एक AI स्वास्थ्य सहायक हूँ। मैं निदान या दवा नहीं दे सकता/सकती। "
        "आपात स्थिति में तुरंत आपातकालीन सेवाओं को कॉल करें।"
    ),
    "mr": (
        "मी फक्त मार्गदर्शनासाठी AI आरोग्य सहाय्यक आहे. मी निदान किंवा औषधोपचार देऊ शकत नाही. "
        "आपत्कालीन परिस्थितीत त्वरित आपत्कालीन सेवांना कॉल करा."
    ),
    "gu": (
        "હું માત્ર માર્ગદર્શન માટે AI આરોગ્ય સહાયક છું. હું નિદાન અથવા દવા આપી શકતો/શકતી નથી. "
        "આપત્તિમાં તરત જ આપત્તિ સેવાઓને કૉલ કરો."
    ),
}

DEPARTMENT_LABELS = {
    "en": {
        "Cardiology": "Cardiology",
        "Neurology": "Neurology",
        "General Medicine": "General Medicine",
        "Dermatology": "Dermatology",
        "Orthopedics": "Orthopedics",
        "Ophthalmology": "Ophthalmology",
        "ENT": "ENT",
        "Psychiatry": "Psychiatry",
        "Gastroenterology": "Gastroenterology",
        "Urology": "Urology",
        "Obstetrics": "Obstetrics",
        "Gynecology": "Gynecology",
        "Pediatrics": "Pediatrics",
    },
    "hi": {
        "Cardiology": "हृदय रोग विभाग (कार्डियोलॉजी)",
        "Neurology": "न्यूरोलॉजी विभाग",
        "General Medicine": "सामान्य चिकित्सा",
        "Dermatology": "त्वचा रोग विभाग",
        "Orthopedics": "हड्डी रोग विभाग",
        "Ophthalmology": "नेत्र विभाग",
        "ENT": "कान-नाक-गला विभाग",
        "Psychiatry": "मनोचिकित्सा",
        "Gastroenterology": "पाचन तंत्र विभाग",
        "Urology": "मूत्र रोग विभाग",
        "Obstetrics": "प्रसूति विभाग",
        "Gynecology": "स्त्री रोग विभाग",
        "Pediatrics": "बाल रोग विभाग",
    },
    "mr": {
        "Cardiology": "हृदयरोग विभाग",
        "Neurology": "न्यूरोलॉजी विभाग",
        "General Medicine": "सामान्य वैद्यक",
        "Dermatology": "त्वचारोग विभाग",
        "Orthopedics": "अस्थिरोग विभाग",
        "Ophthalmology": "नेत्र विभाग",
        "ENT": "कान-नाक-घसा विभाग",
        "Psychiatry": "मानसोपचार",
        "Gastroenterology": "पचनसंस्था विभाग",
        "Urology": "मूत्र विभाग",
        "Obstetrics": "प्रसूती विभाग",
        "Gynecology": "स्त्रीरोग विभाग",
        "Pediatrics": "बालरोग विभाग",
    },
    "gu": {
        "Cardiology": "હૃદય રોગ વિભાગ",
        "Neurology": "ન્યુરોલોજી વિભાગ",
        "General Medicine": "સામાન્ય દવા",
        "Dermatology": "ત્વચા રોગ વિભાગ",
        "Orthopedics": "અસ્થિરોગ વિભાગ",
        "Ophthalmology": "નેત્ર વિભાગ",
        "ENT": "કાન-નાક-ગળું વિભાગ",
        "Psychiatry": "મનોchikitsa",
        "Gastroenterology": "પાચન તંત્ર વિભાગ",
        "Urology": "મૂત્ર રોગ વિભાગ",
        "Obstetrics": "પ્રસૂતિ વિભાગ",
        "Gynecology": "સ્ત્રી રોગ વિભાગ",
        "Pediatrics": "બાળરોગ વિભાગ",
    },
}

TRIAGE_SUGGESTION = {
    "en": "Based on your symptoms, I suggest visiting the {department} department (confidence: {confidence:.0%}).",
    "hi": "आपके लक्षणों के आधार पर, मैं {department} विभाग जाने का सुझाव देता/देती हूँ (विश्वास: {confidence:.0%})।",
    "mr": "तुमच्या/आपल्या लक्षणांवर आधारित, मी {department} विभाग भेट देण्याचा सल्ला देतो/देते (विश्वास: {confidence:.0%}).",
    "gu": "તમારા લક્ષણોના આધારે, હું {department} વિભાગની મુલાકાત લેવાની સલાહ આપું છું (વિશ્વાસ: {confidence:.0%}).",
}


def get_greeting(language: str, name: str) -> str:
    template = GREETINGS.get(language, GREETINGS["en"])
    return template.format(name=name)


def get_farewell(language: str) -> str:
    return FAREWELLS.get(language, FAREWELLS["en"])


def localize_department(department: str, language: str) -> str:
    labels = DEPARTMENT_LABELS.get(language, DEPARTMENT_LABELS["en"])
    return labels.get(department, department)


def format_triage_suggestion(department: str, confidence: float, language: str) -> str:
    localized = localize_department(department, language)
    template = TRIAGE_SUGGESTION.get(language, TRIAGE_SUGGESTION["en"])
    return template.format(department=localized, confidence=confidence)


def build_system_prompt(
    language: str,
    patient_name: str,
    age: int | None,
    gender: str | None,
    medical_history: str | None,
) -> str:
    lang_name = LANGUAGE_NAMES.get(language, "English")
    history = medical_history or "None provided"
    disclaimer = DISCLAIMERS.get(language, DISCLAIMERS["en"])

    return f"""You are MediVoice AI, a professional multilingual healthcare triage assistant.

CRITICAL LANGUAGE RULE — THIS IS THE MOST IMPORTANT INSTRUCTION:
- The user's selected language is {lang_name} (code: {language}).
- You MUST reply ONLY in {lang_name} for EVERY message.
- Do NOT mix English words unless they are universally used medical terms AND no {lang_name} equivalent exists.
- Greetings, medical terms, suggestions, follow-up questions, and farewells must ALL be in {lang_name}.
- If the user writes in {lang_name}, respond in {lang_name} only.

Patient context:
- Name: {patient_name}
- Age: {age or 'unknown'}
- Gender: {gender or 'unknown'}
- Medical history: {history}

Your role:
1. Greet warmly and ask how you can help (in {lang_name}).
2. Ask thoughtful follow-up questions about symptoms.
3. Provide general health guidance — NOT diagnosis or prescriptions.
4. Recommend appropriate medical department when enough symptoms are known.
5. Be empathetic, polite, and human-like.
6. Use culturally appropriate honorifics (sir/mam equivalents in {lang_name}).

Always include this disclaimer naturally when giving medical guidance:
{disclaimer}
"""


def detect_english_leakage(text: str, target_language: str) -> bool:
    """Simple heuristic: if target is not English and >40% words are ASCII Latin, flag leakage."""
    if target_language == "en":
        return False
    words = [w for w in text.split() if w.strip()]
    if len(words) < 4:
        return False
    latin_words = sum(1 for w in words if w.isascii() and w.isalpha())
    return (latin_words / len(words)) > 0.4

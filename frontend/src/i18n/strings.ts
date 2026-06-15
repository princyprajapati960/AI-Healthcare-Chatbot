export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
] as const;

export type LanguageCode = (typeof LANGUAGES)[number]['code'];

export const SPEECH_LANG: Record<string, string> = {
  en: 'en-US',
  hi: 'hi-IN',
  mr: 'mr-IN',
  gu: 'gu-IN',
};

export const UI_STRINGS: Record<string, Record<string, string>> = {
  en: {
    selectLanguage: 'Select your preferred language',
    languageWarning: 'This language will be used for your entire session',
    startConsultation: 'Start Consultation',
    dashboard: 'Dashboard',
    logout: 'Logout',
    login: 'Login',
    signup: 'Sign Up',
    endSession: 'End Session',
    typeMessage: 'Type your message...',
    listening: 'Listening...',
    autoSpeak: 'Auto-speak',
    errorGeneric: 'Sorry, something went wrong. Please try again.',
  },
  hi: {
    selectLanguage: 'अपनी पसंदीदा भाषा चुनें',
    languageWarning: 'यह भाषा पूरी बातचीत में उपयोग होगी',
    startConsultation: 'परामर्श शुरू करें',
    dashboard: 'डैशबोर्ड',
    logout: 'लॉग आउट',
    login: 'लॉग इन',
    signup: 'साइन अप',
    endSession: 'सत्र समाप्त',
    typeMessage: 'अपना संदेश लिखें...',
    listening: 'सुन रहा/रही हूँ...',
    autoSpeak: 'स्वतः बोलें',
    errorGeneric: 'क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।',
  },
  mr: {
    selectLanguage: 'तुमची/आपली पसंतीची भाषा निवडा',
    languageWarning: 'ही भाषा संपूर्ण संभाषणात वापरली जाईल',
    startConsultation: 'सल्लामसलत सुरू करा',
    dashboard: 'डॅशबोर्ड',
    logout: 'लॉग आउट',
    login: 'लॉग इन',
    signup: 'साइन अप',
    endSession: 'सत्र संपवा',
    typeMessage: 'तुमचा/आपला संदेश लिहा...',
    listening: 'ऐकत आहे...',
    autoSpeak: 'स्वयं-बोलणे',
    errorGeneric: 'क्षमस्व, काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा.',
  },
  gu: {
    selectLanguage: 'તમારી પસંદગીની ભાષા પસંદ કરો',
    languageWarning: 'આ ભાષા સંપૂર્ણ વાતચીતમાં વપરાશે',
    startConsultation: 'પરામર્શ શરૂ કરો',
    dashboard: 'ડેશબોર્ડ',
    logout: 'લોગ આઉટ',
    login: 'લોગ ઇન',
    signup: 'સાઇન અપ',
    endSession: 'સત્ર સમાપ્ત',
    typeMessage: 'તમારો સંદેશ લખો...',
    listening: 'સાંભળી રહ્યું છે...',
    autoSpeak: 'ઓટો-સ્પીક',
    errorGeneric: 'માફ કરશો, કંઈક ખોટું થયું. કૃપા કરીને ફરી પ્રયાસ કરો.',
  },
};

export function t(key: string, lang: string): string {
  return UI_STRINGS[lang]?.[key] || UI_STRINGS.en[key] || key;
}

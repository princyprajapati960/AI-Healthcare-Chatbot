"""Healthcare chat agent with same-language enforcement."""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from aiohttp import http_websocket
from aiohttp import client_exceptions
from PIL import ImageFile
from PIL import ImageFile
from PIL import ImageFile

import logging
import google.generativeai as genai

from backend.app.config import settings
from backend.app.services.language_engine import (
build_system_prompt,
detect_english_leakage,
format_triage_suggestion,
get_farewell,
get_greeting,
)
from backend.app.services.triage_ml import predict_department

FALLBACK_RESPONSES = {
"en": (
"I understand your concern. Could you tell me more about your symptoms — when they started, "
"how severe they are, and if anything makes them better or worse?"
),
"hi": (
"मैं आपकी चिंता समझता/समझती हूँ। क्या आप अपने लक्षणों के बारे में और बता सकते हैं — "
"वे कब शुरू हुए, कितनी गंभीर हैं, और क्या कुछ उन्हें बेहतर या बदतर बनाता है?"
),
"mr": (
"मी तुमची/आपली चिंता समजतो/समजते. कृपया तुमच्या/आपल्या लक्षणांबद्दल अधिक सांगा — "
"ते कधी सुरू झाले, किती तीव्र आहेत, आणि काही त्यांना बरे किंवा वाईट करते का?"
),
"gu": (
"હું તમારી ચિંતા સમજું છું. કૃપા કરીને તમારા લક્ષણો વિશે વધુ જણાવો — "
"તે ક્યારે શરૂ થયા, કેટલા ગંભીર છે, અને શું કંઈક તેમને સારું અથવા ખરાબ બનાવે છે?"
),
}

class ChatAgent:
    def __init__(self):
        try:
            genai.configure(
                api_key=settings.gemini_api_key
            )
            self.model = genai.GenerativeModel(
                settings.gemini_model
            )
            logging.info("Gemini initialized successfully")
        except Exception as e:
            logging.error(
                f"Gemini initialization failed: {e}"
            )
            self.model = None

    def generate_greeting(self, language: str, name: str) -> str:
        return get_greeting(language, name)

    def generate_farewell(self, language: str) -> str:
        return get_farewell(language)

    def generate_response(
        self,
        user_message: str,
        language: str,
        patient_name: str,
        age: int | None,
        gender: str | None,
        medical_history: str | None,
        history: list[dict[str, str]],
    ) -> tuple[str, str | None, float | None]:

        department, confidence = predict_department(user_message)

        triage_note = (
            format_triage_suggestion(
                department,
                confidence,
                language,
            )
            if confidence > 0.3
            else None
        )

        if not self.model:
            base = FALLBACK_RESPONSES.get(
                language,
                FALLBACK_RESPONSES["en"]
            )

            if triage_note:
                return (
                    f"{base}\n\n{triage_note}",
                    department,
                    confidence,
                )

            return base, department, confidence

        try:
            system = build_system_prompt(
                language,
                patient_name,
                age,
                gender,
                medical_history,
            )

            messages: list[dict[str, str]] = [
                {"role": "system", "content": system}
            ]

            for msg in history[-10:]:
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

            prompt_parts = []

            for msg in messages:
                prompt_parts.append(
                    f"{msg['role']}: {msg['content']}"
                )

            prompt = "\n".join(prompt_parts)

            response = self.model.generate_content(
                prompt
            )

            content = (
                response.text
                if response.text
                else FALLBACK_RESPONSES.get(
                    language,
                    FALLBACK_RESPONSES["en"]
                )
            )

            if detect_english_leakage(
                content,
                language,
            ):
                try:
                    retry_messages = messages + [
                        {
                            "role": "system",
                            "content": (
                                f"Your previous response mixed English. "
                                f"Rewrite ENTIRELY in {language} only."
                            ),
                        }
                    ]

                    retry_prompt = "\n".join(
                        [
                            f"{msg['role']}: {msg['content']}"
                            for msg in retry_messages
                        ]
                    )

                    retry = self.model.generate_content(
                        retry_prompt
                    )

                    if retry.text:
                        content = retry.text

                except Exception:
                    pass

            if triage_note and confidence > 0.5:
                content = (
                    f"{content}\n\n{triage_note}"
                )

            return (
                content,
                department,
                confidence,
            )

        except Exception as e:
            logging.warning(
                f"Gemini API error, using fallback: {e}"
            )

            base = FALLBACK_RESPONSES.get(
                language,
                FALLBACK_RESPONSES["en"]
            )

            if triage_note:
                return (
                    f"{base}\n\n{triage_note}",
                    department,
                    confidence,
                )

            return (
                base,
                department,
                confidence,
            )

chat_agent = ChatAgent()
"""Text-to-speech via gTTS."""

from __future__ import annotations

import uuid
from pathlib import Path

from gtts import gTTS

from backend.app.services.language_engine import GTTS_CODES

AUDIO_DIR = Path(__file__).resolve().parents[3] / "audio"


def synthesize_speech(text: str, language: str) -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    lang_code = GTTS_CODES.get(language, "en")
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename
    tts = gTTS(text=text, lang=lang_code)
    tts.save(str(filepath))
    return filepath

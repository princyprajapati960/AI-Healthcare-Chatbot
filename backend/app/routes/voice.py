from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.app.auth.security import get_current_user
from backend.app.models.schemas_api import TTSRequest
from backend.app.models.schemas_db import User
from backend.app.services.voice_service import synthesize_speech

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/tts")
def text_to_speech(data: TTSRequest, user: User = Depends(get_current_user)):
    if len(data.text) > 2000:
        raise HTTPException(status_code=400, detail="Text too long for TTS")
    filepath = synthesize_speech(data.text, data.language)
    return FileResponse(path=filepath, media_type="audio/mpeg", filename=filepath.name)

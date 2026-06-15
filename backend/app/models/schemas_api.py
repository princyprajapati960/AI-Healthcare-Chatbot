from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    avatar: str | None = None
    onboarding_complete: bool = False

    model_config = {"from_attributes": True}


class PatientProfileIn(BaseModel):
    full_name: str = Field(min_length=1)
    age: int = Field(ge=1, le=150)
    gender: str
    address: str
    phone: str
    medical_history: str | None = None
    language: str = Field(pattern="^(en|hi|mr|gu)$")


class PatientProfileOut(BaseModel):
    full_name: str
    age: int
    gender: str
    address: str
    phone: str
    medical_history: str | None
    language: str
    onboarding_complete: bool

    model_config = {"from_attributes": True}


class ChatMessageIn(BaseModel):
    content: str = Field(min_length=1)
    session_id: int | None = None


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    triage_department: str | None = None
    triage_confidence: float | None = None


class ChatSessionOut(BaseModel):
    id: int
    language: str
    started_at: str
    is_active: bool
    message_count: int = 0


class TriageRequest(BaseModel):
    symptoms: str


class TriageResponse(BaseModel):
    department: str
    confidence: float
    symptoms: str


class TTSRequest(BaseModel):
    text: str
    language: str = Field(pattern="^(en|hi|mr|gu)$")

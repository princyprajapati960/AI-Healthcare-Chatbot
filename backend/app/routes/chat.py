from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database.connection import get_db
from backend.app.models.schemas_api import ChatMessageIn, ChatMessageOut, ChatSessionOut, TriageRequest, TriageResponse
from backend.app.models.schemas_db import ChatMessage, ChatSession, PatientProfile, User
from backend.app.services.chat_agent import chat_agent
from backend.app.services.triage_ml import predict_department

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/session", response_model=ChatSessionOut)
def create_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if not profile or not profile.onboarding_complete:
        raise HTTPException(status_code=400, detail="Complete onboarding first")

    db.query(ChatSession).filter(ChatSession.user_id == user.id, ChatSession.is_active.is_(True)).update(
        {"is_active": False, "ended_at": datetime.utcnow()}
    )

    session = ChatSession(user_id=user.id, language=profile.language)
    db.add(session)
    db.commit()
    db.refresh(session)

    greeting = chat_agent.generate_greeting(profile.language, profile.full_name)
    msg = ChatMessage(session_id=session.id, role="assistant", content=greeting)
    db.add(msg)
    db.commit()

    return ChatSessionOut(
        id=session.id,
        language=session.language,
        started_at=session.started_at.isoformat(),
        is_active=session.is_active,
        message_count=1,
    )


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.started_at.desc())
        .limit(20)
        .all()
    )
    return [
        ChatSessionOut(
            id=s.id,
            language=s.language,
            started_at=s.started_at.isoformat(),
            is_active=s.is_active,
            message_count=len(s.messages),
        )
        for s in sessions
    ]


@router.get("/session/{session_id}/messages", response_model=list[ChatMessageOut])
def get_messages(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return [
        ChatMessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in session.messages
    ]


@router.post("/message", response_model=ChatMessageOut)
def send_message(
    data: ChatMessageIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Profile required")

    if data.session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == data.session_id, ChatSession.user_id == user.id, ChatSession.is_active.is_(True))
            .first()
        )
    else:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user.id, ChatSession.is_active.is_(True))
            .order_by(ChatSession.started_at.desc())
            .first()
        )
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    user_msg = ChatMessage(session_id=session.id, role="user", content=data.content)
    db.add(user_msg)
    db.commit()

    history = [{"role": m.role, "content": m.content} for m in session.messages]

    content, department, confidence = chat_agent.generate_response(
        user_message=data.content,
        language=session.language,
        patient_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        medical_history=profile.medical_history,
        history=history,
    )

    assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=content)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatMessageOut(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        created_at=assistant_msg.created_at.isoformat(),
        triage_department=department,
        triage_confidence=confidence,
    )


@router.post("/session/{session_id}/end")
def end_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    farewell = chat_agent.generate_farewell(session.language)
    msg = ChatMessage(session_id=session.id, role="assistant", content=farewell)
    db.add(msg)
    session.is_active = False
    session.ended_at = datetime.utcnow()
    db.commit()

    return {"message": farewell, "session_id": session_id}


@router.post("/triage", response_model=TriageResponse)
def triage(data: TriageRequest, user: User = Depends(get_current_user)):
    department, confidence = predict_department(data.symptoms)
    return TriageResponse(department=department, confidence=confidence, symptoms=data.symptoms)

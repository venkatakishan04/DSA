from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion, RealTimeAnalysis
from app.models.user import JobDescription
from app.services.ai_service import AIAnalysisService

router = APIRouter()
ai_service = AIAnalysisService()

# Pydantic models
class InterviewSessionCreate(BaseModel):
    title: str
    interview_type: str  # behavioral, technical, mixed
    job_description_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None

class InterviewSessionResponse(BaseModel):
    id: int
    session_id: str
    title: str
    interview_type: str
    status: str
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_minutes: Optional[int]
    overall_score: Optional[float]
    confidence_score: Optional[float]
    communication_score: Optional[float]
    technical_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
    requirements: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    experience_level: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    description: str
    requirements: Optional[List[str]]
    skills_required: Optional[List[str]]
    experience_level: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class InterviewQuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    category: Optional[str]
    difficulty_level: Optional[str]
    user_response: Optional[str]
    content_score: Optional[float]
    clarity_score: Optional[float]
    relevance_score: Optional[float]
    structure_score: Optional[float]
    feedback: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("/job-description", response_model=JobDescriptionResponse)
async def create_job_description(
    job_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    try:
        job_description = JobDescription(
            user_id=current_user.id,
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            requirements=job_data.requirements,
            skills_required=job_data.skills_required,
            experience_level=job_data.experience_level
        )
        
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        
        return JobDescriptionResponse.from_orm(job_description)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job description"
        )

@router.get("/job-descriptions", response_model=List[JobDescriptionResponse])
async def get_job_descriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's job descriptions"""
    try:
        job_descriptions = db.query(JobDescription).filter(
            JobDescription.user_id == current_user.id,
            JobDescription.is_active == True
        ).all()
        
        return [JobDescriptionResponse.from_orm(jd) for jd in job_descriptions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job descriptions"
        )

@router.post("/session", response_model=InterviewSessionResponse)
async def create_interview_session(
    session_data: InterviewSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new interview session"""
    try:
        session_id = str(uuid.uuid4())
        
        interview_session = InterviewSession(
            user_id=current_user.id,
            job_description_id=session_data.job_description_id,
            session_id=session_id,
            title=session_data.title,
            interview_type=session_data.interview_type,
            scheduled_at=session_data.scheduled_at,
            status="scheduled"
        )
        
        db.add(interview_session)
        db.commit()
        db.refresh(interview_session)
        
        return InterviewSessionResponse.from_orm(interview_session)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview session"
        )

@router.get("/sessions", response_model=List[InterviewSessionResponse])
async def get_interview_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's interview sessions"""
    try:
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id
        ).order_by(InterviewSession.created_at.desc()).all()
        
        return [InterviewSessionResponse.from_orm(session) for session in sessions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview sessions"
        )

@router.get("/session/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific interview session"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        return InterviewSessionResponse.from_orm(session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview session"
        )

@router.post("/session/{session_id}/start")
async def start_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start an interview session"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        if session.status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session cannot be started"
            )
        
        # Update session status
        session.status = "in_progress"
        session.started_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Interview session started", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start interview session"
        )

@router.post("/session/{session_id}/end")
async def end_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End an interview session"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session is not in progress"
            )
        
        # Update session status
        session.status = "completed"
        session.ended_at = datetime.utcnow()
        
        if session.started_at:
            duration = session.ended_at - session.started_at
            session.duration_minutes = int(duration.total_seconds() / 60)
        
        db.commit()
        
        return {"message": "Interview session ended", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end interview session"
        )

@router.get("/session/{session_id}/questions", response_model=List[InterviewQuestionResponse])
async def get_session_questions(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get questions for an interview session"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).order_by(InterviewQuestion.created_at).all()
        
        return [InterviewQuestionResponse.from_orm(q) for q in questions]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session questions"
        )

@router.get("/session/{session_id}/analysis")
async def get_session_analysis(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed analysis for an interview session"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Get real-time analysis data
        real_time_analysis = db.query(RealTimeAnalysis).filter(
            RealTimeAnalysis.session_id == session.id
        ).order_by(RealTimeAnalysis.timestamp).all()
        
        analysis_data = {
            "session_id": session_id,
            "overall_score": session.overall_score,
            "confidence_score": session.confidence_score,
            "communication_score": session.communication_score,
            "technical_score": session.technical_score,
            "feedback_summary": session.feedback_summary,
            "improvement_suggestions": session.improvement_suggestions,
            "analysis_data": session.analysis_data,
            "real_time_analysis": [
                {
                    "timestamp": analysis.timestamp.isoformat(),
                    "analysis_type": analysis.analysis_type,
                    "confidence_level": analysis.confidence_level,
                    "emotion_detected": analysis.emotion_detected,
                    "eye_contact_score": analysis.eye_contact_score,
                    "speaking_pace": analysis.speaking_pace,
                    "filler_words_count": analysis.filler_words_count,
                    "alert_triggered": analysis.alert_triggered,
                    "feedback_message": analysis.feedback_message
                }
                for analysis in real_time_analysis
            ]
        }
        
        return analysis_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session analysis"
        )

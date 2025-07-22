from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    
    # Session details
    session_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    interview_type = Column(String, nullable=False)  # behavioral, technical, mixed
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Recording and data
    video_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    
    # AI Analysis Results
    overall_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    
    # Detailed analysis
    analysis_data = Column(JSON, nullable=True)  # Comprehensive AI analysis
    feedback_summary = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    job_description = relationship("JobDescription", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session")
    real_time_analysis = relationship("RealTimeAnalysis", back_populates="session")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # behavioral, technical, situational
    category = Column(String, nullable=True)  # leadership, problem-solving, etc.
    difficulty_level = Column(String, nullable=True)  # easy, medium, hard
    
    # Timing
    asked_at = Column(DateTime(timezone=True), nullable=True)
    response_start_time = Column(DateTime(timezone=True), nullable=True)
    response_end_time = Column(DateTime(timezone=True), nullable=True)
    response_duration_seconds = Column(Integer, nullable=True)
    
    # Response analysis
    user_response = Column(Text, nullable=True)
    response_transcript = Column(Text, nullable=True)
    
    # AI Scoring
    content_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    structure_score = Column(Float, nullable=True)  # STAR method adherence
    
    # Detailed analysis
    analysis_data = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    suggested_improvements = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")

class RealTimeAnalysis(Base):
    __tablename__ = "real_time_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    analysis_type = Column(String, nullable=False)  # facial, vocal, posture, content
    
    # Analysis results
    confidence_level = Column(Float, nullable=True)
    emotion_detected = Column(String, nullable=True)
    facial_expression_data = Column(JSON, nullable=True)
    vocal_analysis_data = Column(JSON, nullable=True)
    posture_data = Column(JSON, nullable=True)
    
    # Behavioral indicators
    eye_contact_score = Column(Float, nullable=True)
    speaking_pace = Column(Float, nullable=True)  # words per minute
    filler_words_count = Column(Integer, default=0)
    volume_level = Column(Float, nullable=True)
    
    # Alerts and feedback
    alert_triggered = Column(Boolean, default=False)
    alert_type = Column(String, nullable=True)  # distraction, low_confidence, etc.
    feedback_message = Column(String, nullable=True)
    
    # Raw data
    raw_analysis_data = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="real_time_analysis")

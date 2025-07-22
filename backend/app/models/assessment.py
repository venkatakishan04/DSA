from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assessment details
    assessment_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    assessment_type = Column(String, nullable=False)  # coding, mcq, aptitude
    category = Column(String, nullable=True)  # algorithms, system-design, etc.
    difficulty_level = Column(String, nullable=False)  # easy, medium, hard
    
    # Timing
    time_limit_minutes = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Status and results
    status = Column(String, default="not_started")  # not_started, in_progress, completed, timeout
    overall_score = Column(Float, nullable=True)
    max_possible_score = Column(Float, nullable=False)
    percentage_score = Column(Float, nullable=True)
    
    # Detailed results
    results_data = Column(JSON, nullable=True)  # Detailed breakdown
    feedback = Column(Text, nullable=True)
    ai_review = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    coding_problems = relationship("CodingProblem", back_populates="assessment")
    mcq_questions = relationship("MCQQuestion", back_populates="assessment")

class CodingProblem(Base):
    __tablename__ = "coding_problems"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    
    # Problem details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False)  # easy, medium, hard
    category = Column(String, nullable=True)  # arrays, strings, dynamic-programming
    
    # Problem constraints
    time_limit_seconds = Column(Integer, default=30)
    memory_limit_mb = Column(Integer, default=128)
    allowed_languages = Column(JSON, nullable=True)
    
    # Test cases
    sample_input = Column(Text, nullable=True)
    sample_output = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=False)  # Hidden test cases
    
    # Solution tracking
    user_code = Column(Text, nullable=True)
    programming_language = Column(String, nullable=True)
    submission_time = Column(DateTime(timezone=True), nullable=True)
    
    # Execution results
    execution_status = Column(String, nullable=True)  # passed, failed, timeout, error
    test_cases_passed = Column(Integer, default=0)
    total_test_cases = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    
    # AI Code Review
    code_quality_score = Column(Float, nullable=True)
    time_complexity = Column(String, nullable=True)
    space_complexity = Column(String, nullable=True)
    code_review_feedback = Column(Text, nullable=True)
    suggested_improvements = Column(JSON, nullable=True)
    
    # Detailed results
    execution_results = Column(JSON, nullable=True)
    error_messages = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="coding_problems")

class MCQQuestion(Base):
    __tablename__ = "mcq_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # aptitude, communication, technical
    category = Column(String, nullable=True)  # logical-reasoning, verbal, numerical
    difficulty = Column(String, nullable=False)  # easy, medium, hard
    
    # Options and answers
    options = Column(JSON, nullable=False)  # List of options
    correct_answer = Column(String, nullable=False)  # Correct option key
    user_answer = Column(String, nullable=True)  # User's selected option
    
    # Timing
    time_allocated_seconds = Column(Integer, default=60)
    time_taken_seconds = Column(Integer, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Scoring
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Float, default=0.0)
    max_points = Column(Float, default=1.0)
    
    # AI-generated explanation
    explanation = Column(Text, nullable=True)
    detailed_solution = Column(Text, nullable=True)
    learning_resources = Column(JSON, nullable=True)  # Links to study materials
    
    # Question metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="mcq_questions")

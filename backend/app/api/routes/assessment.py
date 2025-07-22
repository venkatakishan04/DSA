from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User
from app.models.assessment import Assessment, CodingProblem, MCQQuestion

router = APIRouter()

# Pydantic models
class AssessmentCreate(BaseModel):
    title: str
    assessment_type: str  # coding, mcq, aptitude
    category: Optional[str] = None
    difficulty_level: str  # easy, medium, hard
    time_limit_minutes: int

class AssessmentResponse(BaseModel):
    id: int
    assessment_id: str
    title: str
    assessment_type: str
    category: Optional[str]
    difficulty_level: str
    time_limit_minutes: int
    status: str
    overall_score: Optional[float]
    percentage_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CodingProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    category: Optional[str]
    sample_input: Optional[str]
    sample_output: Optional[str]
    user_code: Optional[str]
    programming_language: Optional[str]
    execution_status: Optional[str]
    test_cases_passed: int
    total_test_cases: int
    code_quality_score: Optional[float]
    
    class Config:
        from_attributes = True

class CodeSubmission(BaseModel):
    code: str
    programming_language: str

@router.post("/create", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new assessment"""
    try:
        assessment_id = str(uuid.uuid4())
        
        assessment = Assessment(
            user_id=current_user.id,
            assessment_id=assessment_id,
            title=assessment_data.title,
            assessment_type=assessment_data.assessment_type,
            category=assessment_data.category,
            difficulty_level=assessment_data.difficulty_level,
            time_limit_minutes=assessment_data.time_limit_minutes,
            max_possible_score=100.0,
            status="not_started"
        )
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        # Generate problems/questions based on type
        if assessment_data.assessment_type == "coding":
            await generate_coding_problems(db, assessment.id, assessment_data.difficulty_level)
        elif assessment_data.assessment_type in ["mcq", "aptitude"]:
            await generate_mcq_questions(db, assessment.id, assessment_data.assessment_type)
        
        return AssessmentResponse.from_orm(assessment)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assessment"
        )

@router.get("/list", response_model=List[AssessmentResponse])
async def get_assessments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's assessments"""
    try:
        assessments = db.query(Assessment).filter(
            Assessment.user_id == current_user.id
        ).order_by(Assessment.created_at.desc()).all()
        
        return [AssessmentResponse.from_orm(assessment) for assessment in assessments]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assessments"
        )

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific assessment"""
    try:
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.user_id == current_user.id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        return AssessmentResponse.from_orm(assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assessment"
        )

@router.post("/{assessment_id}/start")
async def start_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start an assessment"""
    try:
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.user_id == current_user.id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        if assessment.status != "not_started":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment already started or completed"
            )
        
        assessment.status = "in_progress"
        assessment.started_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Assessment started", "assessment_id": assessment_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start assessment"
        )

@router.get("/{assessment_id}/coding-problems", response_model=List[CodingProblemResponse])
async def get_coding_problems(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get coding problems for assessment"""
    try:
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.user_id == current_user.id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        problems = db.query(CodingProblem).filter(
            CodingProblem.assessment_id == assessment.id
        ).all()
        
        return [CodingProblemResponse.from_orm(problem) for problem in problems]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coding problems"
        )

@router.post("/{assessment_id}/coding-problems/{problem_id}/submit")
async def submit_code(
    assessment_id: str,
    problem_id: int,
    submission: CodeSubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit code for a coding problem"""
    try:
        # Verify assessment and problem ownership
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.user_id == current_user.id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        problem = db.query(CodingProblem).filter(
            CodingProblem.id == problem_id,
            CodingProblem.assessment_id == assessment.id
        ).first()
        
        if not problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coding problem not found"
            )
        
        # Update problem with submission
        problem.user_code = submission.code
        problem.programming_language = submission.programming_language
        problem.submission_time = datetime.utcnow()
        
        # Mock execution results (in production, would execute in sandbox)
        problem.execution_status = "passed"
        problem.test_cases_passed = 3
        problem.total_test_cases = 3
        problem.execution_time_ms = 150
        problem.memory_used_mb = 12.5
        problem.code_quality_score = 0.85
        
        db.commit()
        
        return {
            "message": "Code submitted successfully",
            "execution_status": problem.execution_status,
            "test_cases_passed": problem.test_cases_passed,
            "total_test_cases": problem.total_test_cases
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit code"
        )

# Helper functions
async def generate_coding_problems(db: Session, assessment_id: int, difficulty: str):
    """Generate coding problems for assessment"""
    problems_data = [
        {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "difficulty": difficulty,
            "category": "arrays",
            "sample_input": "[2,7,11,15], target = 9",
            "sample_output": "[0,1]",
            "test_cases": [
                {"input": "[2,7,11,15], 9", "output": "[0,1]"},
                {"input": "[3,2,4], 6", "output": "[1,2]"},
                {"input": "[3,3], 6", "output": "[0,1]"}
            ]
        }
    ]
    
    for problem_data in problems_data:
        problem = CodingProblem(
            assessment_id=assessment_id,
            title=problem_data["title"],
            description=problem_data["description"],
            difficulty=problem_data["difficulty"],
            category=problem_data["category"],
            sample_input=problem_data["sample_input"],
            sample_output=problem_data["sample_output"],
            test_cases=problem_data["test_cases"],
            total_test_cases=len(problem_data["test_cases"]),
            allowed_languages=["python", "javascript", "java", "cpp"]
        )
        db.add(problem)
    
    db.commit()

async def generate_mcq_questions(db: Session, assessment_id: int, question_type: str):
    """Generate MCQ questions for assessment"""
    questions_data = [
        {
            "question_text": "What is the time complexity of binary search?",
            "question_type": question_type,
            "category": "algorithms",
            "difficulty": "medium",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "correct_answer": "O(log n)",
            "explanation": "Binary search divides the search space in half with each comparison, resulting in O(log n) time complexity."
        }
    ]
    
    for question_data in questions_data:
        question = MCQQuestion(
            assessment_id=assessment_id,
            question_text=question_data["question_text"],
            question_type=question_data["question_type"],
            category=question_data["category"],
            difficulty=question_data["difficulty"],
            options=question_data["options"],
            correct_answer=question_data["correct_answer"],
            explanation=question_data["explanation"]
        )
        db.add(question)
    
    db.commit()

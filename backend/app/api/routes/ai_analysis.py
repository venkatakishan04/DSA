from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User
from app.services.ai_service import AIAnalysisService

router = APIRouter()
ai_service = AIAnalysisService()

# Pydantic models
class QuestionGenerationRequest(BaseModel):
    job_description: str
    resume_content: Optional[str] = None
    interview_type: str  # behavioral, technical, situational
    difficulty_level: str = "medium"
    num_questions: int = 5

class GeneratedQuestion(BaseModel):
    question_text: str
    question_type: str
    category: str
    difficulty_level: str
    expected_answer_structure: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None

class AnalysisRequest(BaseModel):
    text_content: str
    analysis_type: str  # sentiment, emotion, content_quality
    context: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float
    timestamp: datetime

@router.post("/generate-questions", response_model=List[GeneratedQuestion])
async def generate_interview_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI-powered interview questions"""
    try:
        # Mock question generation (in production, would use AI service)
        questions = [
            GeneratedQuestion(
                question_text="Tell me about a time when you had to work with a difficult team member. How did you handle the situation?",
                question_type="behavioral",
                category="teamwork",
                difficulty_level=request.difficulty_level,
                expected_answer_structure="STAR method (Situation, Task, Action, Result)",
                evaluation_criteria=[
                    "Clear situation description",
                    "Specific actions taken",
                    "Positive outcome",
                    "Learning or growth demonstrated"
                ]
            ),
            GeneratedQuestion(
                question_text="Describe your approach to debugging a complex software issue.",
                question_type="technical",
                category="problem-solving",
                difficulty_level=request.difficulty_level,
                expected_answer_structure="Systematic approach with specific steps",
                evaluation_criteria=[
                    "Logical debugging process",
                    "Use of appropriate tools",
                    "Problem isolation techniques",
                    "Documentation and communication"
                ]
            ),
            GeneratedQuestion(
                question_text="How would you prioritize features for a new product launch?",
                question_type="situational",
                category="decision-making",
                difficulty_level=request.difficulty_level,
                expected_answer_structure="Framework-based approach",
                evaluation_criteria=[
                    "Clear prioritization framework",
                    "Consideration of stakeholders",
                    "Data-driven decision making",
                    "Risk assessment"
                ]
            )
        ]
        
        return questions[:request.num_questions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions"
        )

@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text_content(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze text content using AI"""
    try:
        if not ai_service.is_initialized:
            await ai_service.initialize_models()
        
        results = {}
        
        if request.analysis_type == "sentiment":
            # Sentiment analysis
            sentiment_result = ai_service.sentiment_analyzer(request.text_content)
            results = {
                "sentiment": sentiment_result[0]["label"] if sentiment_result else "neutral",
                "confidence": sentiment_result[0]["score"] if sentiment_result else 0.5
            }
            
        elif request.analysis_type == "emotion":
            # Emotion analysis
            emotion_result = ai_service.emotion_analyzer(request.text_content)
            results = {
                "emotion": emotion_result[0]["label"] if emotion_result else "neutral",
                "confidence": emotion_result[0]["score"] if emotion_result else 0.5
            }
            
        elif request.analysis_type == "content_quality":
            # Content quality analysis
            word_count = len(request.text_content.split())
            filler_words = ["um", "uh", "like", "you know", "actually", "basically"]
            filler_count = sum(request.text_content.lower().count(word) for word in filler_words)
            
            results = {
                "word_count": word_count,
                "filler_words_count": filler_count,
                "clarity_score": max(0, 1 - (filler_count / max(word_count, 1))),
                "structure_score": 0.8,  # Mock score
                "relevance_score": 0.75  # Mock score
            }
        
        return AnalysisResponse(
            analysis_type=request.analysis_type,
            results=results,
            confidence_score=results.get("confidence", 0.8),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze text content"
        )

@router.get("/feedback-suggestions")
async def get_feedback_suggestions(
    confidence_score: float,
    eye_contact_score: float,
    speaking_pace: float,
    filler_words_count: int,
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-generated feedback suggestions"""
    try:
        suggestions = []
        
        # Confidence-based suggestions
        if confidence_score < 0.5:
            suggestions.extend([
                "Take deep breaths to calm your nerves",
                "Practice power poses before the interview",
                "Prepare specific examples using the STAR method"
            ])
        elif confidence_score < 0.7:
            suggestions.extend([
                "You're doing well! Try to speak with more conviction",
                "Use confident body language - sit up straight"
            ])
        
        # Eye contact suggestions
        if eye_contact_score < 0.6:
            suggestions.extend([
                "Maintain eye contact with the camera",
                "Look directly at the interviewer when speaking",
                "Avoid looking down or away frequently"
            ])
        
        # Speaking pace suggestions
        if speaking_pace > 180:  # Too fast
            suggestions.append("Slow down your speaking pace for better clarity")
        elif speaking_pace < 120:  # Too slow
            suggestions.append("Try to speak a bit faster to maintain engagement")
        
        # Filler words suggestions
        if filler_words_count > 5:
            suggestions.extend([
                "Reduce filler words like 'um', 'uh', 'like'",
                "Pause instead of using filler words",
                "Practice speaking more deliberately"
            ])
        
        # General positive reinforcement
        if not suggestions:
            suggestions.append("Great job! Keep up the excellent communication!")
        
        return {
            "suggestions": suggestions,
            "overall_score": (confidence_score + eye_contact_score) / 2,
            "areas_for_improvement": [
                "confidence" if confidence_score < 0.7 else None,
                "eye_contact" if eye_contact_score < 0.7 else None,
                "speaking_pace" if speaking_pace < 120 or speaking_pace > 180 else None,
                "filler_words" if filler_words_count > 5 else None
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate feedback suggestions"
        )

@router.post("/evaluate-answer")
async def evaluate_interview_answer(
    question: str,
    answer: str,
    expected_criteria: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate an interview answer using AI"""
    try:
        # Mock evaluation (in production, would use sophisticated AI analysis)
        word_count = len(answer.split())
        
        # Basic scoring
        content_score = min(1.0, word_count / 100)  # Longer answers get higher scores
        structure_score = 0.8 if "situation" in answer.lower() or "example" in answer.lower() else 0.5
        relevance_score = 0.9 if any(keyword in answer.lower() for keyword in question.lower().split()) else 0.6
        clarity_score = 0.8  # Mock score
        
        overall_score = (content_score + structure_score + relevance_score + clarity_score) / 4
        
        # Generate feedback
        feedback = []
        if content_score < 0.7:
            feedback.append("Provide more detailed examples and explanations")
        if structure_score < 0.7:
            feedback.append("Use the STAR method to structure your answer")
        if relevance_score < 0.7:
            feedback.append("Make sure your answer directly addresses the question")
        if clarity_score < 0.7:
            feedback.append("Speak more clearly and avoid filler words")
        
        if not feedback:
            feedback.append("Excellent answer! Well structured and comprehensive.")
        
        return {
            "overall_score": overall_score,
            "detailed_scores": {
                "content": content_score,
                "structure": structure_score,
                "relevance": relevance_score,
                "clarity": clarity_score
            },
            "feedback": feedback,
            "strengths": [
                "Good use of specific examples" if "example" in answer.lower() else None,
                "Clear communication" if clarity_score > 0.7 else None,
                "Relevant content" if relevance_score > 0.7 else None
            ],
            "improvement_areas": [
                "Add more specific details" if content_score < 0.7 else None,
                "Use STAR method structure" if structure_score < 0.7 else None,
                "Stay more focused on the question" if relevance_score < 0.7 else None
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate answer"
        )

@router.get("/model-status")
async def get_ai_model_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of AI models"""
    try:
        return {
            "models_initialized": ai_service.is_initialized,
            "available_models": {
                "whisper": ai_service.whisper_model is not None,
                "emotion_analyzer": ai_service.emotion_analyzer is not None,
                "sentiment_analyzer": ai_service.sentiment_analyzer is not None,
                "face_detection": ai_service.face_mesh is not None,
                "pose_detection": ai_service.pose_detector is not None
            },
            "status": "ready" if ai_service.is_initialized else "initializing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model status"
        )

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User, Resume
from app.services.auth_service import auth_service

router = APIRouter()

# Pydantic models
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    current_position: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    education: Optional[Dict[str, Any]] = None

class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone_number: Optional[str]
    bio: Optional[str]
    current_position: Optional[str]
    experience_years: Optional[int]
    skills: Optional[List[str]]
    education: Optional[Dict[str, Any]]
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: int
    file_name: Optional[str]
    parsed_content: Optional[Dict[str, Any]]
    skills: Optional[List[str]]
    experience: Optional[List[Dict[str, Any]]]
    education: Optional[List[Dict[str, Any]]]
    upload_date: str
    is_active: bool
    
    class Config:
        from_attributes = True

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get user profile"""
    return UserProfileResponse.from_orm(current_user)

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        updated_user = auth_service.update_user_profile(
            db, current_user.id, profile_data.dict(exclude_unset=True)
        )
        return UserProfileResponse.from_orm(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post("/resume/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and parse resume"""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOC, and DOCX files are allowed"
            )
        
        # Save file (in production, use cloud storage)
        file_path = f"uploads/resumes/{current_user.id}_{file.filename}"
        
        # Parse resume content (placeholder - would use actual parsing)
        parsed_content = {
            "name": current_user.full_name,
            "email": current_user.email,
            "skills": ["Python", "JavaScript", "React"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Software Developer",
                    "duration": "2020-2023"
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "Computer Science",
                    "year": "2020"
                }
            ]
        }
        
        # Create resume record
        resume = Resume(
            user_id=current_user.id,
            file_path=file_path,
            file_name=file.filename,
            file_size=len(await file.read()),
            parsed_content=parsed_content,
            skills=parsed_content.get("skills", []),
            experience=parsed_content.get("experience", []),
            education=parsed_content.get("education", [])
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return ResumeResponse.from_orm(resume)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload resume"
        )

@router.get("/resumes", response_model=List[ResumeResponse])
async def get_user_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's resumes"""
    try:
        resumes = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        ).order_by(Resume.upload_date.desc()).all()
        
        return [ResumeResponse.from_orm(resume) for resume in resumes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resumes"
        )

@router.delete("/resume/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    try:
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume.is_active = False
        db.commit()
        
        return {"message": "Resume deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume"
        )

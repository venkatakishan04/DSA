from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, interview, assessment, user, ai_analysis
from app.core.websocket_manager import WebSocketManager
from app.services.ai_service import AIAnalysisService

# Create database tables
Base.metadata.create_all(bind=engine)

# WebSocket manager for real-time communication
websocket_manager = WebSocketManager()
ai_service = AIAnalysisService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 HireSmart AI Backend Starting...")
    await ai_service.initialize_models()
    print("✅ AI Models Loaded Successfully")
    yield
    # Shutdown
    print("🛑 HireSmart AI Backend Shutting Down...")
    await ai_service.cleanup()

# Initialize FastAPI app
app = FastAPI(
    title="HireSmart AI API",
    description="AI-Powered Mock Interview and Assessment Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(interview.router, prefix="/api/v1/interview", tags=["Interview"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Assessment"])
app.include_router(ai_analysis.router, prefix="/api/v1/ai", tags=["AI Analysis"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Welcome to HireSmart AI API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_models": "loaded",
        "services": {
            "interview": "active",
            "assessment": "active",
            "ai_analysis": "active"
        }
    }

# WebSocket endpoint for real-time interview
@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Receive data from client (audio/video chunks)
            data = await websocket.receive_bytes()
            
            # Process with AI service
            analysis_result = await ai_service.process_realtime_data(data, session_id)
            
            # Send real-time feedback
            if analysis_result:
                await websocket_manager.send_personal_message(
                    analysis_result, session_id
                )
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        print(f"Client {session_id} disconnected from interview session")

# WebSocket endpoint for coding assessment
@app.websocket("/ws/coding/{session_id}")
async def coding_websocket(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Receive code from client
            code_data = await websocket.receive_json()
            
            # Process code execution
            execution_result = await ai_service.execute_code(
                code_data["code"], 
                code_data["language"],
                session_id
            )
            
            # Send execution results
            await websocket_manager.send_personal_message(
                execution_result, session_id
            )
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        print(f"Client {session_id} disconnected from coding session")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

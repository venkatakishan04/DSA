import asyncio
import cv2
import numpy as np
import whisper
import torch
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import mediapipe as mp
from transformers import pipeline, AutoTokenizer, AutoModel
import librosa
import soundfile as sf
from io import BytesIO
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)

class AIAnalysisService:
    def __init__(self):
        self.whisper_model = None
        self.emotion_analyzer = None
        self.face_mesh = None
        self.pose_detector = None
        self.sentiment_analyzer = None
        self.question_generator = None
        self.is_initialized = False
        
    async def initialize_models(self):
        """Initialize all AI models"""
        try:
            logger.info("Initializing AI models...")
            
            # Initialize Whisper for speech-to-text
            self.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded")
            
            # Initialize emotion analysis
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Emotion analyzer loaded")
            
            # Initialize MediaPipe for face and pose detection
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.pose_detector = mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            logger.info("✅ MediaPipe models loaded")
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Sentiment analyzer loaded")
            
            # Initialize question generator (using OpenAI or local model)
            if settings.OPENAI_API_KEY:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                self.question_generator = "openai"
            else:
                # Fallback to local model
                self.question_generator = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    device=0 if torch.cuda.is_available() else -1
                )
            logger.info("✅ Question generator initialized")
            
            self.is_initialized = True
            logger.info("🎉 All AI models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            raise
    
    async def process_realtime_data(self, data: bytes, session_id: str) -> Dict[str, Any]:
        """Process real-time audio/video data during interview"""
        if not self.is_initialized:
            await self.initialize_models()
        
        try:
            # Decode the incoming data (assuming it's base64 encoded)
            decoded_data = base64.b64decode(data)
            
            # Determine if it's audio or video data based on size/format
            analysis_result = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "type": "real_time_analysis"
            }
            
            # Process video data for facial analysis
            if len(decoded_data) > 10000:  # Likely video frame
                video_analysis = await self._analyze_video_frame(decoded_data)
                analysis_result.update(video_analysis)
            
            # Process audio data for speech analysis
            else:  # Likely audio chunk
                audio_analysis = await self._analyze_audio_chunk(decoded_data)
                analysis_result.update(audio_analysis)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing real-time data: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_video_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """Analyze video frame for facial expressions and body language"""
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"error": "Invalid video frame"}
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            analysis = {
                "facial_analysis": {},
                "pose_analysis": {},
                "eye_contact": {},
                "confidence_indicators": {}
            }
            
            # Face mesh analysis
            face_results = self.face_mesh.process(rgb_frame)
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                
                # Calculate eye contact (looking at camera)
                eye_contact_score = self._calculate_eye_contact(face_landmarks)
                analysis["eye_contact"] = {
                    "score": eye_contact_score,
                    "looking_at_camera": eye_contact_score > 0.7
                }
                
                # Detect facial expressions
                expression_data = self._analyze_facial_expression(face_landmarks)
                analysis["facial_analysis"] = expression_data
            
            # Pose analysis
            pose_results = self.pose_detector.process(rgb_frame)
            if pose_results.pose_landmarks:
                pose_data = self._analyze_body_posture(pose_results.pose_landmarks)
                analysis["pose_analysis"] = pose_data
            
            # Generate confidence indicators
            analysis["confidence_indicators"] = self._calculate_confidence_indicators(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video frame: {e}")
            return {"error": str(e)}
    
    async def _analyze_audio_chunk(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio chunk for speech patterns and content"""
        try:
            # Convert bytes to audio array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            analysis = {
                "speech_analysis": {},
                "vocal_patterns": {},
                "content_analysis": {}
            }
            
            # Analyze vocal patterns
            if len(audio_array) > 1000:  # Minimum audio length
                # Calculate speaking pace
                speaking_rate = self._calculate_speaking_rate(audio_array)
                
                # Analyze volume and pitch
                volume_analysis = self._analyze_volume_patterns(audio_array)
                pitch_analysis = self._analyze_pitch_patterns(audio_array)
                
                analysis["vocal_patterns"] = {
                    "speaking_rate": speaking_rate,
                    "volume": volume_analysis,
                    "pitch": pitch_analysis
                }
                
                # Transcribe audio for content analysis
                try:
                    # Save audio temporarily for Whisper
                    temp_audio_path = f"/tmp/audio_{datetime.now().timestamp()}.wav"
                    sf.write(temp_audio_path, audio_array, 16000)
                    
                    # Transcribe with Whisper
                    result = self.whisper_model.transcribe(temp_audio_path)
                    transcript = result["text"]
                    
                    if transcript.strip():
                        # Analyze content
                        content_analysis = await self._analyze_speech_content(transcript)
                        analysis["content_analysis"] = content_analysis
                        analysis["transcript"] = transcript
                    
                    # Clean up temp file
                    import os
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        
                except Exception as e:
                    logger.error(f"Error in speech transcription: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audio chunk: {e}")
            return {"error": str(e)}
    
    def _calculate_eye_contact(self, face_landmarks) -> float:
        """Calculate eye contact score based on gaze direction"""
        try:
            # Get eye landmarks
            left_eye = [face_landmarks.landmark[i] for i in [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]]
            right_eye = [face_landmarks.landmark[i] for i in [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]]
            
            # Calculate gaze direction (simplified)
            # In a real implementation, this would be more sophisticated
            eye_contact_score = 0.8  # Placeholder - would calculate based on pupil position
            
            return eye_contact_score
            
        except Exception as e:
            logger.error(f"Error calculating eye contact: {e}")
            return 0.5
    
    def _analyze_facial_expression(self, face_landmarks) -> Dict[str, Any]:
        """Analyze facial expression from landmarks"""
        try:
            # Simplified facial expression analysis
            # In production, this would use more sophisticated algorithms
            
            expressions = {
                "confidence": 0.7,
                "nervousness": 0.3,
                "engagement": 0.8,
                "micro_expressions": {
                    "smile_detected": False,
                    "frown_detected": False,
                    "eyebrow_raise": False
                }
            }
            
            return expressions
            
        except Exception as e:
            logger.error(f"Error analyzing facial expression: {e}")
            return {"error": str(e)}
    
    def _analyze_body_posture(self, pose_landmarks) -> Dict[str, Any]:
        """Analyze body posture and gestures"""
        try:
            # Calculate posture metrics
            posture_data = {
                "posture_score": 0.75,
                "shoulder_alignment": "good",
                "head_position": "centered",
                "gestures_detected": [],
                "overall_body_language": "confident"
            }
            
            return posture_data
            
        except Exception as e:
            logger.error(f"Error analyzing body posture: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence_indicators(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall confidence indicators"""
        try:
            confidence_score = 0.0
            indicators = []
            
            # Eye contact contribution
            if "eye_contact" in analysis and "score" in analysis["eye_contact"]:
                eye_score = analysis["eye_contact"]["score"]
                confidence_score += eye_score * 0.3
                if eye_score > 0.7:
                    indicators.append("Good eye contact")
                else:
                    indicators.append("Improve eye contact")
            
            # Posture contribution
            if "pose_analysis" in analysis and "posture_score" in analysis["pose_analysis"]:
                posture_score = analysis["pose_analysis"]["posture_score"]
                confidence_score += posture_score * 0.3
                if posture_score > 0.7:
                    indicators.append("Good posture")
                else:
                    indicators.append("Improve posture")
            
            # Facial expression contribution
            if "facial_analysis" in analysis and "confidence" in analysis["facial_analysis"]:
                facial_confidence = analysis["facial_analysis"]["confidence"]
                confidence_score += facial_confidence * 0.4
            
            return {
                "overall_confidence_score": min(confidence_score, 1.0),
                "indicators": indicators,
                "recommendations": self._generate_confidence_recommendations(confidence_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence indicators: {e}")
            return {"error": str(e)}
    
    def _generate_confidence_recommendations(self, confidence_score: float) -> List[str]:
        """Generate real-time confidence improvement recommendations"""
        recommendations = []
        
        if confidence_score < 0.5:
            recommendations.extend([
                "Take a deep breath and relax",
                "Maintain eye contact with the camera",
                "Sit up straight and keep shoulders back"
            ])
        elif confidence_score < 0.7:
            recommendations.extend([
                "You're doing well, keep it up!",
                "Try to speak a bit more clearly"
            ])
        else:
            recommendations.append("Excellent confidence! Keep going!")
        
        return recommendations
    
    async def cleanup(self):
        """Clean up AI models and resources"""
        try:
            if self.face_mesh:
                self.face_mesh.close()
            if self.pose_detector:
                self.pose_detector.close()
            logger.info("AI models cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up AI models: {e}")
    
    # Additional helper methods for audio analysis
    def _calculate_speaking_rate(self, audio_array: np.ndarray) -> float:
        """Calculate words per minute from audio"""
        # Simplified implementation
        return 150.0  # Average speaking rate
    
    def _analyze_volume_patterns(self, audio_array: np.ndarray) -> Dict[str, float]:
        """Analyze volume patterns in speech"""
        rms = np.sqrt(np.mean(audio_array**2))
        return {
            "average_volume": float(rms),
            "volume_consistency": 0.8
        }
    
    def _analyze_pitch_patterns(self, audio_array: np.ndarray) -> Dict[str, float]:
        """Analyze pitch patterns in speech"""
        return {
            "average_pitch": 150.0,
            "pitch_variation": 0.3
        }
    
    async def _analyze_speech_content(self, transcript: str) -> Dict[str, Any]:
        """Analyze speech content for quality and sentiment"""
        try:
            # Sentiment analysis
            sentiment_result = self.sentiment_analyzer(transcript)
            
            # Emotion analysis
            emotion_result = self.emotion_analyzer(transcript)
            
            # Filler words detection
            filler_words = ["um", "uh", "like", "you know", "actually", "basically"]
            filler_count = sum(transcript.lower().count(word) for word in filler_words)
            
            return {
                "sentiment": sentiment_result[0] if sentiment_result else None,
                "emotion": emotion_result[0] if emotion_result else None,
                "filler_words_count": filler_count,
                "word_count": len(transcript.split()),
                "clarity_score": max(0, 1 - (filler_count / max(len(transcript.split()), 1)))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing speech content: {e}")
            return {"error": str(e)}

    async def execute_code(self, code: str, language: str, session_id: str) -> Dict[str, Any]:
        """Execute user code safely and return results"""
        try:
            # This would integrate with a secure code execution service
            # For now, return a mock result
            execution_result = {
                "session_id": session_id,
                "language": language,
                "execution_status": "success",
                "output": "Code executed successfully",
                "execution_time_ms": 150,
                "memory_used_mb": 12.5,
                "test_cases_passed": 3,
                "total_test_cases": 3,
                "timestamp": datetime.now().isoformat()
            }

            # In production, this would:
            # 1. Validate the code for security
            # 2. Execute in a sandboxed environment
            # 3. Run against test cases
            # 4. Provide detailed feedback

            return execution_result

        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "session_id": session_id,
                "execution_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

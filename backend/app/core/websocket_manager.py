from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, dict] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0,
            "last_activity": asyncio.get_event_loop().time()
        }
        logger.info(f"WebSocket connected: {session_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connected to HireSmart AI",
            "timestamp": asyncio.get_event_loop().time()
        }, session_id)
    
    def disconnect(self, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.connection_metadata:
            del self.connection_metadata[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send a message to a specific session"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message))
                
                # Update metadata
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["message_count"] += 1
                    self.connection_metadata[session_id]["last_activity"] = asyncio.get_event_loop().time()
                    
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                # Remove broken connection
                self.disconnect(session_id)
    
    async def send_binary_message(self, data: bytes, session_id: str):
        """Send binary data to a specific session"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_bytes(data)
                
                # Update metadata
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["message_count"] += 1
                    self.connection_metadata[session_id]["last_activity"] = asyncio.get_event_loop().time()
                    
            except Exception as e:
                logger.error(f"Error sending binary data to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_message(self, message: dict):
        """Broadcast a message to all connected sessions"""
        if not self.active_connections:
            return
            
        # Create list of tasks for concurrent sending
        tasks = []
        for session_id in list(self.active_connections.keys()):
            task = self.send_personal_message(message, session_id)
            tasks.append(task)
        
        # Execute all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_real_time_feedback(self, feedback_data: dict, session_id: str):
        """Send real-time AI feedback during interview"""
        feedback_message = {
            "type": "real_time_feedback",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "feedback": feedback_data
        }
        await self.send_personal_message(feedback_message, session_id)
    
    async def send_coding_result(self, result_data: dict, session_id: str):
        """Send coding execution results"""
        result_message = {
            "type": "coding_execution_result",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "result": result_data
        }
        await self.send_personal_message(result_message, session_id)
    
    async def send_interview_question(self, question_data: dict, session_id: str):
        """Send new interview question"""
        question_message = {
            "type": "interview_question",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "question": question_data
        }
        await self.send_personal_message(question_message, session_id)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_info(self, session_id: str) -> dict:
        """Get connection metadata for a session"""
        return self.connection_metadata.get(session_id, {})
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    async def cleanup_inactive_connections(self, timeout_seconds: int = 300):
        """Clean up connections that have been inactive for too long"""
        current_time = asyncio.get_event_loop().time()
        inactive_sessions = []
        
        for session_id, metadata in self.connection_metadata.items():
            if current_time - metadata["last_activity"] > timeout_seconds:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Cleaning up inactive connection: {session_id}")
            self.disconnect(session_id)

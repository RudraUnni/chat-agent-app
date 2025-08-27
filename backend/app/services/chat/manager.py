from typing import Dict, Optional, List
from datetime import datetime
import uuid

from app.workflows.base import WorkflowContext
from app.models.chat import ChatMessage


class ChatSession:
    """Represents a chat session"""
    
    def __init__(self, session_id: str = None, user_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.messages: List[ChatMessage] = []
        self.context = WorkflowContext(
            session_id=self.session_id,
            user_id=user_id
        )
        self.message_count = 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.message_count += 1
    
    def add_message(self, role: str, content: str) -> ChatMessage:
        """Add a message to the conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(message)
        self.update_activity()
        return message
    
    def add_user_message(self, content: str) -> ChatMessage:
        """Add a user message to the conversation"""
        return self.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> ChatMessage:
        """Add an assistant message to the conversation"""
        return self.add_message("assistant", content)
    
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the full conversation history"""
        return self.messages.copy()
    
    def get_messages_for_agent(self) -> List[Dict[str, str]]:
        """Get messages formatted for agent consumption (role + content)"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]


class ChatManager:
    """Manages chat sessions"""
    
    def __init__(self):
        self._sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(user_id=user_id)
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing session"""
        return self._sessions.get(session_id)
    
    def get_or_create_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ChatSession:
        """Get existing session or create new one"""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.update_activity()
            return session
        return self.create_session(user_id)
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def list_sessions(self) -> List[Dict]:
        """List all active sessions"""
        return [
            {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'message_count': session.message_count
            }
            for session in self._sessions.values()
        ]
    
    def cleanup_inactive_sessions(self, inactive_minutes: int = 30):
        """Remove inactive sessions"""
        now = datetime.now()
        to_delete = []
        
        for session_id, session in self._sessions.items():
            inactive_time = (now - session.last_activity).total_seconds() / 60
            if inactive_time > inactive_minutes:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
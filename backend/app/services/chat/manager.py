from typing import Dict, Optional, List
from datetime import datetime
import uuid

from app.workflows.base import WorkflowContext
from app.database.connection import AsyncSessionLocal
from app.database.models import Conversation
from sqlalchemy.future import select


class ChatSession:
    """Represents a chat session"""
    
    def __init__(self, session_id: str = None, user_id: str = None, conversation_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.conversation_id = conversation_id or self.session_id  # Use session_id as conversation_id by default
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.context = WorkflowContext(
            session_id=self.session_id,
            user_id=user_id
        )
        self.message_count = 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.message_count += 1


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
    
    async def ensure_conversation_exists(self, session: ChatSession) -> str:
        """Ensure database conversation exists for session"""
        async with AsyncSessionLocal() as db:
            try:
                # Check if conversation exists
                stmt = select(Conversation).where(Conversation.id == session.conversation_id)
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    # Create new conversation
                    conversation = Conversation(
                        id=session.conversation_id,
                        user_id=session.user_id,
                        title="Chat Session"
                    )
                    db.add(conversation)
                    await db.commit()
                    
                return session.conversation_id
            except Exception as e:
                await db.rollback()
                raise e
    
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
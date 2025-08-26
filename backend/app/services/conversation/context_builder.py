from typing import List, Dict, Any
from app.database.models import Message


def format_messages_for_agent(messages: List[Message], current_message: str) -> List[Dict[str, str]]:
    """
    Format conversation history for agent consumption.
    
    Args:
        messages: List of previous messages from database
        current_message: The current user message
        
    Returns:
        List of messages in OpenAI chat format [{"role": "user/assistant", "content": "..."}]
    """
    formatted_messages = []
    
    # Convert previous messages to agent format
    for message in messages:
        formatted_messages.append({
            "role": message.role,
            "content": message.content
        })
    
    # Add current user message
    formatted_messages.append({
        "role": "user", 
        "content": current_message
    })
    
    return formatted_messages


def get_conversation_context(messages: List[Message], current_message: str, max_messages: int = 10) -> List[Dict[str, str]]:
    """
    Get conversation context with message limit.
    
    Args:
        messages: All previous messages from database
        current_message: Current user message
        max_messages: Maximum number of previous messages to include
        
    Returns:
        Formatted messages for agent
    """
    # Limit to last N messages to avoid context overflow
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
    
    return format_messages_for_agent(recent_messages, current_message)
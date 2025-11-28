"""
ClientSession Manager for MCP Server

This module manages conversation state and context for multi-turn interactions.
Each MCP client gets a unique session to maintain conversation history and context.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from threading import Lock
from pydantic import BaseModel

from src.config.mcp_config import (
    SESSION_MAX_AGE_HOURS,
    MAX_SESSIONS,
)

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Represents a message in a conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """Represents the state of a conversation session."""
    session_id: str
    created_at: datetime
    last_active: datetime
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "context": self.context,
        }


class SessionManager:
    """
    Manages ClientSessions for the MCP server.

    Features:
    - Create and retrieve sessions
    - Track conversation history
    - Store session context (uploaded files, preferences, etc.)
    - Auto-cleanup old sessions
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize the session manager."""
        self._sessions: Dict[str, ConversationState] = {}
        self._lock = Lock()
        logger.info("🔧 Session manager initialized")

    def create_session(self, session_id: str) -> ConversationState:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationState instance
        """
        with self._lock:
            if session_id in self._sessions:
                logger.warning(f"⚠️ Session {session_id} already exists, returning existing")
                return self._sessions[session_id]

            # Check if we've reached max sessions
            if len(self._sessions) >= MAX_SESSIONS:
                logger.warning(f"⚠️ Max sessions ({MAX_SESSIONS}) reached, cleaning up old sessions")
                self._cleanup_old_sessions(force=True)

            now = datetime.now()
            session = ConversationState(
                session_id=session_id,
                created_at=now,
                last_active=now
            )
            self._sessions[session_id] = session
            logger.info(f"✅ Created session: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[ConversationState]:
        """
        Get an existing session.

        Args:
            session_id: Session identifier

        Returns:
            ConversationState or None if not found
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                # Update last active time
                session.last_active = datetime.now()
            return session

    def get_or_create_session(self, session_id: str) -> ConversationState:
        """
        Get an existing session or create a new one.

        Args:
            session_id: Session identifier

        Returns:
            ConversationState instance
        """
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to a session's conversation history.

        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.warning(f"⚠️ Session {session_id} not found, creating new session")
                session = self.create_session(session_id)

            message = Message(
                role=role,
                content=content,
                metadata=metadata or {}
            )
            session.messages.append(message)
            session.last_active = datetime.now()

            logger.debug(f"📝 Added {role} message to session {session_id}")

    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return (most recent)

        Returns:
            List of messages
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return []

            messages = session.messages
            if limit:
                messages = messages[-limit:]

            return messages

    def update_context(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """
        Update session context.

        Context can store:
        - Uploaded file paths
        - User preferences
        - Current research topic
        - etc.

        Args:
            session_id: Session identifier
            key: Context key
            value: Context value
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.warning(f"⚠️ Session {session_id} not found, creating new session")
                session = self.create_session(session_id)

            session.context[key] = value
            session.last_active = datetime.now()

            logger.debug(f"🔄 Updated context for session {session_id}: {key}")

    def get_context(
        self,
        session_id: str,
        key: Optional[str] = None
    ) -> Any:
        """
        Get session context.

        Args:
            session_id: Session identifier
            key: Optional specific context key (returns all context if None)

        Returns:
            Context value or dict of all context
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None if key else {}

            if key:
                return session.context.get(key)
            return session.context.copy()

    def delete_session(self, session_id: str):
        """
        Delete a session.

        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"🗑️ Deleted session: {session_id}")

    def _cleanup_old_sessions(self, force: bool = False):
        """
        Remove old inactive sessions.

        Args:
            force: If True, removes oldest sessions even if not expired
        """
        with self._lock:
            now = datetime.now()
            max_age = timedelta(hours=SESSION_MAX_AGE_HOURS)

            sessions_to_delete = []

            for session_id, session in self._sessions.items():
                age = now - session.last_active
                if force or age > max_age:
                    sessions_to_delete.append(session_id)

            for session_id in sessions_to_delete:
                del self._sessions[session_id]

            if sessions_to_delete:
                logger.info(f"🧹 Cleaned up {len(sessions_to_delete)} old sessions")

    def cleanup_old_sessions(self, max_age_hours: Optional[int] = None):
        """
        Public method to trigger session cleanup.

        Args:
            max_age_hours: Optional override for max age
        """
        if max_age_hours:
            old_max_age = SESSION_MAX_AGE_HOURS
            # Temporarily override
            import src.config.mcp_config as config
            config.SESSION_MAX_AGE_HOURS = max_age_hours
            self._cleanup_old_sessions()
            config.SESSION_MAX_AGE_HOURS = old_max_age
        else:
            self._cleanup_old_sessions()

    def get_session_count(self) -> int:
        """Get the current number of active sessions."""
        with self._lock:
            return len(self._sessions)

    def list_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        with self._lock:
            return list(self._sessions.keys())


# Global singleton instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """
    Get the global session manager instance.

    Returns:
        SessionManager singleton
    """
    return _session_manager

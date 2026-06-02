"""
Conversation Session Manager - Track conversation history and context
Uses SQLite for lightweight persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import uuid


class SessionManager:
    """Manages conversation sessions and history"""
    
    def __init__(self, db_path: str = "data/sessions.db"):
        """Initialize SQLite database for sessions"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create tables if not exist
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    message_count INTEGER DEFAULT 0,
                    context TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    intent TEXT,
                    sentiment TEXT,
                    kb_context TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            conn.commit()
    
    def create_session(self, customer_id: str) -> str:
        """
        Create new conversation session
        
        Returns:
            session_id
        """
        session_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, customer_id, status)
                VALUES (?, ?, ?)
            """, (session_id, customer_id, 'active'))
            conn.commit()
        
        print(f"[SESSION] Created: {session_id[:8]}... for {customer_id}")
        return session_id
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        sentiment: Optional[str] = None,
        kb_context: Optional[str] = None
    ) -> bool:
        """
        Add message to session
        
        Args:
            session_id: Session ID
            role: "user" or "assistant"
            content: Message content
            intent: Detected intent (optional)
            sentiment: Sentiment label (optional)
            kb_context: Retrieved KB context (optional)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert message
                cursor.execute("""
                    INSERT INTO messages 
                    (session_id, role, content, intent, sentiment, kb_context)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, role, content, intent, sentiment, kb_context))
                
                # Update message count
                cursor.execute("""
                    UPDATE sessions 
                    SET message_count = message_count + 1
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
            
            return True
        except Exception as e:
            print(f"[SESSION] Add message error: {e}")
            return False
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all messages in a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[SESSION] Get history error: {e}")
            return []
    
    def close_session(self, session_id: str) -> bool:
        """Close a conversation session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET status = 'closed', end_time = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
            
            print(f"[SESSION] Closed: {session_id[:8]}...")
            return True
        except Exception as e:
            print(f"[SESSION] Close error: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"[SESSION] Get info error: {e}")
            return None


# Global session manager instance
session_manager = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager"""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager

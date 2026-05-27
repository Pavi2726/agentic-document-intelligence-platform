"""US-12: Conversation Context Management with Redis/MongoDB."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: redis not installed. Session caching will be disabled.")

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("Warning: pymongo not installed. Chat history persistence will be disabled.")

from app.core.config import settings


class ConversationContextManager:
    def __init__(self):
        self.redis_client = None
        self.mongo_client = None
        self.db = None
        self.json_storage_path = os.path.join(settings.UPLOAD_DIR, "chat_history.json")
        self._init_redis()
        self._init_mongo()
        self._init_json_storage()
    
    def _init_json_storage(self):
        """Initialize JSON file storage as fallback."""
        if not os.path.exists(self.json_storage_path):
            with open(self.json_storage_path, 'w') as f:
                json.dump({"sessions": {}, "messages": []}, f)
    
    def _load_json_storage(self):
        """Load data from JSON file."""
        try:
            with open(self.json_storage_path, 'r') as f:
                return json.load(f)
        except:
            return {"sessions": {}, "messages": []}
    
    def _save_json_storage(self, data):
        """Save data to JSON file."""
        try:
            with open(self.json_storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[JSON Storage] Failed to save: {e}")
    
    def _init_redis(self):
        """Initialize Redis for session memory (fast access)."""
        if not REDIS_AVAILABLE:
            self.redis_client = None
            return
            
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
        except Exception:
            self.redis_client = None
    
    def _init_mongo(self):
        """Initialize MongoDB for persistent chat history."""
        if not MONGO_AVAILABLE:
            self.mongo_client = None
            self.db = None
            return
            
        try:
            mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
            self.mongo_client = MongoClient(mongo_uri)
            self.db = self.mongo_client['document_intelligence']
            self.db.chat_history.create_index([("session_id", 1), ("timestamp", -1)])
            self.db.chat_sessions.create_index([("session_id", 1)])
        except Exception:
            self.mongo_client = None
            self.db = None
    
    def create_session(self, user_id: str = "default") -> str:
        """Create a new conversation session."""
        session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_id}",
                timedelta(hours=24),
                json.dumps({"user_id": user_id, "created_at": str(datetime.now())})
            )
        
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Add a message to conversation history."""
        message = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        }
        
        # Store in MongoDB for persistence
        if self.db is not None:
            self.db.chat_history.insert_one(message)
        else:
            # Fallback to JSON storage
            data = self._load_json_storage()
            data["messages"].append({
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "timestamp": str(message["timestamp"])
            })
            # Update session info
            if session_id not in data["sessions"]:
                data["sessions"][session_id] = {
                    "session_id": session_id,
                    "created_at": str(message["timestamp"]),
                    "message_count": 0
                }
            data["sessions"][session_id]["message_count"] += 1
            data["sessions"][session_id]["last_message"] = str(message["timestamp"])
            self._save_json_storage(data)
        
        # Cache recent messages in Redis
        if self.redis_client:
            key = f"chat:{session_id}"
            self.redis_client.lpush(key, json.dumps({
                "role": role,
                "content": content,
                "timestamp": str(message["timestamp"])
            }))
            self.redis_client.ltrim(key, 0, 49)  # Keep last 50 messages
            self.redis_client.expire(key, timedelta(hours=24))
    
    def get_context(self, session_id: str, limit: int = 10) -> list[dict]:
        """Get recent conversation context for multi-turn handling."""
        # Try Redis first (faster)
        if self.redis_client:
            key = f"chat:{session_id}"
            messages = self.redis_client.lrange(key, 0, limit - 1)
            if messages:
                return [json.loads(msg) for msg in messages]
        
        # Fallback to MongoDB
        if self.db is not None:
            cursor = self.db.chat_history.find(
                {"session_id": session_id}
            ).sort("timestamp", -1).limit(limit)
            
            return [{
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": str(msg["timestamp"])
            } for msg in cursor]
        
        # Fallback to JSON storage
        data = self._load_json_storage()
        session_messages = [
            msg for msg in data["messages"]
            if msg["session_id"] == session_id
        ]
        # Sort by timestamp descending and limit
        session_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        return session_messages[:limit]
    
    def get_full_history(self, session_id: str) -> list[dict]:
        """Get complete chat history from MongoDB or JSON."""
        if self.db is not None:
            cursor = self.db.chat_history.find(
                {"session_id": session_id}
            ).sort("timestamp", 1)
            
            return [{
                "role": msg["role"],
                "content": msg["content"],
                "metadata": msg.get("metadata", {}),
                "timestamp": str(msg["timestamp"])
            } for msg in cursor]
        
        # Fallback to JSON storage
        data = self._load_json_storage()
        session_messages = [
            msg for msg in data["messages"]
            if msg["session_id"] == session_id
        ]
        # Sort by timestamp ascending
        session_messages.sort(key=lambda x: x["timestamp"])
        return session_messages
    
    def delete_session(self, session_id: str):
        """Delete a conversation session."""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}", f"chat:{session_id}")
        
        if self.db is not None:
            self.db.chat_history.delete_many({"session_id": session_id})
        else:
            # Fallback to JSON storage
            data = self._load_json_storage()
            data["messages"] = [
                msg for msg in data["messages"]
                if msg["session_id"] != session_id
            ]
            if session_id in data["sessions"]:
                del data["sessions"][session_id]
            self._save_json_storage(data)
    
    def list_sessions(self, user_id: str = "default") -> list[dict]:
        """List all sessions for a user."""
        if self.db is not None:
            pipeline = [
                {"$match": {"session_id": {"$regex": f"^session_{user_id}_"}}},
                {"$group": {
                    "_id": "$session_id",
                    "last_message": {"$last": "$timestamp"},
                    "message_count": {"$sum": 1}
                }},
                {"$sort": {"last_message": -1}}
            ]
            
            return [{
                "session_id": doc["_id"],
                "last_message": str(doc["last_message"]),
                "message_count": doc["message_count"]
            } for doc in self.db.chat_history.aggregate(pipeline)]
        
        # Fallback to JSON storage
        data = self._load_json_storage()
        sessions = []
        for session_id, session_info in data["sessions"].items():
            if session_id.startswith(f"session_{user_id}_"):
                sessions.append({
                    "session_id": session_id,
                    "last_message": session_info.get("last_message", session_info.get("created_at", "")),
                    "message_count": session_info.get("message_count", 0)
                })
        # Sort by last_message descending
        sessions.sort(key=lambda x: x["last_message"], reverse=True)
        return sessions


context_manager = ConversationContextManager()

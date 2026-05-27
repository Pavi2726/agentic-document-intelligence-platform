"""User authentication and management."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings


class UserManager:
    def __init__(self):
        self.users_file = os.path.join(settings.UPLOAD_DIR, "users.json")
        self.sessions_file = os.path.join(settings.UPLOAD_DIR, "sessions.json")
        self._init_storage()
    
    def _init_storage(self):
        """Initialize user storage files."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f)
        
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump({"sessions": {}}, f)
    
    def _load_users(self):
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {"users": []}
    
    def _save_users(self, data):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_sessions(self):
        """Load sessions from file."""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except:
            return {"sessions": {}}
    
    def _save_sessions(self, data):
        """Save sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self, username: str) -> str:
        """Generate session token."""
        timestamp = str(datetime.now().timestamp())
        return hashlib.sha256(f"{username}{timestamp}".encode()).hexdigest()
    
    def register_user(self, username: str, password: str, email: str = "") -> dict:
        """Register a new user."""
        data = self._load_users()
        
        # Check if user already exists
        for user in data["users"]:
            if user["username"] == username:
                return {"success": False, "message": "Username already exists"}
        
        # Create new user
        user = {
            "username": username,
            "password": self._hash_password(password),
            "email": email,
            "created_at": str(datetime.now()),
            "last_login": None
        }
        
        data["users"].append(user)
        self._save_users(data)
        
        return {"success": True, "message": "User registered successfully"}
    
    def login_user(self, username: str, password: str) -> dict:
        """Login user and create session."""
        data = self._load_users()
        
        # Find user
        user = None
        for u in data["users"]:
            if u["username"] == username:
                user = u
                break
        
        if not user:
            return {"success": False, "message": "Invalid username or password"}
        
        # Verify password
        if user["password"] != self._hash_password(password):
            return {"success": False, "message": "Invalid username or password"}
        
        # Update last login
        user["last_login"] = str(datetime.now())
        self._save_users(data)
        
        # Create session
        token = self._generate_token(username)
        sessions = self._load_sessions()
        sessions["sessions"][token] = {
            "username": username,
            "created_at": str(datetime.now()),
            "expires_at": str(datetime.now() + timedelta(days=7))
        }
        self._save_sessions(sessions)
        
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "username": username,
            "email": user.get("email", "")
        }
    
    def logout_user(self, token: str) -> dict:
        """Logout user and remove session."""
        sessions = self._load_sessions()
        
        if token in sessions["sessions"]:
            del sessions["sessions"][token]
            self._save_sessions(sessions)
            return {"success": True, "message": "Logged out successfully"}
        
        return {"success": False, "message": "Invalid session"}
    
    def verify_session(self, token: str) -> Optional[dict]:
        """Verify session token and return user info."""
        sessions = self._load_sessions()
        
        if token not in sessions["sessions"]:
            return None
        
        session = sessions["sessions"][token]
        
        # Check if session expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            del sessions["sessions"][token]
            self._save_sessions(sessions)
            return None
        
        return {
            "username": session["username"],
            "token": token
        }
    
    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information."""
        data = self._load_users()
        
        for user in data["users"]:
            if user["username"] == username:
                return {
                    "username": user["username"],
                    "email": user.get("email", ""),
                    "created_at": user["created_at"],
                    "last_login": user.get("last_login")
                }
        
        return None


user_manager = UserManager()

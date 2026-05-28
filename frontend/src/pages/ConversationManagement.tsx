import { useState, useEffect } from 'react';
import { Search, Trash2, Edit2, MessageSquare, Calendar } from 'lucide-react';
import {
  getChatSessions,
  getChatHistory,
  deleteChatSession,
  renameChatSession,
  searchChatSessions,
} from '../services/api';
import { ChatSession, ChatMessage } from '../types';

const ConversationManagement = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingSession, setEditingSession] = useState<string | null>(null);
  const [newName, setNewName] = useState('');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    const data = await getChatSessions();
    setSessions(data);
  };

  const handleSearch = async () => {
    if (searchQuery.trim()) {
      const data = await searchChatSessions(searchQuery);
      setSessions(data.sessions);
    } else {
      loadSessions();
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    setSelectedSession(sessionId);
    const history = await getChatHistory(sessionId);
    setMessages(history);
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('Delete this conversation?')) return;
    await deleteChatSession(sessionId);
    if (selectedSession === sessionId) {
      setSelectedSession(null);
      setMessages([]);
    }
    loadSessions();
  };

  const handleRenameSession = async (sessionId: string) => {
    if (!newName.trim()) return;
    await renameChatSession(sessionId, newName);
    setEditingSession(null);
    setNewName('');
    loadSessions();
  };

  const startRename = (sessionId: string) => {
    setEditingSession(sessionId);
    setNewName('');
  };

  return (
    <div className="h-full flex gap-4">
      {/* Sessions List */}
      <div className="w-96 bg-white rounded-lg shadow flex flex-col">
        <div className="p-4 border-b">
          <h2 className="text-xl font-bold mb-4">Conversations</h2>
          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {sessions.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No conversations found</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.session_id}
                className={`p-3 rounded-lg border cursor-pointer hover:bg-gray-50 ${
                  selectedSession === session.session_id ? 'bg-blue-50 border-blue-300' : ''
                }`}
                onClick={() => handleSelectSession(session.session_id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {editingSession === session.session_id ? (
                      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          className="flex-1 px-2 py-1 border rounded text-sm"
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleRenameSession(session.session_id)}
                          autoFocus
                        />
                        <button
                          onClick={() => handleRenameSession(session.session_id)}
                          className="px-2 py-1 bg-blue-600 text-white rounded text-sm"
                        >
                          Save
                        </button>
                      </div>
                    ) : (
                      <div className="font-medium text-sm truncate">
                        Session {session.session_id.slice(-8)}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                      <MessageSquare className="w-3 h-3" />
                      <span>{session.message_count} messages</span>
                      <Calendar className="w-3 h-3 ml-2" />
                      <span>{new Date(session.last_message).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex gap-1 ml-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => startRename(session.session_id)}
                      className="p-1 hover:bg-gray-200 rounded"
                    >
                      <Edit2 className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => handleDeleteSession(session.session_id)}
                      className="p-1 hover:bg-red-100 rounded"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Conversation View */}
      <div className="flex-1 bg-white rounded-lg shadow flex flex-col">
        {selectedSession ? (
          <>
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Conversation Details</h3>
              <p className="text-sm text-gray-500">Session ID: {selectedSession}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl px-4 py-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-xs opacity-75 mb-1">
                      {msg.role === 'user' ? 'You' : 'Assistant'} •{' '}
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 border-t bg-gray-50">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>Total messages: {messages.length}</span>
                <span>
                  Started: {messages.length > 0 ? new Date(messages[0].timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">Select a conversation to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationManagement;

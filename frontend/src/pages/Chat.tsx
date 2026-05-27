import { useState, useEffect, useRef } from 'react';
import { Send, Plus, SunMoon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessageStream, getChatHistory, getChatSessions } from '../services/api';
import { ChatMessage, ChatSession } from '../types';

const Chat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    const data = await getChatSessions();
    setSessions(data);
  };

  const loadHistory = async (sid: string) => {
    const history = await getChatHistory(sid);
    setMessages(history);
    setSessionId(sid);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setStreaming(true);
    setLoading(true);

    let accumulated = '';

    try {
      const response = await sendChatMessageStream(input, sessionId || undefined, (chunk) => {
        accumulated += chunk;
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant') {
            return [...prev.slice(0, -1), { ...last, content: accumulated, timestamp: new Date().toISOString() }];
          }
          return [...prev, { role: 'assistant', content: accumulated, timestamp: new Date().toISOString() }];
        });
      });

      const newSessionId = response.headers.get('x-session-id');
      if (!sessionId && newSessionId) {
        setSessionId(newSessionId);
        await loadSessions();
      }
    } catch (err) {
      console.error('Streaming chat error:', err);
    } finally {
      setStreaming(false);
      setLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
  };



  const toggleTheme = () => setTheme(t => (t === 'light' ? 'dark' : 'light'));

  return (
    <div className="flex h-full gap-4">
      <div className="w-64 bg-white rounded-lg shadow p-4">
        <button
          onClick={startNewChat}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center mb-4"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Chat
        </button>
        <div className="space-y-2">
          {sessions.map((session) => (
            <button
              key={session.session_id}
              onClick={() => loadHistory(session.session_id)}
              className={`w-full text-left px-3 py-2 rounded hover:bg-gray-100 ${
                sessionId === session.session_id ? 'bg-gray-100' : ''
              }`}
            >
              <div className="text-sm font-medium truncate">
                Session {session.session_id.slice(-8)}
              </div>
              <div className="text-xs text-gray-500">{session.message_count} messages</div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow flex flex-col">
        <div className="flex items-center justify-between p-3 border-b dark:border-gray-700">
          <div className="text-lg font-semibold text-gray-800 dark:text-gray-100">Chat</div>
          <div className="flex items-center gap-2">
            <button onClick={toggleTheme} title="Toggle theme" className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
              <SunMoon className="w-5 h-5 text-gray-700 dark:text-gray-200" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl px-4 py-2 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'}`}>
                <div className="prose max-w-none break-words text-sm">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
                  {new Date(msg.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
          {(loading || streaming) && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
                <div className="flex space-x-2 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  <div className="text-xs text-gray-600 dark:text-gray-300 ml-2">AI is typing...</div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
            />

            <button
              onClick={handleSend}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              title="Send message"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;

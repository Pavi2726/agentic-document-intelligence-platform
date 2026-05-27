import axios from 'axios';
import { Document, ChatMessage, ChatSession, ChatResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (username: string, password: string) => {
  const { data } = await api.post('/auth/login', { username, password });
  return data;
};

export const register = async (username: string, password: string, email: string = '') => {
  const { data } = await api.post('/auth/register', { username, password, email });
  return data;
};

export const logout = async () => {
  const { data } = await api.post('/auth/logout');
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  return data;
};

export const getCurrentUser = async () => {
  const { data } = await api.get('/auth/me');
  return data;
};

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/upload', formData);
  return data;
};

export const uploadDocumentWithProgress = async (
  file: File,
  onProgress: (percent: number) => void
) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent: any) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

export const getDocuments = async (): Promise<Document[]> => {
  const { data } = await api.get('/documents');
  return data.documents;
};

export const deleteDocument = async (filename: string) => {
  const { data } = await api.delete(`/documents/${filename}`);
  return data;
};

export const sendChatMessage = async (
  message: string,
  sessionId?: string,
  stream: boolean = false
): Promise<ChatResponse> => {
  const { data } = await api.post('/chat', {
    message,
    session_id: sessionId,
    stream,
  });
  return data;
};

// Stream responses from the backend `/chat` endpoint. Caller provides an
// `onChunk` callback that will be invoked with partial text as it arrives.
export const sendChatMessageStream = async (
  message: string,
  sessionId: string | undefined,
  onChunk: (chunk: string) => void
) => {
  const url = `/api/chat`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, stream: true }),
  });

  if (!res.ok || !res.body) {
    throw new Error('Streaming request failed');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let done = false;
  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = !!readerDone;
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  }

  return res;
};

export const getChatHistory = async (sessionId: string): Promise<ChatMessage[]> => {
  const { data } = await api.get(`/chat/history/${sessionId}`);
  return data.history;
};

export const getChatSessions = async (userId: string = 'default'): Promise<ChatSession[]> => {
  const { data } = await api.get(`/chat/sessions?user_id=${userId}`);
  return data.sessions;
};

export const deleteChatSession = async (sessionId: string) => {
  const { data } = await api.delete(`/chat/session/${sessionId}`);
  return data;
};

export const getHealth = async () => {
  const { data } = await api.get('/health');
  return data;
};

export const getGraphData = async () => {
  const { data } = await api.get('/graph/data');
  return data;
};

export const getAnalyticsMetrics = async () => {
  const { data } = await api.get('/analytics/metrics');
  return data;
};

export const renameChatSession = async (sessionId: string, name: string) => {
  const { data } = await api.put(`/chat/session/${sessionId}/rename?name=${encodeURIComponent(name)}`);
  return data;
};

export const searchChatSessions = async (query: string, userId: string = 'default') => {
  const { data } = await api.get(`/chat/sessions/search?query=${encodeURIComponent(query)}&user_id=${userId}`);
  return data;
};

export interface Document {
  id: number;
  filename: string;
  file_path: string;
  chunk_count: number;
  uploaded_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  last_message: string;
  message_count: number;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: {
    vector_count: number;
    graph_count: number;
    sql_count: number;
  };
  context_used: number;
}

export interface GraphNode {
  id: string;
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  document: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AnalyticsMetrics {
  total_documents: number;
  total_chunks: number;
  total_queries: number;
  api_usage: Array<{ date: string; requests: number }>;
  latency: Array<{ endpoint: string; avg_ms: number }>;
  recent_activity: Array<{ query: string; agent: string; timestamp: string }>;
}

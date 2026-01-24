/**
 * API client for conversation history (Chat Champ)
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface MessageRecord {
  id: string;
  role: string;
  content: string;
  input_tokens: number;
  output_tokens: number;
  model: string | null;
  created_at: string;
}

export interface ConversationRecord {
  id: string;
  agent_id: string;
  agent_name: string | null;
  session_id: string;
  status: string;
  message_count: number;
  total_tokens: number;
  started_at: string;
  ended_at: string | null;
  last_message_at: string | null;
  messages?: MessageRecord[];
}

export interface ConversationListResponse {
  conversations: ConversationRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ListConversationsParams {
  page?: number;
  page_size?: number;
  agent_id?: string;
  status?: string;
}

export interface ExportConversationsParams {
  format: "csv" | "json";
  conversation_ids?: string[];
  agent_id?: string;
  date_from?: string;
  date_to?: string;
  include_messages?: boolean;
}

export interface AnalyzeConversationsParams {
  conversation_ids?: string[];
  agent_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface ConversationAnalysisResponse {
  total_conversations_analyzed: number;
  total_messages: number;
  total_tokens: number;
  patterns: string[];
  issues: string[];
  suggestions: string[];
  sample_improvements: string;
}

export interface ConversationEfficiencyScore {
  conversation_id: string;
  agent_name: string | null;
  message_count: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  duration_seconds: number | null;
  efficiency_rating: "efficient" | "moderate" | "wasteful";
  started_at: string;
}

export interface ConversationAnalyticsResponse {
  total_conversations: number;
  total_messages: number;
  total_tokens: number;
  avg_messages_per_conversation: number;
  avg_tokens_per_conversation: number;
  efficiency_scores: ConversationEfficiencyScore[];
  conversations_by_efficiency: { efficient: number; moderate: number; wasteful: number };
  avg_duration_seconds: number | null;
  estimated_cost_total: number;
  estimated_cost_wasted: number;
}

/**
 * List conversations with pagination and filtering
 */
export async function listConversations(
  params: ListConversationsParams = {}
): Promise<ConversationListResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", params.page.toString());
  if (params.page_size) searchParams.set("page_size", params.page_size.toString());
  if (params.agent_id) searchParams.set("agent_id", params.agent_id);
  if (params.status) searchParams.set("status", params.status);

  const response = await fetch(`${API_BASE}/api/v1/conversations?${searchParams.toString()}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch conversations");
  }

  return response.json();
}

/**
 * Get a specific conversation with messages
 */
export async function getConversation(conversationId: string): Promise<ConversationRecord> {
  const response = await fetch(`${API_BASE}/api/v1/conversations/${conversationId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch conversation");
  }

  return response.json();
}

/**
 * Export conversations as CSV or JSON
 */
export async function exportConversations(params: ExportConversationsParams): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/v1/conversations/export`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to export conversations");
  }

  return response.blob();
}

/**
 * Analyze conversations using GPT-4
 */
export async function analyzeConversations(
  params: AnalyzeConversationsParams
): Promise<ConversationAnalysisResponse> {
  const response = await fetch(`${API_BASE}/api/v1/conversations/analyze`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to analyze conversations");
  }

  return response.json();
}

/**
 * Get conversation analytics with efficiency metrics
 */
export async function getConversationAnalytics(
  params: {
    agent_id?: string;
    date_from?: string;
    date_to?: string;
  } = {}
): Promise<ConversationAnalyticsResponse> {
  const searchParams = new URLSearchParams();
  if (params.agent_id) searchParams.set("agent_id", params.agent_id);
  if (params.date_from) searchParams.set("date_from", params.date_from);
  if (params.date_to) searchParams.set("date_to", params.date_to);

  const response = await fetch(
    `${API_BASE}/api/v1/conversations/analytics?${searchParams.toString()}`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch conversation analytics");
  }

  return response.json();
}

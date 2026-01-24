/**
 * API client for call history
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface CallRecord {
  id: string;
  provider: string;
  provider_call_id: string;
  agent_id: string | null;
  agent_name: string | null;
  contact_id: number | null;
  contact_name: string | null;
  workspace_id: string | null;
  workspace_name: string | null;
  direction: "inbound" | "outbound";
  status: string;
  from_number: string;
  to_number: string;
  duration_seconds: number;
  recording_url: string | null;
  transcript: string | null;
  started_at: string;
  answered_at: string | null;
  ended_at: string | null;
}

export interface CallRecordListResponse {
  calls: CallRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ListCallsParams {
  page?: number;
  page_size?: number;
  agent_id?: string;
  workspace_id?: string;
  direction?: "inbound" | "outbound";
  status?: string;
}

export interface CallStats {
  total_calls: number;
  completed_calls: number;
  inbound_calls: number;
  outbound_calls: number;
  total_duration_seconds: number;
  average_duration_seconds: number;
}

export interface ExportCallsParams {
  format: "csv" | "json";
  call_ids?: string[];
  agent_id?: string;
  date_from?: string;
  date_to?: string;
  include_transcripts?: boolean;
}

export interface AnalyzeCallsParams {
  call_ids?: string[];
  agent_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface CallAnalysisResponse {
  total_calls_analyzed: number;
  total_duration_seconds: number;
  patterns: string[];
  issues: string[];
  suggestions: string[];
  sample_improvements: string;
}

export interface CallEfficiencyScore {
  call_id: string;
  agent_name: string | null;
  duration_seconds: number;
  transcript_length: number;
  word_count: number;
  turn_count: number;
  words_per_minute: number;
  efficiency_rating: "efficient" | "moderate" | "wasteful";
  started_at: string;
}

export interface CallAnalyticsResponse {
  total_calls: number;
  total_duration_seconds: number;
  avg_duration_seconds: number;
  efficiency_scores: CallEfficiencyScore[];
  calls_by_efficiency: { efficient: number; moderate: number; wasteful: number };
  avg_words_per_minute: number;
  avg_turns_per_call: number;
  estimated_cost_total: number;
  estimated_cost_wasted: number;
}

/**
 * List call records with pagination and filtering
 */
export async function listCalls(params: ListCallsParams = {}): Promise<CallRecordListResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", params.page.toString());
  if (params.page_size) searchParams.set("page_size", params.page_size.toString());
  if (params.agent_id) searchParams.set("agent_id", params.agent_id);
  if (params.workspace_id) searchParams.set("workspace_id", params.workspace_id);
  if (params.direction) searchParams.set("direction", params.direction);
  if (params.status) searchParams.set("status", params.status);

  const response = await fetch(`${API_BASE}/api/v1/calls?${searchParams.toString()}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch calls");
  }

  return response.json();
}

/**
 * Get a specific call record
 */
export async function getCall(callId: string): Promise<CallRecord> {
  const response = await fetch(`${API_BASE}/api/v1/calls/${callId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch call");
  }

  return response.json();
}

/**
 * Get call statistics for an agent
 */
export async function getAgentCallStats(agentId: string): Promise<CallStats> {
  const response = await fetch(`${API_BASE}/api/v1/calls/agent/${agentId}/stats`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch agent call stats");
  }

  return response.json();
}

/**
 * Export calls as CSV or JSON
 */
export async function exportCalls(params: ExportCallsParams): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/v1/calls/export`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to export calls");
  }

  return response.blob();
}

/**
 * Analyze calls using GPT-4
 */
export async function analyzeCalls(params: AnalyzeCallsParams): Promise<CallAnalysisResponse> {
  const response = await fetch(`${API_BASE}/api/v1/calls/analyze`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to analyze calls");
  }

  return response.json();
}

/**
 * Get call analytics with efficiency metrics
 */
export async function getCallAnalytics(
  params: {
    agent_id?: string;
    date_from?: string;
    date_to?: string;
  } = {}
): Promise<CallAnalyticsResponse> {
  const searchParams = new URLSearchParams();
  if (params.agent_id) searchParams.set("agent_id", params.agent_id);
  if (params.date_from) searchParams.set("date_from", params.date_from);
  if (params.date_to) searchParams.set("date_to", params.date_to);

  const response = await fetch(`${API_BASE}/api/v1/calls/analytics?${searchParams.toString()}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to fetch call analytics");
  }

  return response.json();
}

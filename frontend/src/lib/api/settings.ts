/**
 * API client for user settings
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Fetch with timeout to prevent hanging requests
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 10000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  // Merge auth headers with any provided headers
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers ?? {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    return response;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("Request timed out - please check if the backend is running");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export interface SettingsResponse {
  openai_api_key_set: boolean;
  deepgram_api_key_set: boolean;
  elevenlabs_api_key_set: boolean;
  telnyx_api_key_set: boolean;
  twilio_account_sid_set: boolean;
  workspace_id: string | null;
}

export interface UpdateSettingsRequest {
  openai_api_key?: string;
  deepgram_api_key?: string;
  elevenlabs_api_key?: string;
  telnyx_api_key?: string;
  telnyx_public_key?: string;
  twilio_account_sid?: string;
  twilio_auth_token?: string;
}

export interface ChatGPTConnectionStatus {
  connected: boolean;
  workspace_id: string | null;
  account_email: string | null;
  account_name: string | null;
  plan_type: string | null;
  expires_at: string | null;
  can_refresh: boolean;
  updated_at: string | null;
}

function workspaceParams(workspaceId?: string): string {
  return workspaceId ? `?workspace_id=${encodeURIComponent(workspaceId)}` : "";
}

async function chatGPTRequest<T>(
  path: string,
  method: "GET" | "POST" | "DELETE",
  workspaceId?: string
): Promise<T> {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/oauth/chatgpt${path}${workspaceParams(workspaceId)}`,
    { method }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "ChatGPT connection request failed");
  }
  return response.json();
}

export function fetchChatGPTStatus(workspaceId?: string): Promise<ChatGPTConnectionStatus> {
  return chatGPTRequest("/status", "GET", workspaceId);
}

export function connectChatGPT(workspaceId?: string): Promise<{ authorization_url: string }> {
  return chatGPTRequest("/connect", "POST", workspaceId);
}

export function refreshChatGPT(workspaceId?: string): Promise<ChatGPTConnectionStatus> {
  return chatGPTRequest("/refresh", "POST", workspaceId);
}

export function disconnectChatGPT(workspaceId?: string): Promise<{ message: string }> {
  return chatGPTRequest("/connection", "DELETE", workspaceId);
}

export async function fetchSettings(workspaceId?: string): Promise<SettingsResponse> {
  const params = workspaceId ? `?workspace_id=${workspaceId}` : "";
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/settings${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch settings: ${response.statusText}`);
  }
  return response.json();
}

export async function updateSettings(
  request: UpdateSettingsRequest,
  workspaceId?: string
): Promise<{ message: string }> {
  const params = workspaceId ? `?workspace_id=${workspaceId}` : "";
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/settings${params}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Failed to update settings");
  }

  return response.json();
}

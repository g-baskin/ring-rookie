const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Lesson {
  id: string;
  user_id: string;
  agent_id: string;
  workspace_id: string | null;
  source_call_id: string;
  title: string;
  observation: string;
  recommended_action: string;
  status: "active" | "archived";
  created_at: string;
  updated_at: string;
}

export interface CreateLessonRequest {
  source_call_id: string;
  title: string;
  observation: string;
  recommended_action: string;
  status?: Lesson["status"];
}

export type UpdateLessonRequest = Partial<Omit<CreateLessonRequest, "source_call_id">>;
export type LessonExportFormat = "csv" | "json";

function authHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function lessonUrl(agentId: string, workspaceId?: string | null, suffix = ""): string {
  const url = new URL(`${API_BASE}/api/v1/agents/${agentId}/lessons${suffix}`);
  if (workspaceId) url.searchParams.set("workspace_id", workspaceId);
  return url.toString();
}

async function requireOk(response: Response, fallback: string): Promise<Response> {
  if (response.ok) return response;
  const error = (await response.json().catch(() => null)) as { detail?: string } | null;
  throw new Error(error?.detail ?? fallback);
}

export async function fetchLessons(
  agentId: string,
  workspaceId?: string | null
): Promise<Lesson[]> {
  const response = await fetch(lessonUrl(agentId, workspaceId), { headers: authHeaders() });
  await requireOk(response, "Failed to load lessons");
  return response.json() as Promise<Lesson[]>;
}

export async function createLesson(
  agentId: string,
  request: CreateLessonRequest,
  workspaceId?: string | null
): Promise<Lesson> {
  const response = await fetch(lessonUrl(agentId, workspaceId), {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  await requireOk(response, "Failed to save lesson");
  return response.json() as Promise<Lesson>;
}

export async function updateLesson(
  agentId: string,
  lessonId: string,
  request: UpdateLessonRequest,
  workspaceId?: string | null
): Promise<Lesson> {
  const response = await fetch(lessonUrl(agentId, workspaceId, `/${lessonId}`), {
    method: "PATCH",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  await requireOk(response, "Failed to update lesson");
  return response.json() as Promise<Lesson>;
}

export async function deleteLesson(
  agentId: string,
  lessonId: string,
  workspaceId?: string | null
): Promise<void> {
  const response = await fetch(lessonUrl(agentId, workspaceId, `/${lessonId}`), {
    method: "DELETE",
    headers: authHeaders(),
  });
  await requireOk(response, "Failed to delete lesson");
}

export async function downloadLessons(
  agentId: string,
  format: LessonExportFormat,
  workspaceId?: string | null,
  lessonIds: string[] = []
): Promise<void> {
  const url = new URL(lessonUrl(agentId, workspaceId, `/export/${format}`));
  lessonIds.forEach((id) => url.searchParams.append("lesson_id", id));
  const response = await fetch(url, { headers: authHeaders() });
  await requireOk(response, `Failed to export ${format.toUpperCase()}`);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = `lessons-${agentId}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

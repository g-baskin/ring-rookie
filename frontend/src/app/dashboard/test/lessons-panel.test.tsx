import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LessonsPanel } from "./lessons-panel";

const fetchLessons = vi.fn();
const deleteLesson = vi.fn();
const downloadLessons = vi.fn();
vi.mock("@/lib/api/lessons", () => ({
  fetchLessons: (...args: unknown[]) => fetchLessons(...args),
  deleteLesson: (...args: unknown[]) => deleteLesson(...args),
  downloadLessons: (...args: unknown[]) => downloadLessons(...args),
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

function renderPanel() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <LessonsPanel agentId="agent-1" workspaceId="workspace-1" onEdit={vi.fn()} />
    </QueryClientProvider>
  );
}

const lesson = {
  id: "lesson-1",
  title: "Greeting",
  observation: "Interrupted caller",
  recommended_action: "Wait",
  created_at: "2026-08-13T00:00:00Z",
};

describe("LessonsPanel", () => {
  beforeEach(() => {
    fetchLessons.mockReset().mockResolvedValue([lesson]);
    deleteLesson.mockReset().mockResolvedValue(undefined);
    downloadLessons.mockReset().mockResolvedValue(undefined);
  });

  it("lists and deletes lessons", async () => {
    renderPanel();
    expect(await screen.findByText("Greeting")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Delete lesson Greeting" }));
    await waitFor(() =>
      expect(deleteLesson).toHaveBeenCalledWith("agent-1", "lesson-1", "workspace-1")
    );
  });

  it("exports both explicit local formats", async () => {
    renderPanel();
    await screen.findByText("Greeting");
    fireEvent.click(screen.getByRole("checkbox", { name: "Select lesson Greeting" }));
    fireEvent.click(screen.getByRole("button", { name: /CSV/ }));
    fireEvent.click(screen.getByRole("button", { name: /JSON/ }));
    await waitFor(() => expect(downloadLessons).toHaveBeenCalledTimes(2));
    expect(downloadLessons).toHaveBeenCalledWith("agent-1", "csv", "workspace-1", ["lesson-1"]);
    expect(downloadLessons).toHaveBeenCalledWith("agent-1", "json", "workspace-1", ["lesson-1"]);
  });
});

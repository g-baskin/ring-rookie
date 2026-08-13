import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LessonDialog } from "./lesson-dialog";

const createLesson = vi.fn();
const updateLesson = vi.fn();
vi.mock("@/lib/api/lessons", () => ({
  createLesson: (...args: unknown[]) => createLesson(...args),
  updateLesson: (...args: unknown[]) => updateLesson(...args),
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

describe("LessonDialog", () => {
  beforeEach(() => {
    createLesson.mockReset();
    updateLesson.mockReset();
  });

  it("keeps save disabled until a transcript has a persisted call id", () => {
    render(
      <LessonDialog
        agentId="agent-1"
        sourceCallId={null}
        open
        onOpenChange={vi.fn()}
        onSaved={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: "Save lesson" })).toBeDisabled();
  });

  it("saves bounded user-authored fields against the source call", async () => {
    createLesson.mockResolvedValue({ id: "lesson-1" });
    const onSaved = vi.fn();
    render(
      <LessonDialog
        agentId="agent-1"
        workspaceId="workspace-1"
        sourceCallId="call-1"
        open
        onOpenChange={vi.fn()}
        onSaved={onSaved}
      />
    );
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Greeting" } });
    fireEvent.change(screen.getByLabelText("What went wrong or what did you learn?"), {
      target: { value: "It interrupted the caller" },
    });
    fireEvent.change(screen.getByLabelText("Recommended prompt or action change"), {
      target: { value: "Wait for a pause" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save lesson" }));
    await waitFor(() => expect(onSaved).toHaveBeenCalled());
    expect(createLesson).toHaveBeenCalledWith(
      "agent-1",
      {
        source_call_id: "call-1",
        title: "Greeting",
        observation: "It interrupted the caller",
        recommended_action: "Wait for a pause",
      },
      "workspace-1"
    );
  });

  it("edits a prior lesson without changing its source call", async () => {
    updateLesson.mockResolvedValue({ id: "lesson-1" });
    render(
      <LessonDialog
        agentId="agent-1"
        sourceCallId={null}
        lesson={{
          id: "lesson-1",
          user_id: "user-1",
          agent_id: "agent-1",
          workspace_id: null,
          source_call_id: "call-1",
          title: "Greeting",
          observation: "Interrupted",
          recommended_action: "Wait",
          status: "active",
          created_at: "2026-08-13T00:00:00Z",
          updated_at: "2026-08-13T00:00:00Z",
        }}
        open
        onOpenChange={vi.fn()}
        onSaved={vi.fn()}
      />
    );
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Updated" } });
    fireEvent.click(screen.getByRole("button", { name: "Update lesson" }));
    await waitFor(() => expect(updateLesson).toHaveBeenCalled());
    expect(updateLesson.mock.calls[0]?.[2]).toMatchObject({ title: "Updated" });
  });
});

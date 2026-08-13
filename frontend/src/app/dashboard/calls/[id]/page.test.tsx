import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CallDetailPage from "./page";

const getCall = vi.fn();
vi.mock("@/lib/api/calls", () => ({ getCall: (...args: unknown[]) => getCall(...args) }));
vi.mock("react", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react")>();
  return { ...actual, use: () => ({ id: "call-1" }) };
});

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity } },
  });
  const view = render(
    <QueryClientProvider client={client}>
      <CallDetailPage params={Promise.resolve({ id: "call-1" })} />
    </QueryClientProvider>
  );
  return { ...view, client };
}

describe("CallDetailPage", () => {
  beforeEach(() => getCall.mockReset());

  it("loads and displays the linked call", async () => {
    getCall.mockResolvedValue({
      id: "call-1",
      provider: "test",
      provider_call_id: "session-1",
      agent_id: "agent-1",
      agent_name: "Reception Agent",
      contact_id: null,
      contact_name: "Alex Caller",
      workspace_id: null,
      workspace_name: null,
      direction: "outbound",
      status: "completed",
      from_number: "test",
      to_number: "+15551234567",
      duration_seconds: 75,
      recording_url: null,
      transcript: "User: Hello\nAssistant: Hi there",
      started_at: "2026-08-13T18:00:00Z",
      answered_at: null,
      ended_at: "2026-08-13T18:01:15Z",
    });
    const { client } = renderPage();
    expect(await screen.findByRole("heading", { name: "Call details" })).toBeInTheDocument();
    expect(screen.getByText("Reception Agent")).toBeInTheDocument();
    expect(screen.getByText(/Assistant: Hi there/)).toBeInTheDocument();
    expect(getCall).toHaveBeenCalledWith("call-1");
    client.clear();
  });

  it("renders the API error state without leaking a route-level 404", async () => {
    getCall.mockRejectedValueOnce(new Error("Call not found"));
    const { client } = renderPage();

    expect(await screen.findByRole("heading", { name: "Call not available" })).toBeInTheDocument();
    expect(screen.getByText("Call not found")).toBeInTheDocument();
    expect(getCall).toHaveBeenCalledWith("call-1");

    client.clear();
  });
});

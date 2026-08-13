export type ExportableTranscriptItem = {
  speaker: "user" | "assistant" | "system";
  text: string;
  timestamp: Date;
};

export function formatTranscriptExport(
  items: ExportableTranscriptItem[],
  agentName: string | undefined
): string {
  const title = agentName ? `${agentName} transcript` : "Agent transcript";
  const lines = items.map((item) => {
    const speaker =
      item.speaker === "user" ? "User" : item.speaker === "assistant" ? "Assistant" : "System";
    return `[${item.timestamp.toISOString()}] ${speaker}: ${item.text}`;
  });
  return [title, `Exported: ${new Date().toISOString()}`, "", ...lines, ""].join("\n");
}

export function createTranscriptFilename(
  agentName: string | undefined,
  exportedAt = new Date()
): string {
  const safeAgentName = (agentName ?? "agent")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  const timestamp = exportedAt.toISOString().replace(/[:.]/g, "-");
  return `${safeAgentName || "agent"}-transcript-${timestamp}.txt`;
}

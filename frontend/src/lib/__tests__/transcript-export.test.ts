import { describe, expect, it, vi } from "vitest";
import { createTranscriptFilename, formatTranscriptExport } from "../transcript-export";

describe("transcript export", () => {
  it("formats local text exports with timestamps and speaker labels", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-08-13T12:00:00.000Z"));

    expect(
      formatTranscriptExport(
        [
          {
            speaker: "user",
            text: "Hello",
            timestamp: new Date("2026-08-13T11:59:00.000Z"),
          },
          {
            speaker: "assistant",
            text: "Hi there",
            timestamp: new Date("2026-08-13T11:59:01.000Z"),
          },
        ],
        "Sales Agent"
      )
    ).toContain(
      "Sales Agent transcript\nExported: 2026-08-13T12:00:00.000Z\n\n" +
        "[2026-08-13T11:59:00.000Z] User: Hello\n" +
        "[2026-08-13T11:59:01.000Z] Assistant: Hi there"
    );

    vi.useRealTimers();
  });

  it("creates filesystem-safe timestamped filenames", () => {
    expect(
      createTranscriptFilename("Sales & Marketing!", new Date("2026-08-13T12:34:56.789Z"))
    ).toBe("sales-marketing-transcript-2026-08-13T12-34-56-789Z.txt");
  });
});

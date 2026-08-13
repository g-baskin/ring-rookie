import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";
import {
  GA_AUDIO_EVENTS,
  REALTIME_CALL_URL,
  addEncodedMicrophoneTrack,
  attachDecodedRemoteAudio,
  createRealtimeCallRequest,
  createTranscriptUrl,
  getRealtimeAudioEventKind,
} from "../realtime-webrtc";

const testPageSource = readFileSync(resolve("src/app/dashboard/test/page.tsx"), "utf8");
const embedPageSource = readFileSync(resolve("src/app/embed/[publicId]/page.tsx"), "utf8");

describe("GA Realtime WebRTC contract", () => {
  it("uses /v1/realtime/calls without the retired beta header", () => {
    expect(REALTIME_CALL_URL).toBe("https://api.openai.com/v1/realtime/calls");
    expect(createRealtimeCallRequest("ek_test", "v=0\r\n")).toEqual({
      method: "POST",
      body: "v=0\r\n",
      headers: {
        "Content-Type": "application/sdp",
        Authorization: "Bearer ek_test",
      },
    });
    expect(createRealtimeCallRequest("ek_test", "").headers).not.toHaveProperty("OpenAI-Beta");
  });

  it("keeps Test and Embed on shared GA transport and browser audio helpers", () => {
    for (const pageSource of [testPageSource, embedPageSource]) {
      expect(pageSource).toContain("REALTIME_CALL_URL");
      expect(pageSource).toContain("createRealtimeCallRequest(ephemeralKey");
      expect(pageSource).toContain("addEncodedMicrophoneTrack(pc, micStream)");
      expect(pageSource).toContain("attachDecodedRemoteAudio(pc, audioElement)");
      expect(pageSource).not.toContain("OpenAI-Beta");
    }
    expect(testPageSource).toContain("GA_AUDIO_EVENTS.transcriptDone");
    expect(embedPageSource).toContain("GA_AUDIO_EVENTS.outputDelta");
    expect(embedPageSource).toContain("GA_AUDIO_EVENTS.outputDone");
    expect(embedPageSource).toContain("GA_AUDIO_EVENTS.transcriptDelta");
    expect(embedPageSource).toContain("GA_AUDIO_EVENTS.transcriptDone");
  });

  it("sends transcript saves in the selected agent workspace context", () => {
    expect(createTranscriptUrl("http://localhost:8000", "agent-1", "workspace/one")).toBe(
      "http://localhost:8000/api/v1/realtime/transcript/agent-1?workspace_id=workspace%2Fone"
    );
    expect(createTranscriptUrl("http://localhost:8000", "agent-1", "all")).toBe(
      "http://localhost:8000/api/v1/realtime/transcript/agent-1"
    );
    expect(testPageSource).toContain("createTranscriptUrl(apiBase, agentId, selectedWorkspaceId)");
    expect(testPageSource).toContain(
      'console.log("[Transcript] Saved transcript to backend successfully")'
    );
    expect(testPageSource).toContain(
      'console.error("[Transcript] Failed to save:", response.status, errorText)'
    );
    expect(testPageSource).toContain(
      'console.error("[Transcript] Failed to save transcript:", error)'
    );
  });

  it("recognizes every GA output audio and transcript event used by Test and Embed", () => {
    expect(getRealtimeAudioEventKind(GA_AUDIO_EVENTS.outputDelta)).toBe("output-delta");
    expect(getRealtimeAudioEventKind(GA_AUDIO_EVENTS.outputDone)).toBe("output-done");
    expect(getRealtimeAudioEventKind(GA_AUDIO_EVENTS.transcriptDelta)).toBe("transcript-delta");
    expect(getRealtimeAudioEventKind(GA_AUDIO_EVENTS.transcriptDone)).toBe("transcript-done");
    expect(getRealtimeAudioEventKind("response.audio.delta")).toBeNull();
  });

  it("adds microphone audio with its stream for browser codec encoding", () => {
    const audioTrack = { kind: "audio" } as MediaStreamTrack;
    const microphoneStream = {
      getAudioTracks: () => [audioTrack],
    } as unknown as MediaStream;
    const addTrack = vi.fn();
    const peerConnection = { addTrack } as unknown as RTCPeerConnection;

    expect(addEncodedMicrophoneTrack(peerConnection, microphoneStream)).toBe(audioTrack);
    expect(addTrack).toHaveBeenCalledWith(audioTrack, microphoneStream);
  });

  it("attaches the browser-decoded remote stream to autoplay audio", () => {
    const peerConnection = {} as RTCPeerConnection;
    const audioElement = document.createElement("audio");
    const remoteStream = new MediaStream();

    attachDecodedRemoteAudio(peerConnection, audioElement);
    peerConnection.ontrack?.({ streams: [remoteStream] } as unknown as RTCTrackEvent);

    expect(audioElement.autoplay).toBe(true);
    expect(audioElement.srcObject).toBe(remoteStream);
  });
});

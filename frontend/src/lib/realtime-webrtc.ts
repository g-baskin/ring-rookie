export const REALTIME_CALL_URL = "https://api.openai.com/v1/realtime/calls";

export const GA_AUDIO_EVENTS = {
  outputDelta: "response.output_audio.delta",
  outputDone: "response.output_audio.done",
  transcriptDelta: "response.output_audio_transcript.delta",
  transcriptDone: "response.output_audio_transcript.done",
} as const;

export type RealtimeAudioEventKind =
  | "output-delta"
  | "output-done"
  | "transcript-delta"
  | "transcript-done"
  | null;

export function getRealtimeAudioEventKind(type: string): RealtimeAudioEventKind {
  switch (type) {
    case GA_AUDIO_EVENTS.outputDelta:
      return "output-delta";
    case GA_AUDIO_EVENTS.outputDone:
      return "output-done";
    case GA_AUDIO_EVENTS.transcriptDelta:
      return "transcript-delta";
    case GA_AUDIO_EVENTS.transcriptDone:
      return "transcript-done";
    default:
      return null;
  }
}

export function createRealtimeCallRequest(ephemeralKey: string, sdp: string): RequestInit {
  return {
    method: "POST",
    body: sdp,
    headers: {
      "Content-Type": "application/sdp",
      Authorization: `Bearer ${ephemeralKey}`,
    },
  };
}

export function addEncodedMicrophoneTrack(
  peerConnection: RTCPeerConnection,
  microphoneStream: MediaStream
): MediaStreamTrack | undefined {
  const audioTrack = microphoneStream.getAudioTracks()[0];
  if (audioTrack) {
    // RTCPeerConnection negotiates the browser-supported audio codec in the SDP offer.
    peerConnection.addTrack(audioTrack, microphoneStream);
  }
  return audioTrack;
}

export function attachDecodedRemoteAudio(
  peerConnection: RTCPeerConnection,
  audioElement: HTMLAudioElement
): void {
  audioElement.autoplay = true;
  peerConnection.ontrack = (event) => {
    // The browser decodes the negotiated remote WebRTC audio track for playback.
    audioElement.srcObject = event.streams[0] ?? null;
  };
}

export function createTranscriptUrl(
  apiBase: string,
  agentId: string,
  selectedWorkspaceId: string
): string {
  const workspaceQuery =
    selectedWorkspaceId === "all" ? "" : `?workspace_id=${encodeURIComponent(selectedWorkspaceId)}`;
  return `${apiBase}/api/v1/realtime/transcript/${agentId}${workspaceQuery}`;
}

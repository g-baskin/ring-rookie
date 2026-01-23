/**
 * Ring Rookie Widget - Standalone Web Component
 *
 * This script creates a floating voice chat widget that can be embedded on any website.
 * Usage:
 *   <script src="https://ringrookie.mragame.com/widget/v1/widget.js" defer></script>
 *   <voice-agent agent-id="ag_xK9mN2pQ"></voice-agent>
 */

type AgentState = "idle" | "listening" | "thinking" | "speaking";
type WidgetStyle = "default" | "retro";

// Styles for the widget
const styles = `
  .va-widget-container {
    position: fixed;
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .va-widget-container.bottom-right {
    bottom: 20px;
    right: 20px;
  }

  .va-widget-container.bottom-left {
    bottom: 20px;
    left: 20px;
  }

  .va-widget-container.top-right {
    top: 20px;
    right: 20px;
  }

  .va-widget-container.top-left {
    top: 20px;
    left: 20px;
  }

  .va-widget-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: var(--va-primary, #6366f1);
    color: white;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 0 0 var(--va-glow-color, rgba(99, 102, 241, 0));
    transition: all 0.3s ease;
    font-size: 14px;
    font-weight: 500;
  }

  .va-widget-button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 32px rgba(0, 0, 0, 0.2), 0 0 16px 4px var(--va-glow-color, rgba(99, 102, 241, 0.3));
  }

  .va-widget-button:active {
    transform: scale(0.98);
  }

  .va-widget-button svg {
    width: 18px;
    height: 18px;
  }

  .va-widget-orb {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .va-widget-orb-gradient {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: conic-gradient(
      from 180deg,
      var(--va-primary, #6366f1) 0deg,
      var(--va-primary-60, #6366f188) 90deg,
      var(--va-primary-30, #6366f144) 180deg,
      var(--va-primary-60, #6366f188) 270deg,
      var(--va-primary, #6366f1) 360deg
    );
    transition: opacity 0.3s ease;
  }

  .va-widget-orb-gradient.animated {
    animation: va-spin 3s linear infinite;
  }

  .va-widget-orb-inner {
    position: absolute;
    inset: 3px;
    border-radius: 50%;
    background: white;
    transition: background-color 0.3s ease;
  }

  .va-widget-orb-dot {
    position: absolute;
    inset: 6px;
    border-radius: 50%;
    background: var(--va-primary, #6366f1);
    opacity: 0.4;
    transition: all 0.2s ease;
  }

  .va-widget-orb-dot.active {
    opacity: 0.8;
    transform: scale(1.1);
  }

  /* State-based styling */
  .va-widget-button.state-listening {
    --va-glow-color: rgba(34, 197, 94, 0.4);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 12px 4px var(--va-glow-color);
  }

  .va-widget-button.state-listening .va-widget-orb-dot {
    background: #22c55e;
    opacity: 0.9;
    animation: va-pulse 1.5s ease-in-out infinite;
  }

  .va-widget-button.state-thinking {
    --va-glow-color: rgba(251, 191, 36, 0.4);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 12px 4px var(--va-glow-color);
  }

  .va-widget-button.state-thinking .va-widget-orb-dot {
    background: #fbbf24;
    opacity: 0.9;
    animation: va-think-pulse 0.8s ease-in-out infinite;
  }

  .va-widget-button.state-speaking {
    --va-glow-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 12px 4px var(--va-glow-color);
  }

  .va-widget-button.state-speaking .va-widget-orb-dot {
    background: #3b82f6;
    opacity: 0.9;
    animation: va-speak-pulse 0.3s ease-in-out infinite;
  }

  .va-widget-popup {
    position: absolute;
    bottom: 60px;
    right: 0;
    width: 380px;
    height: 520px;
    background: transparent;
    overflow: hidden;
    opacity: 0;
    transform: translateY(20px) scale(0.95);
    transition: all 0.3s ease;
    pointer-events: none;
  }

  .va-widget-popup.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
  }

  .va-widget-popup iframe {
    width: 100%;
    height: 100%;
    border: none;
  }

  .va-widget-branding {
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    margin-top: 8px;
  }

  .va-widget-branding a {
    color: var(--va-primary, #6366f1);
    text-decoration: none;
  }

  @keyframes va-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes va-pulse {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.15); opacity: 1; }
  }

  @keyframes va-think-pulse {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.1); opacity: 1; }
  }

  @keyframes va-speak-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
  }

  @media (max-width: 480px) {
    .va-widget-popup {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      border-radius: 0;
      bottom: 0;
      right: 0;
    }
  }

  /* ========================================
     RETRO ARCADE THEME
     Synthwave aesthetic with neon glow, pixel shadows, and CRT effects
     ======================================== */

  .va-widget-button.theme-retro {
    --retro-neon-green: #39ff14;
    --retro-magenta: #ff00ff;
    --retro-cyan: #00ffff;
    --retro-dark: #0a0a0f;
    --retro-pixel-shadow: 4px 4px 0 0 rgba(0, 0, 0, 0.8);

    background: var(--retro-dark);
    border: 2px solid var(--retro-neon-green);
    border-radius: 4px;
    box-shadow:
      var(--retro-pixel-shadow),
      0 0 20px 4px rgba(57, 255, 20, 0.4),
      inset 0 0 20px rgba(57, 255, 20, 0.1);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    font-family: "Press Start 2P", "Courier New", monospace;
    font-size: 11px;
    position: relative;
    overflow: hidden;
  }

  /* Scanline overlay */
  .va-widget-button.theme-retro::before {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 0, 0, 0.15) 2px,
      rgba(0, 0, 0, 0.15) 4px
    );
    pointer-events: none;
    z-index: 1;
  }

  /* Dot grid pattern */
  .va-widget-button.theme-retro::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(
      circle at 1px 1px,
      rgba(57, 255, 20, 0.08) 1px,
      transparent 1px
    );
    background-size: 4px 4px;
    pointer-events: none;
    z-index: 0;
  }

  .va-widget-button.theme-retro:hover {
    transform: translate(-2px, -2px);
    box-shadow:
      6px 6px 0 0 rgba(0, 0, 0, 0.8),
      0 0 30px 8px rgba(57, 255, 20, 0.5),
      inset 0 0 30px rgba(57, 255, 20, 0.15);
  }

  .va-widget-button.theme-retro:active {
    transform: translate(2px, 2px);
    box-shadow:
      2px 2px 0 0 rgba(0, 0, 0, 0.8),
      0 0 15px 2px rgba(57, 255, 20, 0.3);
  }

  /* Retro orb styling */
  .va-widget-button.theme-retro .va-widget-orb {
    border: 2px solid var(--retro-neon-green);
    border-radius: 4px;
    background: var(--retro-dark);
    box-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
  }

  .va-widget-button.theme-retro .va-widget-orb-gradient {
    background: linear-gradient(
      135deg,
      var(--retro-neon-green) 0%,
      rgba(57, 255, 20, 0.3) 50%,
      var(--retro-neon-green) 100%
    );
    border-radius: 2px;
    opacity: 0.3;
  }

  .va-widget-button.theme-retro .va-widget-orb-gradient.animated {
    animation: va-retro-pulse 1.5s ease-in-out infinite;
  }

  .va-widget-button.theme-retro .va-widget-orb-inner {
    background: var(--retro-dark);
    border-radius: 2px;
    inset: 4px;
  }

  .va-widget-button.theme-retro .va-widget-orb-dot {
    background: var(--retro-neon-green);
    border-radius: 2px;
    box-shadow: 0 0 8px var(--retro-neon-green);
    inset: 8px;
  }

  /* Retro state: Listening - Neon Green */
  .va-widget-button.theme-retro.state-listening {
    border-color: var(--retro-neon-green);
    box-shadow:
      var(--retro-pixel-shadow),
      0 0 25px 6px rgba(57, 255, 20, 0.5),
      inset 0 0 25px rgba(57, 255, 20, 0.15);
  }

  .va-widget-button.theme-retro.state-listening .va-widget-orb {
    border-color: var(--retro-neon-green);
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.7);
  }

  .va-widget-button.theme-retro.state-listening .va-widget-orb-dot {
    background: var(--retro-neon-green);
    box-shadow: 0 0 12px var(--retro-neon-green);
    animation: va-retro-listen-pulse 1s ease-in-out infinite;
  }

  /* Retro state: Thinking - Magenta */
  .va-widget-button.theme-retro.state-thinking {
    border-color: var(--retro-magenta);
    box-shadow:
      var(--retro-pixel-shadow),
      0 0 25px 6px rgba(255, 0, 255, 0.5),
      inset 0 0 25px rgba(255, 0, 255, 0.15);
  }

  .va-widget-button.theme-retro.state-thinking .va-widget-orb {
    border-color: var(--retro-magenta);
    box-shadow: 0 0 15px rgba(255, 0, 255, 0.7);
  }

  .va-widget-button.theme-retro.state-thinking .va-widget-orb-dot {
    background: var(--retro-magenta);
    box-shadow: 0 0 12px var(--retro-magenta);
    animation: va-retro-think-pulse 0.6s ease-in-out infinite;
  }

  .va-widget-button.theme-retro.state-thinking .va-widget-orb-gradient {
    background: linear-gradient(
      135deg,
      var(--retro-magenta) 0%,
      rgba(255, 0, 255, 0.3) 50%,
      var(--retro-magenta) 100%
    );
  }

  /* Retro state: Speaking - Cyan */
  .va-widget-button.theme-retro.state-speaking {
    border-color: var(--retro-cyan);
    box-shadow:
      var(--retro-pixel-shadow),
      0 0 25px 6px rgba(0, 255, 255, 0.5),
      inset 0 0 25px rgba(0, 255, 255, 0.15);
  }

  .va-widget-button.theme-retro.state-speaking .va-widget-orb {
    border-color: var(--retro-cyan);
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.7);
  }

  .va-widget-button.theme-retro.state-speaking .va-widget-orb-dot {
    background: var(--retro-cyan);
    box-shadow: 0 0 12px var(--retro-cyan);
    animation: va-retro-speak-pulse 0.25s ease-in-out infinite;
  }

  .va-widget-button.theme-retro.state-speaking .va-widget-orb-gradient {
    background: linear-gradient(
      135deg,
      var(--retro-cyan) 0%,
      rgba(0, 255, 255, 0.3) 50%,
      var(--retro-cyan) 100%
    );
  }

  /* Retro branding */
  .theme-retro-container .va-widget-branding {
    font-family: "Press Start 2P", "Courier New", monospace;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .theme-retro-container .va-widget-branding a {
    color: var(--retro-neon-green, #39ff14);
    text-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
  }

  /* Retro animations */
  @keyframes va-retro-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.6; }
  }

  @keyframes va-retro-listen-pulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 8px var(--retro-neon-green); }
    50% { transform: scale(1.2); box-shadow: 0 0 16px var(--retro-neon-green); }
  }

  @keyframes va-retro-think-pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
  }

  @keyframes va-retro-speak-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.3); }
  }
`;

class VoiceAgentElement extends HTMLElement {
  private shadow: ShadowRoot;
  private isOpen = false;
  private agentId: string | null = null;
  private position: string = "bottom-right";
  private theme: string = "auto";
  private buttonText: string = "Voice Chat";
  private baseUrl: string = "";
  private primaryColor: string = "#6366f1";
  private widgetStyle: WidgetStyle = "default";
  private currentState: AgentState = "idle";
  private messageHandler: ((event: MessageEvent) => void) | null = null;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: "open" });
  }

  static get observedAttributes() {
    return [
      "agent-id",
      "position",
      "theme",
      "button-text",
      "base-url",
      "primary-color",
      "widget-style",
    ];
  }

  attributeChangedCallback(name: string, _oldValue: string, newValue: string) {
    switch (name) {
      case "agent-id":
        this.agentId = newValue;
        break;
      case "position":
        this.position = newValue || "bottom-right";
        break;
      case "theme":
        this.theme = newValue || "auto";
        break;
      case "button-text":
        this.buttonText = newValue || "Voice Chat";
        break;
      case "base-url":
        this.baseUrl = newValue || "";
        break;
      case "primary-color":
        this.primaryColor = newValue || "#6366f1";
        break;
      case "widget-style":
        if (newValue === "retro" || newValue === "default") {
          this.widgetStyle = newValue;
        }
        break;
    }
    if (this.isConnected) {
      this.render();
    }
  }

  connectedCallback() {
    // Read attributes
    this.agentId = this.getAttribute("agent-id");
    this.position = this.getAttribute("position") ?? "bottom-right";
    this.theme = this.getAttribute("theme") ?? "auto";
    this.buttonText = this.getAttribute("button-text") ?? "Voice Chat";
    this.baseUrl = this.getAttribute("base-url") ?? this.detectBaseUrl();
    this.primaryColor = this.getAttribute("primary-color") ?? "#6366f1";
    this.widgetStyle = this.detectStyle();

    this.render();

    // Set up message handler
    this.messageHandler = (event: MessageEvent) => this.handleMessage(event);
    window.addEventListener("message", this.messageHandler);
  }

  disconnectedCallback() {
    // Clean up message handler
    if (this.messageHandler) {
      window.removeEventListener("message", this.messageHandler);
      this.messageHandler = null;
    }
  }

  private detectBaseUrl(): string {
    // Try to detect base URL from the script src
    const scripts = document.getElementsByTagName("script");
    for (const script of scripts) {
      if (script.src?.includes("widget")) {
        try {
          const url = new URL(script.src);
          return `${url.protocol}//${url.host}`;
        } catch {
          // Ignore
        }
      }
    }
    // Fallback to current origin
    return window.location.origin;
  }

  private detectStyle(): WidgetStyle {
    // Check explicit attribute first
    const attr = this.getAttribute("widget-style");
    if (attr === "retro" || attr === "default") {
      return attr;
    }
    // Auto-detect retro style for mragame.com
    if (
      window.location.hostname.includes("mragame.com") ||
      window.location.hostname.includes("mragame")
    ) {
      return "retro";
    }
    return "default";
  }

  private hexToHSL(hex: string): { h: number; s: number; l: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result?.[1] || !result[2] || !result[3]) return { h: 0, s: 0, l: 50 };

    const r = parseInt(result[1], 16) / 255;
    const g = parseInt(result[2], 16) / 255;
    const b = parseInt(result[3], 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h = 0;
    let s = 0;
    const l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
          break;
        case g:
          h = ((b - r) / d + 2) / 6;
          break;
        case b:
          h = ((r - g) / d + 4) / 6;
          break;
      }
    }

    return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
  }

  private render() {
    if (!this.agentId) {
      console.error("VoiceAgent: agent-id attribute is required");
      return;
    }

    // Generate CSS color variations
    const hsl = this.hexToHSL(this.primaryColor);
    const primary60 = `hsla(${hsl.h}, ${hsl.s}%, ${hsl.l}%, 0.53)`;
    const primary30 = `hsla(${hsl.h}, ${hsl.s}%, ${hsl.l}%, 0.27)`;

    // Apply custom primary color to styles
    const customStyles = styles
      .replace(/var\(--va-primary, #6366f1\)/g, this.primaryColor)
      .replace(/var\(--va-primary-60, #6366f188\)/g, primary60)
      .replace(/var\(--va-primary-30, #6366f144\)/g, primary30);

    // Determine theme classes
    const themeClass = this.widgetStyle === "retro" ? "theme-retro" : "";
    const containerThemeClass = this.widgetStyle === "retro" ? "theme-retro-container" : "";

    this.shadow.innerHTML = `
      <style>
        :host {
          --va-primary: ${this.primaryColor};
          --va-primary-60: ${primary60};
          --va-primary-30: ${primary30};
        }
        ${customStyles}
      </style>
      <div class="va-widget-container ${this.position} ${containerThemeClass}">
        <div class="va-widget-popup" id="popup">
          <iframe
            src="${this.baseUrl}/embed/${this.agentId}?theme=${this.theme}&autostart=true"
            allow="microphone"
            title="Voice Agent"
          ></iframe>
        </div>
        <div class="va-widget-button-wrapper">
          <button class="va-widget-button ${themeClass}" id="toggle">
            <div class="va-widget-orb" id="orb">
              <div class="va-widget-orb-gradient" id="orb-gradient"></div>
              <div class="va-widget-orb-inner"></div>
              <div class="va-widget-orb-dot" id="orb-dot"></div>
            </div>
            <span id="button-text">${this.buttonText}</span>
          </button>
          <div class="va-widget-branding">
            Powered by <a href="https://www.mragame.com/ring-rookie" target="_blank" rel="noopener noreferrer">Ring Rookie</a>
          </div>
        </div>
      </div>
    `;

    // Add event listeners
    this.shadow.getElementById("toggle")?.addEventListener("click", () => this.toggle());
  }

  private toggle() {
    this.isOpen = !this.isOpen;
    const popup = this.shadow.getElementById("popup");
    const buttonText = this.shadow.getElementById("button-text");
    const orbGradient = this.shadow.getElementById("orb-gradient");
    const orbDot = this.shadow.getElementById("orb-dot");
    const iframe = popup?.querySelector("iframe");

    if (popup) {
      popup.classList.toggle("open", this.isOpen);
    }

    if (buttonText) {
      buttonText.textContent = this.isOpen ? "Close" : this.buttonText;
    }

    if (orbGradient) {
      orbGradient.classList.toggle("animated", this.isOpen);
    }

    if (orbDot) {
      orbDot.classList.toggle("active", this.isOpen);
    }

    // Send message to iframe to restart session when opening
    if (this.isOpen && iframe?.contentWindow) {
      iframe.contentWindow.postMessage({ type: "voice-agent:start" }, "*");
    }

    // Reset state when closing
    if (!this.isOpen) {
      this.updateState("idle");
    }
  }

  private updateState(state: AgentState) {
    this.currentState = state;
    const button = this.shadow.getElementById("toggle");

    if (button) {
      // Remove all state classes (preserves theme-retro class)
      button.classList.remove("state-idle", "state-listening", "state-thinking", "state-speaking");
      // Add current state class
      if (state !== "idle") {
        button.classList.add(`state-${state}`);
      }
    }
  }

  private handleMessage(event: MessageEvent) {
    // Handle messages from the iframe
    const data = event.data;

    if (!data || typeof data !== "object") return;

    // Handle close request
    if (data.type === "voice-agent:close") {
      if (this.isOpen) {
        this.toggle();
      }
      return;
    }

    // Handle state updates from embed
    if (data.type === "voice-agent:state") {
      const state = data.state as AgentState;
      if (["idle", "listening", "thinking", "speaking"].includes(state)) {
        this.updateState(state);
      }
      return;
    }

    // Handle audio level updates for dynamic effects
    if (data.type === "voice-agent:audio-level") {
      const level = data.level as number;
      this.updateAudioLevel(level);
    }
  }

  private updateAudioLevel(level: number) {
    const orb = this.shadow.getElementById("orb");
    const button = this.shadow.getElementById("toggle");

    if (orb && this.isOpen) {
      // Scale orb based on audio level
      const scale = 1 + level * 0.2;
      orb.style.transform = `scale(${scale})`;
    }

    if (button && this.isOpen && this.currentState === "speaking") {
      // Dynamic glow intensity based on audio level
      const glowSize = 12 + level * 12;
      const glowOpacity = 0.4 + level * 0.4;

      if (this.widgetStyle === "retro") {
        // Retro cyan glow for speaking state
        button.style.boxShadow = `4px 4px 0 0 rgba(0, 0, 0, 0.8), 0 0 ${glowSize + 10}px ${glowSize / 2 + 4}px rgba(0, 255, 255, ${glowOpacity}), inset 0 0 25px rgba(0, 255, 255, 0.15)`;
      } else {
        button.style.boxShadow = `0 4px 24px rgba(0, 0, 0, 0.15), 0 0 ${glowSize}px ${glowSize / 2}px rgba(59, 130, 246, ${glowOpacity})`;
      }
    }
  }
}

// Register the custom element
if (!customElements.get("voice-agent")) {
  customElements.define("voice-agent", VoiceAgentElement);
}

// Export for potential module usage
export { VoiceAgentElement };

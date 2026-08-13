import { describe, expect, it } from "vitest";

import { resolveNextDistDir } from "../../../next.config";

describe("Next.js artifact isolation", () => {
  it("uses a dedicated directory for the development server", () => {
    expect(resolveNextDistDir("development")).toBe(".next-dev");
  });

  it("uses a separate directory for production builds", () => {
    expect(resolveNextDistDir("production")).toBe(".next-build");
  });

  it("allows an explicit directory override", () => {
    expect(resolveNextDistDir("development", ".next-smoke")).toBe(".next-smoke");
  });

  it("never shares default development and production artifacts", () => {
    expect(resolveNextDistDir("development")).not.toBe(resolveNextDistDir("production"));
  });
});

import path from "node:path";

import { describe, expect, it } from "vitest";

import nextConfig from "../../../next.config";

describe("Next.js build roots", () => {
  it("keeps development and production artifacts inside the frontend project", () => {
    const frontendRoot = path.resolve(process.cwd());

    expect(nextConfig.outputFileTracingRoot).toBe(frontendRoot);
    expect(nextConfig.turbopack?.root).toBe(frontendRoot);
  });
});

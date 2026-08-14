import path from "node:path";
import { fileURLToPath } from "node:url";

import type { NextConfig } from "next";

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

export function resolveNextDistDir(
  nodeEnvironment = process.env.NODE_ENV,
  configuredDistDir = process.env.NEXT_DIST_DIR,
 ): string {
  if (configuredDistDir) {
    return configuredDistDir;
  }

  return nodeEnvironment === "development" ? ".next-dev" : ".next-build";
}

const nextConfig: NextConfig = {
  distDir: resolveNextDistDir(),
  outputFileTracingRoot: frontendRoot,
  turbopack: {
    root: frontendRoot,
  },
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.simpleicons.org",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/:path*`,
      },
      {
        source: "/health/:path*",
        destination: `${process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/health/:path*`,
      },
    ];
  },
};

export default nextConfig;

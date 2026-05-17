import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // output: "standalone" produces a self-contained bundle used by the Docker image.
  // Remove this if you're not building a Docker image (e.g. deploying to Vercel).
  output: "standalone",
};

export default nextConfig;

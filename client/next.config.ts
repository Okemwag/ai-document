import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true, // Disable ESLint during build
  },
  /* config options here */
};

export default nextConfig;
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next.js 16 proxy pattern
  async rewrites() {
    return [
      {
        source: "/api/mission-control/:path*",
        destination: `${process.env.BACKEND_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;

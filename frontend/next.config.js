/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Proxy /api/* to the Flask backend in development.
    // In production set NEXT_PUBLIC_API_URL and remove this.
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://localhost:5000"}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

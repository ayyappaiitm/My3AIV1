/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compress: true,
  images: {
    domains: process.env.NEXT_PUBLIC_IMAGE_DOMAINS
      ? process.env.NEXT_PUBLIC_IMAGE_DOMAINS.split(',')
      : [],
    unoptimized: false,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  },
  // Production optimizations
  swcMinify: true,
  poweredByHeader: false,
  // Enable static optimization
  output: 'standalone',
  // Vercel Analytics
  analyticsId: process.env.VERCEL_ANALYTICS_ID,
}

module.exports = nextConfig


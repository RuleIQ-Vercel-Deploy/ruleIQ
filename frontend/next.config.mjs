import { withSentryConfig } from "@sentry/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Transpile GSAP and its plugins for proper SSR support
  transpilePackages: ['gsap', '@gsap/react'],
  
  // Build configuration
  eslint: {
    ignoreDuringBuilds: true, // Allow build to proceed with ESLint warnings
  },
  typescript: {
    ignoreBuildErrors: false, // Enforce TypeScript errors during build
  },

  // Performance optimizations
  images: {
    unoptimized: false, // Enable image optimization in production
    domains: ['api.ruleiq.com', 'staging-api.ruleiq.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Compression
  compress: true,

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ]
  },

  // Redirects for SEO
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ]
  },

  // Bundle optimization and analysis
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Bundle analysis
    if (process.env.ANALYZE === 'true') {
      const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: isServer ? '../analyze/server.html' : './analyze/client.html',
        })
      )
    }

    // Code splitting optimizations
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            reuseExistingChunk: true,
          },
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|lucide-react)[\\/]/,
            name: 'ui',
            priority: 20,
            reuseExistingChunk: true,
          },
          charts: {
            test: /[\\/]node_modules[\\/](recharts|react-chartjs-2|chart\.js)[\\/]/,
            name: 'charts',
            priority: 20,
            reuseExistingChunk: true,
          },
          ai: {
            test: /[\\/](ai|assessments-ai|chat)[\\/]/,
            name: 'ai',
            priority: 15,
            reuseExistingChunk: true,
          },
        },
      }
    }

    return config
  },

  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
}

// Sentry configuration options
const sentryOptions = {
  // Upload source maps during build
  widenClientFileUpload: true,
  
  // Automatically tree-shake Sentry logger statements for better performance
  disableLogger: process.env.NODE_ENV === "production",
  
  // Hide source maps from generated client bundles
  hideSourceMaps: true,
  
  // Only upload source maps in production builds
  dryRun: process.env.NODE_ENV !== "production",
  
  // Disable Sentry CLI prompts during build
  silent: true,
  
  // Upload source maps to Sentry for better error tracking
  sourcemaps: {
    disable: process.env.NODE_ENV !== "production",
    deleteFilesAfterUpload: ["**/*.map"],
  },
  
  // Additional Sentry build configuration
  tunnelRoute: "/monitoring/sentry",
};

// Export the config wrapped with Sentry
export default withSentryConfig(nextConfig, sentryOptions);

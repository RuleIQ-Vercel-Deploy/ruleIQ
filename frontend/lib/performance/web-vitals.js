// Core Web Vitals tracking with Sentry integration
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

// Sentry integration for performance monitoring
let Sentry;
if (typeof window !== 'undefined') {
  Sentry = require('@sentry/nextjs');
}

const vitals = {
  CLS: 0,
  FID: 0,
  FCP: 0,
  LCP: 0,
  TTFB: 0,
};

const thresholds = {
  CLS: [0.1, 0.25],
  FID: [100, 300],
  FCP: [1800, 3000],
  LCP: [2500, 4000],
  TTFB: [800, 1800],
};

function getRating(name, value) {
  const [good, poor] = thresholds[name];
  if (value <= good) return 'good';
  if (value <= poor) return 'needs-improvement';
  return 'poor';
}

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating || getRating(metric.name, metric.value),
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
  });

  // Send to analytics endpoint
  if (typeof window !== 'undefined' && navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/web-vitals', body);
  }

  // Send to Sentry
  if (Sentry) {
    Sentry.metrics.distribution(`web_vitals.${metric.name}`, metric.value, {
      tags: {
        rating: getRating(metric.name, metric.value),
        navigationType: metric.navigationType,
      },
    });
  }

  // Log for debugging
  console.log(
    `[Web Vitals] ${metric.name}: ${metric.value} (${getRating(metric.name, metric.value)})`,
  );
}

export function reportWebVitals() {
  if (typeof window === 'undefined') return;

  try {
    getCLS(sendToAnalytics);
    getFID(sendToAnalytics);
    getFCP(sendToAnalytics);
    getLCP(sendToAnalytics);
    getTTFB(sendToAnalytics);
  } catch (error) {
    console.error('Error reporting web vitals:', error);
  }
}

// Performance observer for additional metrics
export function initPerformanceObserver() {
  if (typeof window === 'undefined') return;

  try {
    // Resource timing
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'resource') {
          // Track slow resources
          if (entry.duration > 1000) {
            console.warn(`Slow resource: ${entry.name} (${entry.duration}ms)`);
          }
        }
      });
    });

    observer.observe({ entryTypes: ['resource', 'navigation', 'paint'] });
  } catch (error) {
    console.error('Error initializing performance observer:', error);
  }
}

// Bundle size monitoring
export function trackBundleSize() {
  if (typeof window === 'undefined') return;

  try {
    // Track JavaScript bundle size
    const jsResources = performance
      .getEntriesByType('resource')
      .filter((entry) => entry.name.includes('.js'))
      .reduce((total, entry) => total + entry.transferSize || 0, 0);

    if (Sentry) {
      Sentry.metrics.distribution('bundle_size.js', jsResources, {
        unit: 'byte',
      });
    }

    console.log(`[Bundle Size] JavaScript: ${(jsResources / 1024 / 1024).toFixed(2)}MB`);
  } catch (error) {
    console.error('Error tracking bundle size:', error);
  }
}

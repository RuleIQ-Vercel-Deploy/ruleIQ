/**
 * K6 Load Testing Configuration for ruleIQ
 * Comprehensive load testing scenarios for production readiness
 */

import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const responseTime = new Trend("response_time");

// Test configuration
export const options = {
  stages: [
    // Ramp-up phase
    { duration: "2m", target: 50 },
    // Steady state
    { duration: "5m", target: 50 },
    // Stress test
    { duration: "2m", target: 100 },
    // Peak load
    { duration: "3m", target: 150 },
    // Ramp-down
    { duration: "2m", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000", "p(99)<5000"],
    http_req_failed: ["rate<0.1"],
    errors: ["rate<0.05"],
  },
};

// Environment configuration
const BASE_URL = __ENV.BASE_URL || "http://localhost:3000";
const API_URL = __ENV.API_URL || "http://localhost:8000";

// Test data
const testUsers = [
  { email: "test1@example.com", password: "Test123!" },
  { email: "test2@example.com", password: "Test123!" },
  { email: "test3@example.com", password: "Test123!" },
];

const testBusinesses = [
  { name: "Tech Startup Ltd", industry: "Technology", size: "small" },
  {
    name: "Consulting Firm Inc",
    industry: "Professional Services",
    size: "medium",
  },
  { name: "Manufacturing Corp", industry: "Manufacturing", size: "large" },
];

// Helper functions
function generateRandomString(length) {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function authenticateUser(user) {
  const loginRes = http.post(
    `${API_URL}/api/auth/login`,
    JSON.stringify({
      email: user.email,
      password: user.password,
    }),
    {
      headers: { "Content-Type": "application/json" },
    }
  );

  check(loginRes, {
    "login successful": (r) => r.status === 200,
    "login response time < 2s": (r) => r.timings.duration < 2000,
  });

  if (loginRes.status === 200) {
    const response = JSON.parse(loginRes.body);
    return response.access_token;
  }
  return null;
}

// Test scenarios
export default function () {
  const user = testUsers[Math.floor(Math.random() * testUsers.length)];
  const token = authenticateUser(user);

  if (!token) {
    errorRate.add(1);
    return;
  }

  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  // Test 1: Dashboard load
  group("Dashboard Load", function () {
    const dashboardRes = http.get(`${BASE_URL}/dashboard`, { headers });
    check(dashboardRes, {
      "dashboard loaded": (r) => r.status === 200,
      "dashboard response time < 3s": (r) => r.timings.duration < 3000,
    });
    responseTime.add(dashboardRes.timings.duration);
  });

  // Test 2: Assessment creation
  group("Assessment Creation", function () {
    const business =
      testBusinesses[Math.floor(Math.random() * testBusinesses.length)];
    const assessmentRes = http.post(
      `${API_URL}/api/assessments`,
      JSON.stringify({
        name: `Load Test Assessment ${generateRandomString(8)}`,
        business_profile: business,
        framework: "gdpr",
      }),
      { headers }
    );

    check(assessmentRes, {
      "assessment created": (r) => r.status === 201,
      "assessment response time < 5s": (r) => r.timings.duration < 5000,
    });
    responseTime.add(assessmentRes.timings.duration);
  });

  // Test 3: Evidence upload simulation
  group("Evidence Upload", function () {
    const formData = {
      file: http.file("dummy.pdf", "dummy content"),
      type: "policy",
      category: "data-protection",
    };

    const uploadRes = http.post(`${API_URL}/api/evidence`, formData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    check(uploadRes, {
      "evidence uploaded": (r) => r.status === 201,
      "upload response time < 10s": (r) => r.timings.duration < 10000,
    });
    responseTime.add(uploadRes.timings.duration);
  });

  // Test 4: API health check
  group("Health Check", function () {
    const healthRes = http.get(`${API_URL}/api/health`);
    check(healthRes, {
      "health check passed": (r) => r.status === 200,
      "health response time < 1s": (r) => r.timings.duration < 1000,
    });
  });

  // Test 5: Search functionality
  group("Search Functionality", function () {
    const searchTerm = generateRandomString(5);
    const searchRes = http.get(`${API_URL}/api/search?q=${searchTerm}`, {
      headers,
    });

    check(searchRes, {
      "search completed": (r) => r.status === 200,
      "search response time < 3s": (r) => r.timings.duration < 3000,
    });
    responseTime.add(searchRes.timings.duration);
  });

  sleep(1);
}

// Smoke test configuration
export function smokeTest() {
  return {
    stages: [
      { duration: "30s", target: 5 },
      { duration: "1m", target: 5 },
      { duration: "30s", target: 0 },
    ],
    thresholds: {
      http_req_duration: ["p(95)<1000"],
      http_req_failed: ["rate<0.05"],
    },
  };
}

// Stress test configuration
export function stressTest() {
  return {
    stages: [
      { duration: "2m", target: 100 },
      { duration: "5m", target: 100 },
      { duration: "2m", target: 200 },
      { duration: "5m", target: 200 },
      { duration: "2m", target: 300 },
      { duration: "5m", target: 300 },
      { duration: "2m", target: 0 },
    ],
    thresholds: {
      http_req_duration: ["p(95)<5000"],
      http_req_failed: ["rate<0.1"],
    },
  };
}

// API-only test configuration
export function apiTest() {
  return {
    stages: [
      { duration: "1m", target: 50 },
      { duration: "3m", target: 50 },
      { duration: "1m", target: 100 },
      { duration: "3m", target: 100 },
      { duration: "1m", target: 0 },
    ],
    thresholds: {
      http_req_duration: ["p(95)<1000"],
      http_req_failed: ["rate<0.05"],
    },
  };
}

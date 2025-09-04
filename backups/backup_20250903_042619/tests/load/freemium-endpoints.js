// K6 Load Test Script for AI Assessment Freemium Strategy
// Tests all freemium endpoints under realistic load conditions

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const emailCaptureRate = new Rate('email_capture_success_rate');
const assessmentStartRate = new Rate('assessment_start_success_rate');
const questionAnswerRate = new Rate('question_answer_success_rate');
const resultsViewRate = new Rate('results_view_success_rate');
const conversionTrackRate = new Rate('conversion_track_success_rate');

const responseTimeEmailCapture = new Trend('email_capture_response_time');
const responseTimeAssessment = new Trend('assessment_response_time');
const responseTimeAI = new Trend('ai_processing_time');

const totalErrors = new Counter('total_errors');
const rateLimitHits = new Counter('rate_limit_hits');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 20 },   // Ramp up to 20 users
    { duration: '5m', target: 50 },   // Stay at 50 users  
    { duration: '10m', target: 100 }, // Peak load at 100 users
    { duration: '5m', target: 50 },   // Scale down to 50 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.05'],     // Error rate under 5%
    email_capture_success_rate: ['rate>0.95'], // 95% success rate for email capture
    assessment_start_success_rate: ['rate>0.90'], // 90% success rate for assessments
    rate_limit_hits: ['count<100'],     // Fewer than 100 rate limit hits
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test data generators
function generateEmail() {
  const domains = ['example.com', 'test.com', 'demo.com'];
  const randomDomain = domains[Math.floor(Math.random() * domains.length)];
  return `test.user.${Math.random().toString(36).substring(2, 15)}@${randomDomain}`;
}

function generateCompanyData() {
  const companies = ['Tech Corp', 'Digital Solutions', 'Compliance Inc', 'Security Ltd'];
  const sizes = ['1-10', '11-50', '51-200', '201-1000'];
  const industries = ['Technology', 'Finance', 'Healthcare', 'Retail'];
  
  return {
    company_name: companies[Math.floor(Math.random() * companies.length)],
    company_size: sizes[Math.floor(Math.random() * sizes.length)],
    industry: industries[Math.floor(Math.random() * industries.length)]
  };
}

function generateUTMParams() {
  const sources = ['google', 'facebook', 'linkedin', 'direct'];
  const mediums = ['cpc', 'social', 'email', 'organic'];
  const campaigns = ['freemium-launch', 'compliance-awareness', 'gdpr-assessment'];
  
  return {
    utm_source: sources[Math.floor(Math.random() * sources.length)],
    utm_medium: mediums[Math.floor(Math.random() * mediums.length)],
    utm_campaign: campaigns[Math.floor(Math.random() * campaigns.length)]
  };
}

// Main test function
export default function () {
  const email = generateEmail();
  const companyData = generateCompanyData();
  const utmParams = generateUTMParams();
  
  group('Freemium Email Capture Flow', function () {
    testEmailCapture(email, companyData, utmParams);
  });
  
  sleep(Math.random() * 2 + 1); // Random sleep 1-3 seconds
}

function testEmailCapture(email, companyData, utmParams) {
  // Test email capture endpoint
  group('Email Capture', function () {
    const emailCapturePayload = {
      email: email,
      first_name: 'Test',
      last_name: 'User',
      ...companyData,
      ...utmParams,
      landing_page: '/freemium',
      referrer_url: 'https://google.com'
    };
    
    const startTime = new Date().getTime();
    const emailResponse = http.post(
      `${BASE_URL}/api/v1/freemium/capture-email`,
      JSON.stringify(emailCapturePayload),
      {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'k6-load-test/1.0',
          'Accept': 'application/json'
        },
        timeout: '30s'
      }
    );
    
    const emailCaptureTime = new Date().getTime() - startTime;
    responseTimeEmailCapture.add(emailCaptureTime);
    
    const emailCaptureSuccess = check(emailResponse, {
      'email capture status is 200 or 201': (r) => r.status === 200 || r.status === 201,
      'email capture returns token': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.token && data.token.length > 0;
        } catch (e) {
          return false;
        }
      },
      'email capture response time < 5s': () => emailCaptureTime < 5000,
    });
    
    emailCaptureRate.add(emailCaptureSuccess);
    
    if (emailResponse.status === 429) {
      rateLimitHits.add(1);
      console.log('Rate limit hit on email capture');
      return;
    }
    
    if (!emailCaptureSuccess) {
      totalErrors.add(1);
      console.log(`Email capture failed: ${emailResponse.status} - ${emailResponse.body}`);
      return;
    }
    
    // Extract token for next steps
    let token;
    try {
      const emailData = JSON.parse(emailResponse.body);
      token = emailData.token;
    } catch (e) {
      console.log('Failed to parse email capture response');
      totalErrors.add(1);
      return;
    }
    
    // Test assessment start
    testAssessmentStart(token);
  });
}

function testAssessmentStart(token) {
  group('Assessment Start', function () {
    const assessmentPayload = {
      token: token
    };
    
    const startTime = new Date().getTime();
    const assessmentResponse = http.post(
      `${BASE_URL}/api/v1/freemium/start-assessment`,
      JSON.stringify(assessmentPayload),
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'k6-load-test/1.0'
        },
        timeout: '60s' // AI processing can take longer
      }
    );
    
    const assessmentTime = new Date().getTime() - startTime;
    responseTimeAssessment.add(assessmentTime);
    
    if (assessmentTime > 30000) {
      responseTimeAI.add(assessmentTime);
    }
    
    const assessmentSuccess = check(assessmentResponse, {
      'assessment start status is 200': (r) => r.status === 200,
      'assessment returns session data': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.session_id && data.questions && data.questions.length > 0;
        } catch (e) {
          return false;
        }
      },
      'assessment response time < 30s': () => assessmentTime < 30000,
    });
    
    assessmentStartRate.add(assessmentSuccess);
    
    if (assessmentResponse.status === 429) {
      rateLimitHits.add(1);
      console.log('Rate limit hit on assessment start');
      return;
    }
    
    if (!assessmentSuccess) {
      totalErrors.add(1);
      console.log(`Assessment start failed: ${assessmentResponse.status} - ${assessmentResponse.body}`);
      return;
    }
    
    // Extract session info for next steps
    let sessionData;
    try {
      sessionData = JSON.parse(assessmentResponse.body);
    } catch (e) {
      console.log('Failed to parse assessment response');
      totalErrors.add(1);
      return;
    }
    
    // Test answering questions
    testQuestionAnswering(token, sessionData);
  });
}

function testQuestionAnswering(token, sessionData) {
  group('Question Answering', function () {
    const questions = sessionData.questions || [];
    const questionsToAnswer = Math.min(questions.length, 3); // Answer up to 3 questions
    
    for (let i = 0; i < questionsToAnswer; i++) {
      const question = questions[i];
      const answerPayload = {
        token: token,
        question_id: question.id,
        answer: generateAnswerForQuestion(question)
      };
      
      const startTime = new Date().getTime();
      const answerResponse = http.post(
        `${BASE_URL}/api/v1/freemium/answer-question`,
        JSON.stringify(answerPayload),
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'User-Agent': 'k6-load-test/1.0'
          },
          timeout: '45s'
        }
      );
      
      const answerTime = new Date().getTime() - startTime;
      
      const answerSuccess = check(answerResponse, {
        'question answer status is 200': (r) => r.status === 200,
        'question answer response time < 15s': () => answerTime < 15000,
      });
      
      questionAnswerRate.add(answerSuccess);
      
      if (answerResponse.status === 429) {
        rateLimitHits.add(1);
        break;
      }
      
      if (!answerSuccess) {
        totalErrors.add(1);
        break;
      }
      
      // Small delay between questions
      sleep(0.5);
    }
    
    // Test getting results after answering questions
    testResultsViewing(token);
  });
}

function testResultsViewing(token) {
  group('Results Viewing', function () {
    // Wait a bit for processing
    sleep(2);
    
    const startTime = new Date().getTime();
    const resultsResponse = http.get(
      `${BASE_URL}/api/v1/freemium/results/${token}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'k6-load-test/1.0'
        },
        timeout: '30s'
      }
    );
    
    const resultsTime = new Date().getTime() - startTime;
    
    const resultsSuccess = check(resultsResponse, {
      'results status is 200': (r) => r.status === 200,
      'results contain analysis': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.compliance_score !== undefined && data.recommendations;
        } catch (e) {
          return false;
        }
      },
      'results response time < 10s': () => resultsTime < 10000,
    });
    
    resultsViewRate.add(resultsSuccess);
    
    if (resultsResponse.status === 429) {
      rateLimitHits.add(1);
      return;
    }
    
    if (!resultsSuccess) {
      totalErrors.add(1);
      return;
    }
    
    // Test conversion tracking
    testConversionTracking(token);
  });
}

function testConversionTracking(token) {
  group('Conversion Tracking', function () {
    const conversionPayload = {
      token: token,
      event_type: 'cta_click',
      event_category: 'conversion',
      event_action: 'get_compliant_now_click',
      page_url: '/freemium/results',
      conversion_value: Math.random() > 0.1 ? null : 99.99 // 10% actually convert
    };
    
    const conversionResponse = http.post(
      `${BASE_URL}/api/v1/freemium/track-conversion`,
      JSON.stringify(conversionPayload),
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'k6-load-test/1.0'
        },
        timeout: '15s'
      }
    );
    
    const conversionSuccess = check(conversionResponse, {
      'conversion tracking status is 200': (r) => r.status === 200,
    });
    
    conversionTrackRate.add(conversionSuccess);
    
    if (conversionResponse.status === 429) {
      rateLimitHits.add(1);
    }
    
    if (!conversionSuccess) {
      totalErrors.add(1);
    }
  });
}

function generateAnswerForQuestion(question) {
  // Generate realistic answers based on question type
  if (question.type === 'yes_no') {
    return Math.random() > 0.5 ? 'yes' : 'no';
  } else if (question.type === 'multiple_choice' && question.options) {
    const randomIndex = Math.floor(Math.random() * question.options.length);
    return question.options[randomIndex];
  } else if (question.type === 'scale') {
    return Math.floor(Math.random() * 5) + 1; // 1-5 scale
  } else {
    // Text answer
    const textAnswers = [
      'We have basic policies in place',
      'Currently under review',
      'Yes, fully implemented',
      'No, not yet addressed',
      'Partially implemented'
    ];
    return textAnswers[Math.floor(Math.random() * textAnswers.length)];
  }
}

// Teardown function
export function teardown(data) {
  console.log('Load test completed');
  console.log(`Total errors: ${totalErrors.value}`);
  console.log(`Rate limit hits: ${rateLimitHits.value}`);
}
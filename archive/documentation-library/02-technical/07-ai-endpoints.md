# AI Assessment Endpoints Documentation

## Overview

The ruleIQ AI Assessment API provides intelligent compliance assistance through four main endpoints. These endpoints leverage advanced AI to provide contextual guidance, generate follow-up questions, analyze assessment results, and create personalized recommendations.

## Rate Limiting

All AI endpoints implement tiered rate limiting to ensure fair usage and optimal performance:

| Endpoint | Rate Limit | Burst Allowance | Description |
|----------|------------|-----------------|-------------|
| AI Help | 10 req/min | 2 extra | Quick guidance for assessment questions |
| AI Follow-up | 5 req/min | 1 extra | Generate additional assessment questions |
| AI Analysis | 3 req/min | 1 extra | Comprehensive assessment analysis |
| AI Recommendations | 3 req/min | 1 extra | Personalized implementation recommendations |

### Rate Limit Headers

All responses include rate limiting information:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640995200
X-RateLimit-Operation: help
Retry-After: 45 (only when rate limited)
```

### Rate Limit Error Response

When rate limited, endpoints return HTTP 429 with detailed information:

```json
{
  "error": {
    "message": "AI help rate limit exceeded",
    "code": "AI_RATE_LIMIT_EXCEEDED",
    "operation": "help",
    "limit": 10,
    "window": "1 minute",
    "retry_after": 45,
    "burst_allowance": 2
  },
  "suggestion": "Please wait 45 seconds before making another help request."
}
```

## Authentication

All AI endpoints require authentication via Bearer token:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### 1. AI Question Help

**POST** `/api/ai/assessments/{framework_id}/help`

Get AI-powered contextual guidance for specific assessment questions.

#### Parameters

- `framework_id` (path): The compliance framework ID (e.g., "gdpr", "iso27001")

#### Request Body

```json
{
  "question_id": "q_data_retention",
  "question_text": "Do you have documented data retention policies?",
  "section_id": "data_protection",
  "user_context": {
    "business_profile": {
      "industry": "technology",
      "employee_count": 150,
      "handles_personal_data": true
    },
    "current_answers": {
      "data_protection_officer": "yes",
      "gdpr_training": "partial"
    },
    "assessment_progress": {
      "completed_sections": ["governance"],
      "current_section": "data_protection"
    }
  }
}
```

#### Response

```json
{
  "guidance": "Data retention policies are crucial for GDPR compliance. You should document specific retention periods for different categories of personal data, ensure you have legal basis for retention, and implement automatic deletion processes where possible.",
  "confidence_score": 0.92,
  "related_topics": [
    "Data Protection by Design",
    "Right to Erasure",
    "Data Minimization"
  ],
  "follow_up_suggestions": [
    "Review your current data retention schedule",
    "Consult with your legal team on retention requirements",
    "Consider implementing automated deletion tools"
  ],
  "source_references": [
    "GDPR Article 5(1)(e)",
    "GDPR Recital 39"
  ],
  "request_id": "help_gdpr_q_data_retention_1640995200",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### 2. AI Follow-up Questions

**POST** `/api/ai/assessments/followup`

Generate intelligent follow-up questions based on current assessment responses.

#### Request Body

```json
{
  "current_question_id": "q_data_retention",
  "user_response": "We have informal data retention practices",
  "framework_id": "gdpr",
  "context": {
    "business_profile": {
      "industry": "healthcare",
      "employee_count": 500,
      "data_sensitivity": "high"
    },
    "current_answers": {
      "data_retention": "informal",
      "automated_deletion": "no",
      "retention_schedule": "no"
    }
  }
}
```

#### Response

```json
{
  "questions": [
    {
      "id": "followup_retention_schedule",
      "text": "What types of personal data do you collect and how long do you typically keep each type?",
      "type": "textarea",
      "reasoning": "Understanding data categories helps create proper retention schedules",
      "priority": "high",
      "options": null
    },
    {
      "id": "followup_deletion_process",
      "text": "How do you currently handle data deletion requests from individuals?",
      "type": "radio",
      "reasoning": "GDPR requires clear processes for data subject rights",
      "priority": "high",
      "options": [
        {"value": "manual", "label": "Manual process with documentation"},
        {"value": "automated", "label": "Automated system"},
        {"value": "none", "label": "No formal process"}
      ]
    }
  ],
  "total_generated": 2,
  "request_id": "followup_gdpr_1640995200",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### 3. AI Assessment Analysis

**POST** `/api/ai/assessments/analysis`

Perform comprehensive AI analysis of completed assessment results.

#### Request Body

```json
{
  "framework_id": "gdpr",
  "business_profile_id": "bp_12345",
  "assessment_results": {
    "answers": {
      "data_retention": "informal",
      "privacy_policy": "yes",
      "dpo_appointed": "no",
      "staff_training": "partial"
    },
    "completion_percentage": 85.5,
    "sections_completed": ["governance", "data_protection", "security"],
    "assessment_duration_minutes": 45
  }
}
```

#### Response

```json
{
  "gaps": [
    {
      "id": "gap_dpo_appointment",
      "description": "Data Protection Officer not appointed despite processing personal data",
      "priority": "high",
      "control_reference": "GDPR Article 37",
      "impact": "Legal requirement violation, potential fines up to 4% of annual turnover",
      "remediation_effort": "2-4 weeks"
    }
  ],
  "recommendations": [
    {
      "id": "rec_appoint_dpo",
      "title": "Appoint Data Protection Officer",
      "description": "Recruit or designate a qualified DPO to oversee GDPR compliance",
      "priority": "immediate",
      "effort_estimate": "2-4 weeks",
      "impact_score": 9.2,
      "resources": ["Legal Team", "HR Department"],
      "implementation_steps": [
        "Define DPO role requirements",
        "Recruit qualified candidate or train internal staff",
        "Formally appoint and communicate role"
      ]
    }
  ],
  "risk_assessment": {
    "overall_risk_level": "high",
    "risk_score": 7.8,
    "key_risk_areas": ["Data Protection Officer", "Staff Training", "Data Retention"]
  },
  "compliance_insights": {
    "maturity_level": "developing",
    "score_breakdown": {
      "governance": 75,
      "data_protection": 60,
      "security": 80,
      "incident_response": 45
    },
    "improvement_priority": [
      "Data Protection Officer appointment",
      "Comprehensive staff training program",
      "Formal data retention policies"
    ]
  },
  "evidence_requirements": [
    {
      "priority": "high",
      "evidence_type": "appointment_letter",
      "description": "DPO appointment letter and role definition",
      "control_mapping": ["GDPR Article 37", "ISO 27001 A.6.1.1"]
    }
  ],
  "request_id": "analysis_gdpr_bp_12345_1640995200",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### 4. AI Personalized Recommendations

**POST** `/api/ai/assessments/recommendations`

Generate personalized compliance recommendations with detailed implementation plans.

#### Request Body

```json
{
  "gaps": [
    {
      "id": "gap_dpo_appointment",
      "description": "Data Protection Officer not appointed",
      "priority": "high",
      "control_reference": "GDPR Article 37"
    }
  ],
  "business_profile": {
    "industry": "technology",
    "employee_count": 150,
    "annual_revenue": "£5M-£25M",
    "data_sensitivity": "high"
  },
  "existing_policies": ["Privacy Policy", "Security Policy"],
  "industry_context": "Technology sector with high data processing volumes",
  "timeline_preferences": "urgent"
}
```

#### Response

```json
{
  "recommendations": [
    {
      "id": "rec_dpo_tech_startup",
      "title": "Appoint Technical DPO for Growing Tech Company",
      "description": "Given your technology focus and growth trajectory, appoint a DPO with both legal and technical expertise",
      "priority": "immediate",
      "effort_estimate": "3-4 weeks",
      "impact_score": 9.5,
      "resources": ["Legal Team", "HR", "Technical Leadership"],
      "implementation_steps": [
        "Define DPO requirements for tech environment",
        "Source candidates with GDPR + technical background",
        "Establish DPO reporting structure and tools access"
      ]
    }
  ],
  "implementation_plan": {
    "phases": [
      {
        "phase_number": 1,
        "phase_name": "Immediate Compliance (Weeks 1-2)",
        "duration_weeks": 2,
        "tasks": [
          "Interim DPO appointment",
          "Immediate risk assessment",
          "Critical gap remediation"
        ],
        "dependencies": []
      },
      {
        "phase_number": 2,
        "phase_name": "Permanent Structure (Weeks 3-4)",
        "duration_weeks": 2,
        "tasks": [
          "Permanent DPO recruitment",
          "Process documentation",
          "Team training"
        ],
        "dependencies": ["Phase 1 completion"]
      }
    ],
    "total_timeline_weeks": 4,
    "resource_requirements": [
      "DPO (1.0 FTE)",
      "Legal Counsel (0.2 FTE)",
      "HR Support (0.1 FTE)"
    ]
  },
  "success_metrics": [
    "DPO appointed within 4 weeks",
    "All staff aware of DPO contact details",
    "DPO integrated into product development process"
  ],
  "request_id": "recommendations_tech_150emp_1640995200",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

## Error Handling

All endpoints follow consistent error response format:

### 400 Bad Request
```json
{
  "error": {
    "message": "Invalid request format",
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "question_id",
      "issue": "Required field missing"
    }
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "message": "Authentication required",
    "code": "UNAUTHORIZED"
  }
}
```

### 429 Too Many Requests
```json
{
  "error": {
    "message": "AI help rate limit exceeded",
    "code": "AI_RATE_LIMIT_EXCEEDED",
    "retry_after": 45
  }
}
```

### 503 Service Unavailable
```json
{
  "error": {
    "message": "AI service temporarily unavailable",
    "code": "AI_SERVICE_UNAVAILABLE",
    "fallback_available": true
  }
}
```

## Best Practices

1. **Rate Limiting**: Implement client-side rate limiting to avoid hitting limits
2. **Caching**: Cache AI responses for identical requests to improve performance
3. **Error Handling**: Always handle rate limiting and service unavailability gracefully
4. **Context**: Provide rich context for better AI recommendations
5. **Monitoring**: Monitor response times and success rates for optimal user experience

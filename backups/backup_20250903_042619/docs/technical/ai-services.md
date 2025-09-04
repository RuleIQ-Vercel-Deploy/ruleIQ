# AI Cost Management System Integration Guide

## Overview

The AI Cost Management system provides comprehensive cost tracking, budgeting, optimization, and real-time monitoring for AI services in ruleIQ. This guide covers integration steps, API usage, and best practices.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Cost Management                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Cost Tracking  │  │ Budget Alerts   │  │ Optimization│  │
│  │  Service        │  │ Service         │  │ Service     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│           │                     │                    │       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Cost-Aware      │  │ Real-time       │  │ Analytics & │  │
│  │ Circuit Breaker │  │ WebSocket       │  │ Reporting   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Storage Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │     Redis       │  │   PostgreSQL    │  │  WebSocket  │  │
│  │ (Real-time)     │  │ (Persistence)   │  │ Connections │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Database Setup

Add the cost management tables to your database:

```bash
# Add cost models to your migration
alembic revision --autogenerate -m "Add AI cost management tables"
alembic upgrade head
```

### 2. Environment Configuration

Add to your `.env` file:

```env
# AI Cost Management
ENABLE_COST_TRACKING=true
ENABLE_BUDGET_ENFORCEMENT=true
DAILY_COST_LIMIT=100.00
MONTHLY_COST_LIMIT=2500.00

# Redis for real-time tracking
REDIS_URL=redis://localhost:6379/0

# WebSocket settings
ENABLE_REALTIME_MONITORING=true
```

### 3. Enable Middleware

Add the cost tracking middleware to your FastAPI app:

```python
from api.middleware.cost_tracking_middleware import CostTrackingMiddleware

app.add_middleware(
    CostTrackingMiddleware,
    enable_budget_enforcement=True,
    enable_cost_optimization=True
)
```

### 4. Include API Routes

Add cost management routes to your application:

```python
from api.routers import ai_cost_monitoring, ai_cost_websocket

app.include_router(ai_cost_monitoring.router)
app.include_router(ai_cost_websocket.router)
```

## API Endpoints

### Cost Tracking

**Track AI Usage**
```http
POST /api/v1/ai/cost/track
Content-Type: application/json

{
  "service_name": "policy_generation",
  "model_name": "gemini-1.5-pro",
  "input_tokens": 1500,
  "output_tokens": 2000,
  "response_quality_score": 0.95,
  "response_time_ms": 1250.5
}
```

**Get Daily Analytics**
```http
GET /api/v1/ai/cost/analytics/daily?target_date=2025-01-27&include_hourly=true
```

**Get Cost Trends**
```http
GET /api/v1/ai/cost/analytics/trends?days=7&include_anomalies=true
```

### Budget Management

**Configure Budget**
```http
POST /api/v1/ai/cost/budget/configure
Content-Type: application/json

{
  "daily_limit": 50.00,
  "monthly_limit": 1200.00,
  "service_limits": {
    "policy_generation": 25.00,
    "assessment_analysis": 15.00
  }
}
```

**Get Budget Status**
```http
GET /api/v1/ai/cost/budget/status
```

**Get Active Alerts**
```http
GET /api/v1/ai/cost/alerts
```

### Optimization

**Get Recommendations**
```http
GET /api/v1/ai/cost/optimization/recommendations
```

**Intelligent Model Selection**
```http
POST /api/v1/ai/cost/routing/select-model
Content-Type: application/json

{
  "task_description": "Generate a comprehensive privacy policy for an e-commerce platform",
  "task_type": "policy_generation",
  "max_cost_per_request": 0.50
}
```

### Reporting

**Monthly Report**
```http
GET /api/v1/ai/cost/reports/monthly?year=2025&month=1&format=json
```

**Service Usage Analysis**
```http
GET /api/v1/ai/cost/usage/by-service?service_name=policy_generation&start_date=2025-01-20&end_date=2025-01-27
```

## WebSocket Integration

### Real-time Dashboard

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ai/cost/ws/realtime-dashboard?user_id=123&dashboard_type=admin');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'initial_data':
            updateDashboard(data.data);
            break;
        case 'cost_update':
            updateCostMetrics(data.data);
            break;
        case 'budget_alert':
            showBudgetAlert(data.data);
            break;
    }
};

// Subscribe to specific events
ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['cost_update', 'budget_alert', 'cost_spike']
}));
```

### Budget Alerts

```javascript
const alertsWs = new WebSocket('ws://localhost:8000/api/v1/ai/cost/ws/budget-alerts?user_id=123');

alertsWs.onmessage = function(event) {
    const alert = JSON.parse(event.data);
    
    if (alert.type === 'budget_alert') {
        displayBudgetAlert(alert.data);
    }
};
```

## Integration with Existing Services

### Circuit Breaker Integration

Replace your existing circuit breaker with the cost-aware version:

```python
from services.ai.cost_aware_circuit_breaker import execute_with_cost_and_circuit_protection

# In your AI service calls
result = await execute_with_cost_and_circuit_protection(
    model_name="gemini-1.5-pro",
    service_name="policy_generation",
    operation=generate_policy_content,
    input_tokens=1500,
    output_tokens=2000,
    user_id=str(current_user.id),
    prompt_data,
    business_context
)
```

### Service-Level Integration

Modify your AI services to include cost tracking:

```python
from services.ai.cost_management import AICostManager

class PolicyGeneratorService:
    def __init__(self):
        self.cost_manager = AICostManager()
    
    async def generate_policy(self, request, user_id):
        # Your existing logic...
        
        # Track the AI request
        cost_result = await self.cost_manager.track_ai_request(
            service_name="policy_generation",
            model_name=model_used,
            input_prompt=input_text,
            response_content=generated_policy,
            input_tokens=token_usage.input_tokens,
            output_tokens=token_usage.output_tokens,
            user_id=user_id
        )
        
        return {
            "policy_content": generated_policy,
            "cost_info": {
                "cost_usd": cost_result["cost_usd"],
                "efficiency_score": cost_result["efficiency_score"]
            }
        }
```

## Model Cost Configuration

Configure model costs in the database:

```sql
INSERT INTO ai_model_configs (
    model_name, provider, input_cost_per_million, output_cost_per_million,
    context_window, max_output_tokens, is_active
) VALUES 
    ('gemini-1.5-pro', 'google', 3.50, 10.50, 1048576, 8192, true),
    ('gemini-1.5-flash', 'google', 0.075, 0.30, 1048576, 8192, true),
    ('gpt-4-turbo', 'openai', 10.00, 30.00, 128000, 4096, true);
```

## Budget Configuration Examples

### Global Budget
```python
from services.ai.cost_management import AICostManager

cost_manager = AICostManager()

# Set daily budget
await cost_manager.set_daily_budget(Decimal("100.00"))

# Set service-specific budgets
await cost_manager.budget_service.set_service_budget("policy_generation", Decimal("40.00"))
await cost_manager.budget_service.set_service_budget("assessment_analysis", Decimal("30.00"))
```

### User-Level Budgets
```python
# Set per-user daily limits
await cost_manager.set_user_daily_limit("user_123", Decimal("25.00"))
await cost_manager.set_user_daily_limit("admin_user", Decimal("100.00"))
```

## Optimization Strategies

### Intelligent Model Routing

```python
from services.ai.cost_management import IntelligentModelRouter

router = IntelligentModelRouter()

# Select optimal model based on task
model_choice = await router.select_optimal_model(
    task_description="Simple compliance question",
    task_type="question_answering",
    max_cost_per_request=Decimal("0.10")
)

# Use recommended model
chosen_model = model_choice["model"]  # e.g., "gemini-1.5-flash"
```

### Dynamic Caching

```python
from services.ai.cost_management import DynamicCacheManager

cache_manager = DynamicCacheManager()

# Check if request should be cached
should_cache = await cache_manager.should_cache_request({
    "estimated_cost": Decimal("0.15"),
    "frequency": 5,  # Seen 5 times
    "prompt_hash": "abc123..."
})

if should_cache:
    # Implement caching logic
    pass
```

### Batch Processing

```python
from services.ai.cost_management import BatchRequestOptimizer

optimizer = BatchRequestOptimizer()

# Optimize multiple requests
batch_result = await optimizer.optimize_batch([
    {"prompt": "Analyze requirement 1"},
    {"prompt": "Analyze requirement 2"},
    {"prompt": "Analyze requirement 3"}
])

if batch_result["batched"]:
    # Use combined prompt for cost savings
    combined_prompt = batch_result["combined_prompt"]
    savings = batch_result["cost_savings"]
```

## Monitoring and Alerting

### Custom Alert Thresholds

```python
# Configure budget alerts
await cost_manager.budget_service.set_daily_budget(Decimal("50.00"))

# Set custom alert thresholds
budget_config = {
    "warning_threshold": 75.0,  # 75% of budget
    "critical_threshold": 90.0  # 90% of budget
}
```

### Webhook Integration

```python
# Configure webhook for alerts (in production)
webhook_config = {
    "budget_alerts": "https://your-domain.com/webhooks/budget-alert",
    "cost_spikes": "https://your-domain.com/webhooks/cost-spike"
}
```

## Best Practices

### 1. Cost Tracking
- Track all AI requests automatically using middleware
- Include user context for proper attribution
- Monitor response quality to calculate efficiency

### 2. Budget Management
- Set conservative budgets initially
- Use service-specific limits for granular control
- Implement user-level limits for multi-tenant scenarios

### 3. Optimization
- Review optimization recommendations weekly
- Implement model routing for cost-effective choices
- Use caching for repeated similar requests

### 4. Monitoring
- Set up real-time dashboards for stakeholders
- Configure alerts for budget thresholds
- Monitor cost trends and anomalies

### 5. Reporting
- Generate monthly cost reports for analysis
- Track ROI and cost per user/feature
- Use forecasting for budget planning

## Troubleshooting

### Common Issues

**High Costs**
1. Check for inefficient prompts (too verbose)
2. Verify model selection (using expensive models for simple tasks)
3. Look for lack of caching on repeated requests

**Budget Alerts Not Working**
1. Verify Redis connection for real-time tracking
2. Check budget configuration in database
3. Ensure middleware is properly enabled

**Inaccurate Cost Tracking**
1. Verify model cost configurations
2. Check token counting accuracy
3. Ensure all AI requests go through tracking

**WebSocket Connection Issues**
1. Check WebSocket endpoint accessibility
2. Verify authentication for WebSocket connections
3. Monitor connection manager for disconnections

### Debug Commands

```bash
# Check cost tracking status
curl -X GET "http://localhost:8000/api/v1/ai/cost/health"

# Get connection stats
curl -X GET "http://localhost:8000/api/v1/ai/cost/ws/connections/stats"

# Test budget configuration
curl -X GET "http://localhost:8000/api/v1/ai/cost/budget/status"
```

## Performance Considerations

### Redis Usage
- Use appropriate TTL for cached data
- Monitor Redis memory usage
- Consider Redis clustering for high scale

### Database Optimization
- Index frequently queried columns
- Use aggregation tables for reporting
- Archive old usage logs periodically

### WebSocket Scaling
- Limit concurrent connections per user
- Implement connection pooling
- Use Redis for multi-instance coordination

## Security

### Authentication
- Authenticate all API requests
- Validate WebSocket connections
- Implement rate limiting

### Data Privacy
- Don't store sensitive prompt content
- Hash or encrypt user identifiers
- Implement data retention policies

### Budget Security
- Validate budget modifications
- Audit budget changes
- Implement approval workflows for large budgets

This integration guide provides comprehensive coverage of the AI cost management system. Follow the steps sequentially for a smooth integration experience.
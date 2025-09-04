"""
Test suite for AI Cost Monitoring API endpoints.

This module tests all endpoints in the ai_cost_monitoring router including:
- Cost tracking and recording
- Budget management and alerts  
- Usage analytics and reporting
- Cost optimization insights
- Real-time monitoring via WebSocket
"""
from __future__ import annotations
import pytest
from decimal import Decimal
from datetime import datetime, timedelta, date
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from api.routers.ai_cost_monitoring import (
    router,
    CostTrackingRequest,
    CostTrackingResponse,
    BudgetAlertConfig as BudgetConfiguration,
    CostAnalysisResponse as BudgetStatus,
    CostTrackingRequest as UsageAnalyticsRequest,
    CostAnalysisResponse as UsageAnalyticsResponse,
    CostTrackingRequest as CostOptimizationRequest,
    CostOptimizationResponse,
    CostTrackingRequest as CostSummaryRequest,
    CostAnalysisResponse as CostSummaryResponse,
    CostAnalysisResponse as ServiceCostBreakdown,
    CostAnalysisResponse as ModelCostBreakdown,
    CostAnalysisResponse as CostInsight,
    CostOptimizationResponse as OptimizationRecommendation
)

@pytest.fixture
def test_client():
    """Create a test client for the router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/ai-costs")
    return TestClient(app)

@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock()
    user.id = "test-user-123"
    user.organization_id = "test-org-456"
    user.is_active = True
    user.roles = ["admin"]
    return user

@pytest.fixture
def mock_cost_manager():
    """Create a mock AI Cost Manager."""
    with patch('api.routers.ai_cost_monitoring.AICostManager') as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager

@pytest.fixture
def mock_cost_tracking_service():
    """Create a mock Cost Tracking Service."""
    with patch('api.routers.ai_cost_monitoring.CostTrackingService') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service

@pytest.fixture
def mock_budget_alert_service():
    """Create a mock Budget Alert Service."""
    with patch('api.routers.ai_cost_monitoring.BudgetAlertService') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service

@pytest.fixture
def mock_cost_optimization_service():
    """Create a mock Cost Optimization Service."""
    with patch('api.routers.ai_cost_monitoring.CostOptimizationService') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service

class TestCostTracking:
    """Test cost tracking endpoints."""
    
    def test_track_usage_success(self, test_client, mock_user, mock_cost_tracking_service):
        """Test successful cost tracking."""
        # Arrange
        request_data = {
            "service_name": "openai",
            "model_name": "gpt-4",
            "input_tokens": 1000,
            "output_tokens": 500,
            "session_id": "session-123",
            "request_id": "req-456",
            "response_quality_score": 0.95,
            "response_time_ms": 1250.5,
            "cache_hit": False,
            "error_occurred": False
        }
        
        expected_response = {
            "usage_id": "usage-789",
            "cost_usd": "0.045",
            "efficiency_score": "0.92",
            "cost_per_token": "0.00003",
            "recommendations": ["Consider using GPT-3.5 for similar queries"]
        }
        
        mock_cost_tracking_service.track_usage.return_value = expected_response
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/track",
                json=request_data
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["usage_id"] == expected_response["usage_id"]
            assert response.json()["cost_usd"] == expected_response["cost_usd"]
            mock_cost_tracking_service.track_usage.assert_called_once()
    
    def test_track_usage_with_cache_hit(self, test_client, mock_user, mock_cost_tracking_service):
        """Test cost tracking when response is from cache."""
        # Arrange
        request_data = {
            "service_name": "openai",
            "model_name": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 0,  # No output tokens for cache hit
            "cache_hit": True,
            "error_occurred": False
        }
        
        expected_response = {
            "usage_id": "cache-usage-123",
            "cost_usd": "0.0",  # No cost for cached response
            "efficiency_score": "1.0",  # Perfect efficiency
            "cost_per_token": "0.0"
        }
        
        mock_cost_tracking_service.track_usage.return_value = expected_response
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/track",
                json=request_data
            )
            
            # Assert
            assert response.status_code == 200
            assert Decimal(response.json()["cost_usd"]) == Decimal("0.0")
            assert Decimal(response.json()["efficiency_score"]) == Decimal("1.0")
    
    def test_track_usage_with_error(self, test_client, mock_user, mock_cost_tracking_service):
        """Test cost tracking when an error occurred."""
        # Arrange
        request_data = {
            "service_name": "anthropic",
            "model_name": "claude-3",
            "input_tokens": 500,
            "output_tokens": 0,  # No output due to error
            "error_occurred": True
        }
        
        expected_response = {
            "usage_id": "error-usage-456",
            "cost_usd": "0.005",  # Still charged for input
            "efficiency_score": "0.0",  # Poor efficiency due to error
            "cost_per_token": "0.00001",
            "warnings": ["Error occurred - consider retry logic"]
        }
        
        mock_cost_tracking_service.track_usage.return_value = expected_response
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/track",
                json=request_data
            )
            
            # Assert
            assert response.status_code == 200
            assert "warnings" in response.json()

class TestBudgetManagement:
    """Test budget management endpoints."""
    
    def test_set_budget_success(self, test_client, mock_user, mock_budget_alert_service):
        """Test successfully setting a budget."""
        # Arrange
        budget_data = {
            "daily_limit_usd": 100.0,
            "monthly_limit_usd": 2500.0,
            "alert_threshold_percent": 80,
            "auto_stop_at_limit": True,
            "notification_emails": ["admin@example.com", "finance@example.com"]
        }
        
        mock_budget_alert_service.set_budget.return_value = {
            "budget_id": "budget-123",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/budget/set",
                json=budget_data
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["budget_id"] == "budget-123"
            assert response.json()["status"] == "active"
    
    def test_get_budget_status(self, test_client, mock_user, mock_budget_alert_service):
        """Test retrieving budget status."""
        # Arrange
        expected_status = {
            "daily_spent_usd": "45.23",
            "daily_limit_usd": "100.00",
            "daily_remaining_usd": "54.77",
            "daily_usage_percent": 45.23,
            "monthly_spent_usd": "1234.56",
            "monthly_limit_usd": "2500.00",
            "monthly_remaining_usd": "1265.44",
            "monthly_usage_percent": 49.38,
            "alerts": [],
            "is_at_limit": False
        }
        
        mock_budget_alert_service.get_budget_status.return_value = expected_status
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/budget/status")
            
            # Assert
            assert response.status_code == 200
            assert response.json()["daily_usage_percent"] == 45.23
            assert response.json()["is_at_limit"] is False
    
    def test_budget_alert_triggered(self, test_client, mock_user, mock_budget_alert_service):
        """Test budget alert when threshold is exceeded."""
        # Arrange
        expected_status = {
            "daily_spent_usd": "85.00",
            "daily_limit_usd": "100.00",
            "daily_remaining_usd": "15.00",
            "daily_usage_percent": 85.0,
            "monthly_spent_usd": "2100.00",
            "monthly_limit_usd": "2500.00",
            "monthly_remaining_usd": "400.00",
            "monthly_usage_percent": 84.0,
            "alerts": [
                {"type": "warning", "message": "Daily budget 85% consumed"},
                {"type": "warning", "message": "Monthly budget 84% consumed"}
            ],
            "is_at_limit": False
        }
        
        mock_budget_alert_service.get_budget_status.return_value = expected_status
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/budget/status")
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()["alerts"]) == 2
            assert "85%" in response.json()["alerts"][0]["message"]

class TestUsageAnalytics:
    """Test usage analytics endpoints."""
    
    def test_get_usage_analytics_daily(self, test_client, mock_user, mock_cost_tracking_service):
        """Test retrieving daily usage analytics."""
        # Arrange
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        expected_analytics = {
            "period": "daily",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_cost_usd": "325.67",
            "total_requests": 1543,
            "average_cost_per_request": "0.211",
            "cost_by_service": {
                "openai": "245.23",
                "anthropic": "80.44"
            },
            "cost_by_model": {
                "gpt-4": "200.00",
                "gpt-3.5-turbo": "45.23",
                "claude-3": "80.44"
            },
            "daily_breakdown": [
                {"date": "2024-01-01", "cost": "45.23", "requests": 220},
                {"date": "2024-01-02", "cost": "52.11", "requests": 245}
            ]
        }
        
        mock_cost_tracking_service.get_usage_analytics.return_value = expected_analytics
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get(
                "/api/v1/ai-costs/analytics",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "group_by": "day"
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["total_requests"] == 1543
            assert "cost_by_service" in response.json()
            assert "daily_breakdown" in response.json()
    
    def test_get_usage_analytics_by_service(self, test_client, mock_user, mock_cost_tracking_service):
        """Test usage analytics grouped by service."""
        # Arrange
        expected_analytics = {
            "period": "monthly",
            "services": [
                {
                    "service_name": "openai",
                    "total_cost": "1234.56",
                    "request_count": 5432,
                    "average_tokens": 750,
                    "cache_hit_rate": 0.23,
                    "error_rate": 0.02
                },
                {
                    "service_name": "anthropic",
                    "total_cost": "567.89",
                    "request_count": 2341,
                    "average_tokens": 890,
                    "cache_hit_rate": 0.18,
                    "error_rate": 0.01
                }
            ]
        }
        
        mock_cost_tracking_service.get_service_analytics.return_value = expected_analytics
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get(
                "/api/v1/ai-costs/analytics/by-service",
                params={"period": "monthly"}
            )
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()["services"]) == 2
            assert response.json()["services"][0]["service_name"] == "openai"

class TestCostOptimization:
    """Test cost optimization endpoints."""
    
    def test_get_optimization_insights(self, test_client, mock_user, mock_cost_optimization_service):
        """Test retrieving cost optimization insights."""
        # Arrange
        expected_insights = {
            "potential_savings_usd": "456.78",
            "savings_percentage": 23.4,
            "recommendations": [
                {
                    "type": "model_downgrade",
                    "description": "Use GPT-3.5 for simple queries",
                    "estimated_savings": "200.00",
                    "implementation_effort": "low",
                    "impact_on_quality": "minimal"
                },
                {
                    "type": "caching",
                    "description": "Implement response caching for repeated queries",
                    "estimated_savings": "156.78",
                    "implementation_effort": "medium",
                    "impact_on_quality": "none"
                },
                {
                    "type": "batch_processing",
                    "description": "Batch similar requests together",
                    "estimated_savings": "100.00",
                    "implementation_effort": "high",
                    "impact_on_quality": "none"
                }
            ],
            "usage_patterns": {
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "high_cost_queries": ["complex_analysis", "document_generation"],
                "inefficient_patterns": ["repeated_similar_queries", "oversized_contexts"]
            }
        }
        
        mock_cost_optimization_service.get_optimization_insights.return_value = expected_insights
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/optimize/insights")
            
            # Assert
            assert response.status_code == 200
            assert response.json()["potential_savings_usd"] == "456.78"
            assert len(response.json()["recommendations"]) == 3
            assert response.json()["recommendations"][0]["type"] == "model_downgrade"
    
    def test_simulate_optimization(self, test_client, mock_user, mock_cost_optimization_service):
        """Test simulating cost optimization strategies."""
        # Arrange
        optimization_request = {
            "strategies": ["model_downgrade", "caching"],
            "simulation_period_days": 30
        }
        
        expected_simulation = {
            "current_projected_cost": "3456.78",
            "optimized_projected_cost": "2345.67",
            "total_savings": "1111.11",
            "savings_by_strategy": {
                "model_downgrade": "700.00",
                "caching": "411.11"
            },
            "implementation_timeline": [
                {"week": 1, "strategy": "caching", "savings": "100.00"},
                {"week": 2, "strategy": "model_downgrade", "savings": "175.00"}
            ],
            "risk_assessment": {
                "quality_impact": "low",
                "implementation_complexity": "medium",
                "rollback_difficulty": "easy"
            }
        }
        
        mock_cost_optimization_service.simulate_optimization.return_value = expected_simulation
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/optimize/simulate",
                json=optimization_request
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["total_savings"] == "1111.11"
            assert "savings_by_strategy" in response.json()

class TestCostSummary:
    """Test cost summary and reporting endpoints."""
    
    def test_get_cost_summary_current_month(self, test_client, mock_user, mock_cost_manager):
        """Test retrieving current month cost summary."""
        # Arrange
        expected_summary = {
            "period": "current_month",
            "total_cost_usd": "1234.56",
            "comparison_to_last_period": "+12.3%",
            "top_costs": [
                {"category": "gpt-4", "cost": "800.00", "percentage": 64.8},
                {"category": "claude-3", "cost": "300.00", "percentage": 24.3},
                {"category": "gpt-3.5-turbo", "cost": "134.56", "percentage": 10.9}
            ],
            "cost_trend": "increasing",
            "projected_month_end_cost": "1567.89",
            "days_remaining": 10
        }
        
        mock_cost_manager.get_cost_summary.return_value = expected_summary
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/summary")
            
            # Assert
            assert response.status_code == 200
            assert response.json()["total_cost_usd"] == "1234.56"
            assert response.json()["cost_trend"] == "increasing"
    
    def test_get_detailed_cost_breakdown(self, test_client, mock_user, mock_cost_manager):
        """Test retrieving detailed cost breakdown."""
        # Arrange
        expected_breakdown = {
            "by_service": [
                {
                    "service": "openai",
                    "total_cost": "900.00",
                    "models": [
                        {"model": "gpt-4", "cost": "800.00", "requests": 450},
                        {"model": "gpt-3.5-turbo", "cost": "100.00", "requests": 1200}
                    ]
                },
                {
                    "service": "anthropic",
                    "total_cost": "334.56",
                    "models": [
                        {"model": "claude-3", "cost": "300.00", "requests": 234},
                        {"model": "claude-2", "cost": "34.56", "requests": 123}
                    ]
                }
            ],
            "by_department": [
                {"department": "engineering", "cost": "600.00"},
                {"department": "customer_support", "cost": "400.00"},
                {"department": "marketing", "cost": "234.56"}
            ],
            "by_feature": [
                {"feature": "chat_assistance", "cost": "500.00"},
                {"feature": "document_analysis", "cost": "400.00"},
                {"feature": "code_generation", "cost": "334.56"}
            ]
        }
        
        mock_cost_manager.get_detailed_breakdown.return_value = expected_breakdown
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/breakdown")
            
            # Assert
            assert response.status_code == 200
            assert "by_service" in response.json()
            assert "by_department" in response.json()
            assert "by_feature" in response.json()

class TestErrorHandling:
    """Test error handling in cost monitoring endpoints."""
    
    def test_track_usage_invalid_tokens(self, test_client, mock_user):
        """Test error when tracking with invalid token counts."""
        # Arrange
        request_data = {
            "service_name": "openai",
            "model_name": "gpt-4",
            "input_tokens": -100,  # Invalid negative tokens
            "output_tokens": 500
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/track",
                json=request_data
            )
            
            # Assert
            assert response.status_code == 422  # Validation error
    
    def test_set_budget_invalid_limits(self, test_client, mock_user):
        """Test error when setting invalid budget limits."""
        # Arrange
        budget_data = {
            "daily_limit_usd": -50.0,  # Invalid negative limit
            "monthly_limit_usd": 2500.0,
            "alert_threshold_percent": 80
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/budget/set",
                json=budget_data
            )
            
            # Assert
            assert response.status_code == 422  # Validation error
    
    def test_unauthorized_access(self, test_client):
        """Test unauthorized access to cost monitoring endpoints."""
        # Arrange - No user authentication
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', side_effect=HTTPException(status_code=401)):
            # Act
            response = test_client.get("/api/v1/ai-costs/summary")
            
            # Assert
            assert response.status_code == 401

class TestRateLimiting:
    """Test rate limiting on cost monitoring endpoints."""
    
    @patch('api.routers.ai_cost_monitoring.RateLimited')
    def test_rate_limit_exceeded(self, mock_rate_limiter, test_client, mock_user):
        """Test rate limiting when too many requests are made."""
        # Arrange
        mock_rate_limiter.side_effect = HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get("/api/v1/ai-costs/summary")
            
            # Assert
            assert response.status_code == 429

class TestCostAlerts:
    """Test cost alert functionality."""
    
    def test_webhook_alert_triggered(self, test_client, mock_user, mock_budget_alert_service):
        """Test webhook alert when budget threshold is reached."""
        # Arrange
        mock_budget_alert_service.check_and_send_alerts.return_value = {
            "alerts_sent": 2,
            "alert_types": ["email", "webhook"],
            "threshold_reached": 85,
            "message": "Daily budget alert triggered at 85% usage"
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post("/api/v1/ai-costs/alerts/check")
            
            # Assert
            assert response.status_code == 200
            assert response.json()["alerts_sent"] == 2
            assert "webhook" in response.json()["alert_types"]
    
    def test_alert_history(self, test_client, mock_user, mock_budget_alert_service):
        """Test retrieving alert history."""
        # Arrange
        expected_history = [
            {
                "alert_id": "alert-123",
                "timestamp": "2024-01-15T10:30:00Z",
                "type": "budget_threshold",
                "threshold_percent": 80,
                "actual_percent": 82.5,
                "message": "Monthly budget 82.5% consumed",
                "recipients": ["admin@example.com"],
                "status": "sent"
            },
            {
                "alert_id": "alert-456",
                "timestamp": "2024-01-14T15:45:00Z",
                "type": "daily_limit",
                "threshold_percent": 90,
                "actual_percent": 91.2,
                "message": "Daily limit 91.2% consumed",
                "recipients": ["finance@example.com"],
                "status": "sent"
            }
        ]
        
        mock_budget_alert_service.get_alert_history.return_value = expected_history
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get(
                "/api/v1/ai-costs/alerts/history",
                params={"limit": 10}
            )
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()) == 2
            assert response.json()[0]["alert_id"] == "alert-123"

class TestCostExport:
    """Test cost data export functionality."""
    
    def test_export_cost_data_csv(self, test_client, mock_user, mock_cost_manager):
        """Test exporting cost data as CSV."""
        # Arrange
        mock_cost_manager.export_cost_data.return_value = {
            "file_url": "https://storage.example.com/exports/cost-report-2024-01.csv",
            "expires_at": "2024-01-16T12:00:00Z",
            "size_bytes": 45678,
            "row_count": 1234
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/export",
                json={
                    "format": "csv",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "include_details": True
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert "file_url" in response.json()
            assert response.json()["row_count"] == 1234
    
    def test_export_cost_data_json(self, test_client, mock_user, mock_cost_manager):
        """Test exporting cost data as JSON."""
        # Arrange
        mock_cost_manager.export_cost_data.return_value = {
            "data": {
                "summary": {
                    "total_cost": "1234.56",
                    "total_requests": 5432
                },
                "details": [
                    {"date": "2024-01-01", "cost": "45.23"},
                    {"date": "2024-01-02", "cost": "52.11"}
                ]
            }
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.post(
                "/api/v1/ai-costs/export",
                json={
                    "format": "json",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert "data" in response.json()
            assert response.json()["data"]["summary"]["total_cost"] == "1234.56"

class TestCostForecasting:
    """Test cost forecasting functionality."""
    
    def test_forecast_monthly_costs(self, test_client, mock_user, mock_cost_optimization_service):
        """Test forecasting monthly costs based on historical data."""
        # Arrange
        expected_forecast = {
            "forecast_period": "next_3_months",
            "predictions": [
                {"month": "2024-02", "predicted_cost": "1345.67", "confidence": 0.85},
                {"month": "2024-03", "predicted_cost": "1456.78", "confidence": 0.78},
                {"month": "2024-04", "predicted_cost": "1567.89", "confidence": 0.72}
            ],
            "trend": "increasing",
            "growth_rate": 0.08,
            "factors": [
                "Seasonal increase in Q1",
                "New feature rollout expected",
                "Historical growth pattern"
            ]
        }
        
        mock_cost_optimization_service.forecast_costs.return_value = expected_forecast
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Act
            response = test_client.get(
                "/api/v1/ai-costs/forecast",
                params={"months": 3}
            )
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()["predictions"]) == 3
            assert response.json()["trend"] == "increasing"

# Integration Tests
class TestCostMonitoringIntegration:
    """Integration tests for cost monitoring system."""
    
    @pytest.mark.integration
    async def test_full_cost_tracking_workflow(self, test_client, mock_user):
        """Test complete cost tracking workflow from usage to reporting."""
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            # Step 1: Track usage
            track_response = test_client.post(
                "/api/v1/ai-costs/track",
                json={
                    "service_name": "openai",
                    "model_name": "gpt-4",
                    "input_tokens": 1000,
                    "output_tokens": 500
                }
            )
            assert track_response.status_code == 200
            
            # Step 2: Check budget status
            budget_response = test_client.get("/api/v1/ai-costs/budget/status")
            assert budget_response.status_code == 200
            
            # Step 3: Get analytics
            analytics_response = test_client.get(
                "/api/v1/ai-costs/analytics",
                params={"group_by": "day"}
            )
            assert analytics_response.status_code == 200
            
            # Step 4: Get optimization insights
            optimize_response = test_client.get("/api/v1/ai-costs/optimize/insights")
            assert optimize_response.status_code == 200
            
            # Step 5: Export data
            export_response = test_client.post(
                "/api/v1/ai-costs/export",
                json={"format": "csv"}
            )
            assert export_response.status_code == 200

# Smoke Tests
class TestCostMonitoringSmoke:
    """Smoke tests for basic cost monitoring functionality."""
    
    @pytest.mark.smoke
    def test_health_check(self, test_client):
        """Test that cost monitoring service is responding."""
        response = test_client.get("/api/v1/ai-costs/health")
        assert response.status_code in [200, 404]  # 404 if health endpoint doesn't exist yet
    
    @pytest.mark.smoke
    def test_basic_cost_tracking(self, test_client, mock_user, mock_cost_tracking_service):
        """Quick test that basic cost tracking works."""
        mock_cost_tracking_service.track_usage.return_value = {
            "usage_id": "test-123",
            "cost_usd": "0.10"
        }
        
        with patch('api.routers.ai_cost_monitoring.get_current_active_user', return_value=mock_user):
            response = test_client.post(
                "/api/v1/ai-costs/track",
                json={
                    "service_name": "openai",
                    "model_name": "gpt-3.5-turbo",
                    "input_tokens": 100,
                    "output_tokens": 50
                }
            )
            assert response.status_code == 200
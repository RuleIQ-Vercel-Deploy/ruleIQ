"""
Webhook Handler Router

Handles incoming webhooks from external services with signature verification
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from database.db_setup import get_db
from services.webhook_verification import WebhookVerificationService, verify_webhook_signature
from database.redis_client import get_redis_client
from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],
    responses={404: {"description": "Not found"}},
)


# Webhook event handlers
async def handle_stripe_event(event_type: str, data: dict, db: AsyncSession):
    """Handle Stripe webhook events."""
    logger.info(f"Processing Stripe event: {event_type}")
    
    if event_type == "payment_intent.succeeded":
        # Handle successful payment
        payment_intent = data.get("object", {})
        customer_id = payment_intent.get("customer")
        amount = payment_intent.get("amount", 0) / 100  # Convert from cents
        
        logger.info(f"Payment succeeded for customer {customer_id}: ${amount}")
        # TODO: Update user subscription status in database
        
    elif event_type == "customer.subscription.created":
        # Handle new subscription
        subscription = data.get("object", {})
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        
        logger.info(f"Subscription created for customer {customer_id}: {status}")
        # TODO: Create subscription record in database
        
    elif event_type == "customer.subscription.deleted":
        # Handle subscription cancellation
        subscription = data.get("object", {})
        customer_id = subscription.get("customer")
        
        logger.info(f"Subscription cancelled for customer {customer_id}")
        # TODO: Update subscription status in database
        
    elif event_type == "invoice.payment_failed":
        # Handle failed payment
        invoice = data.get("object", {})
        customer_id = invoice.get("customer")
        
        logger.warning(f"Payment failed for customer {customer_id}")
        # TODO: Send notification to customer
        
    else:
        logger.info(f"Unhandled Stripe event type: {event_type}")


async def handle_github_event(event_type: str, data: dict, db: AsyncSession):
    """Handle GitHub webhook events."""
    logger.info(f"Processing GitHub event: {event_type}")
    
    if event_type == "push":
        # Handle code push
        repository = data.get("repository", {}).get("full_name")
        pusher = data.get("pusher", {}).get("name")
        
        logger.info(f"Code pushed to {repository} by {pusher}")
        # TODO: Trigger CI/CD or notifications
        
    elif event_type == "pull_request":
        # Handle pull request events
        action = data.get("action")
        pr_number = data.get("pull_request", {}).get("number")
        
        logger.info(f"Pull request #{pr_number} {action}")
        # TODO: Trigger code review or checks
        
    elif event_type == "issues":
        # Handle issue events
        action = data.get("action")
        issue_number = data.get("issue", {}).get("number")
        
        logger.info(f"Issue #{issue_number} {action}")
        # TODO: Update issue tracking
        
    else:
        logger.info(f"Unhandled GitHub event type: {event_type}")


async def handle_sendgrid_event(events: list, db: AsyncSession):
    """Handle SendGrid webhook events."""
    for event in events:
        event_type = event.get("event")
        email = event.get("email")
        
        logger.info(f"Processing SendGrid event: {event_type} for {email}")
        
        if event_type == "delivered":
            # Email was delivered
            logger.info(f"Email delivered to {email}")
            # TODO: Update email status in database
            
        elif event_type == "bounce":
            # Email bounced
            reason = event.get("reason", "Unknown")
            logger.warning(f"Email bounced for {email}: {reason}")
            # TODO: Mark email as invalid
            
        elif event_type == "spam_report":
            # User marked as spam
            logger.warning(f"Email marked as spam by {email}")
            # TODO: Update user preferences
            
        elif event_type == "unsubscribe":
            # User unsubscribed
            logger.info(f"User unsubscribed: {email}")
            # TODO: Update subscription preferences


# Webhook endpoints

@router.post("/stripe", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Handle Stripe webhooks with signature verification.
    
    Configure webhook endpoint in Stripe dashboard:
    https://dashboard.stripe.com/webhooks
    """
    try:
        # Get raw body for signature verification
        payload = await request.body()
        
        # Verify webhook signature
        service = WebhookVerificationService(redis_client)
        is_valid, error = await service.verify_webhook(
            request=request,
            provider="stripe",
            payload=payload
        )
        
        if not is_valid:
            logger.warning(f"Invalid Stripe webhook signature: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Extract event type and data
        event_type = data.get("type")
        event_data = data.get("data", {})
        
        # Process event in background
        background_tasks.add_task(
            handle_stripe_event,
            event_type,
            event_data,
            db
        )
        
        # Log successful webhook
        await service.log_webhook_attempt(
            provider="stripe",
            endpoint="/webhooks/stripe",
            is_valid=True,
            metadata={"event_type": event_type}
        )
        
        # Return success immediately (Stripe expects 200 OK)
        return {"received": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.post("/github", include_in_schema=False)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Handle GitHub webhooks with signature verification.
    
    Configure webhook in repository settings:
    https://github.com/[owner]/[repo]/settings/hooks
    """
    try:
        # Get raw body for signature verification
        payload = await request.body()
        
        # Verify webhook signature
        service = WebhookVerificationService(redis_client)
        is_valid, error = await service.verify_webhook(
            request=request,
            provider="github",
            payload=payload
        )
        
        if not is_valid:
            logger.warning(f"Invalid GitHub webhook signature: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        
        # Process event in background
        background_tasks.add_task(
            handle_github_event,
            event_type,
            data,
            db
        )
        
        # Log successful webhook
        await service.log_webhook_attempt(
            provider="github",
            endpoint="/webhooks/github",
            is_valid=True,
            metadata={"event_type": event_type}
        )
        
        return {"received": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.post("/sendgrid", include_in_schema=False)
async def sendgrid_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Handle SendGrid email event webhooks.
    
    Configure webhook in SendGrid settings:
    https://app.sendgrid.com/settings/mail_settings/event_notification
    """
    try:
        # Get raw body for signature verification
        payload = await request.body()
        
        # Verify webhook signature
        service = WebhookVerificationService(redis_client)
        is_valid, error = await service.verify_webhook(
            request=request,
            provider="sendgrid",
            payload=payload
        )
        
        if not is_valid:
            logger.warning(f"Invalid SendGrid webhook signature: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the payload (SendGrid sends array of events)
        try:
            events = json.loads(payload)
            if not isinstance(events, list):
                events = [events]
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Process events in background
        background_tasks.add_task(
            handle_sendgrid_event,
            events,
            db
        )
        
        # Log successful webhook
        await service.log_webhook_attempt(
            provider="sendgrid",
            endpoint="/webhooks/sendgrid",
            is_valid=True,
            metadata={"event_count": len(events)}
        )
        
        return {"received": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SendGrid webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.post("/custom/{webhook_id}", include_in_schema=False)
async def custom_webhook(
    webhook_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Handle custom webhooks with signature verification.
    
    Use this for any service that doesn't have a dedicated endpoint.
    Requires webhook configuration with signature secret.
    """
    try:
        # Get raw body for signature verification
        payload = await request.body()
        
        # Get webhook secret from configuration
        # TODO: Load webhook configuration from database based on webhook_id
        webhook_secret = None  # Load from database
        
        # Verify webhook signature
        service = WebhookVerificationService(redis_client)
        is_valid, error = await service.verify_webhook(
            request=request,
            provider="custom",
            secret=webhook_secret,
            payload=payload
        )
        
        if not is_valid:
            logger.warning(f"Invalid custom webhook signature for {webhook_id}: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # TODO: Process custom webhook based on webhook_id configuration
        logger.info(f"Received custom webhook {webhook_id}: {data}")
        
        # Log successful webhook
        await service.log_webhook_attempt(
            provider="custom",
            endpoint=f"/webhooks/custom/{webhook_id}",
            is_valid=True,
            metadata={"webhook_id": webhook_id}
        )
        
        return {"received": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom webhook error for {webhook_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.get("/test/generate-signature")
async def test_generate_signature(
    payload: str = '{"test": "data"}',
    secret: str = "test_secret",
    provider: str = "custom"
):
    """
    Test endpoint to generate webhook signatures for testing.
    
    Only available in development/test environments.
    """
    import os
    if os.getenv("ENVIRONMENT", "production").lower() not in ["development", "test", "local"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in development"
        )
    
    service = WebhookVerificationService()
    signature = await service.generate_webhook_signature(
        payload=payload,
        secret=secret,
        provider=provider
    )
    
    return {
        "provider": provider,
        "signature": signature,
        "header_name": WebhookVerificationService.PROVIDERS[provider]["header"],
        "payload": payload
    }
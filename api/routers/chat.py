"""
FastAPI router for chat functionality with the AI assistant.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from uuid import UUID, uuid4
import json
import logging

from database.db_setup import get_db
from database.user import User
from database.business_profile import BusinessProfile
from database.chat_conversation import ChatConversation, ConversationStatus
from database.chat_message import ChatMessage
from api.dependencies.auth import get_current_user
from api.schemas.chat import (
    SendMessageRequest, MessageResponse, ConversationResponse,
    CreateConversationRequest, ConversationListResponse, ConversationSummary,
    EvidenceRecommendationRequest, EvidenceRecommendationResponse,
    ComplianceAnalysisRequest, ComplianceAnalysisResponse
)
from services.ai import ComplianceAssistant

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat Assistant"])

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat conversation."""
    try:
        # Get the user's business profile
        business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_id == str(current_user.id)
        ).first()
        
        if not business_profile:
            raise HTTPException(
                status_code=400, 
                detail="No business profile found. Please complete your profile setup first."
            )
        
        # Create new conversation
        conversation = ChatConversation(
            user_id=current_user.id,
            business_profile_id=business_profile.id,
            title=request.title or f"Chat {db.query(ChatConversation).filter(ChatConversation.user_id == current_user.id).count() + 1}",
            status=ConversationStatus.ACTIVE
        )
        
        db.add(conversation)
        db.flush()  # Get the conversation ID
        
        messages = []
        
        # If there's an initial message, process it
        if request.initial_message:
            assistant = ComplianceAssistant(db)
            
            # Add user message
            user_message = ChatMessage(
                conversation_id=conversation.id,
                role="user",
                content=request.initial_message,
                sequence_number=1
            )
            db.add(user_message)
            
            # Generate assistant response
            response_text, metadata = await assistant.process_message(
                conversation_id=conversation.id,
                user_id=current_user.id,
                message=request.initial_message,
                business_profile_id=business_profile.id
            )
            
            # Add assistant message
            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=response_text,
                metadata=metadata,
                sequence_number=2
            )
            db.add(assistant_message)
            
            messages = [user_message, assistant_message]
        
        db.commit()
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            status=conversation.status.value,
            messages=[MessageResponse.from_orm(msg) for msg in messages],
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's chat conversations."""
    try:
        # Get total count
        total = db.query(ChatConversation).filter(
            ChatConversation.user_id == current_user.id,
            ChatConversation.status != ConversationStatus.DELETED
        ).count()
        
        # Get conversations with pagination
        conversations = db.query(ChatConversation).filter(
            ChatConversation.user_id == current_user.id,
            ChatConversation.status != ConversationStatus.DELETED
        ).order_by(desc(ChatConversation.updated_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        # Get message counts and last message times
        conversation_summaries = []
        for conv in conversations:
            message_count = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conv.id
            ).count()
            
            last_message = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conv.id
            ).order_by(desc(ChatMessage.created_at)).first()
            
            conversation_summaries.append(ConversationSummary(
                id=conv.id,
                title=conv.title,
                status=conv.status.value,
                message_count=message_count,
                last_message_at=last_message.created_at if last_message else None,
                created_at=conv.created_at
            ))
        
        return ConversationListResponse(
            conversations=conversation_summaries,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with all messages."""
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.sequence_number).all()
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            status=conversation.status.value,
            messages=[MessageResponse.from_orm(msg) for msg in messages],
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation")

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a conversation."""
    try:
        # Verify conversation exists and belongs to user
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id,
            ChatConversation.status == ConversationStatus.ACTIVE
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or inactive")
        
        # Get business profile
        business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_id == str(current_user.id)
        ).first()
        
        if not business_profile:
            raise HTTPException(status_code=400, detail="Business profile not found")
        
        # Get next sequence number
        last_message = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(desc(ChatMessage.sequence_number)).first()
        
        next_sequence = (last_message.sequence_number + 1) if last_message else 1
        
        # Add user message
        user_message = ChatMessage(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            sequence_number=next_sequence
        )
        db.add(user_message)
        db.flush()
        
        # Generate assistant response
        assistant = ComplianceAssistant(db)
        response_text, metadata = await assistant.process_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message=request.message,
            business_profile_id=business_profile.id
        )
        
        # Add assistant message
        assistant_message = ChatMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata=metadata,
            sequence_number=next_sequence + 1
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = func.now()
        
        db.commit()
        
        return MessageResponse.from_orm(assistant_message)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete (archive) a conversation."""
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.status = ConversationStatus.DELETED
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

@router.post("/evidence-recommendations", response_model=List[EvidenceRecommendationResponse])
async def get_evidence_recommendations(
    request: EvidenceRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered evidence collection recommendations."""
    try:
        business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_id == str(current_user.id)
        ).first()
        
        if not business_profile:
            raise HTTPException(status_code=400, detail="Business profile not found")
        
        assistant = ComplianceAssistant(db)
        recommendations = await assistant.get_evidence_recommendations(
            business_profile_id=business_profile.id,
            framework=request.framework
        )
        
        return [EvidenceRecommendationResponse(**rec) for rec in recommendations]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evidence recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.post("/compliance-analysis", response_model=ComplianceAnalysisResponse)
async def analyze_compliance_gap(
    request: ComplianceAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze compliance gaps for a specific framework."""
    try:
        business_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_id == str(current_user.id)
        ).first()
        
        if not business_profile:
            raise HTTPException(status_code=400, detail="Business profile not found")
        
        assistant = ComplianceAssistant(db)
        analysis = await assistant.analyze_evidence_gap(
            business_profile_id=business_profile.id,
            framework=request.framework
        )
        
        return ComplianceAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing compliance gap: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze compliance gap")
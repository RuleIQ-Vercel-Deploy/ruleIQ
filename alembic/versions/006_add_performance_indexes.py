"""Add performance indexes for evidence and business profile queries

Revision ID: 006
Revises: 005
Create Date: 2025-06-21

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add critical performance indexes for evidence and business profile queries."""
    
    # Evidence Items Performance Indexes
    # Primary filtering indexes
    op.create_index('idx_evidence_items_user_id', 'evidence_items', ['user_id'])
    op.create_index('idx_evidence_items_framework_id', 'evidence_items', ['framework_id'])
    op.create_index('idx_evidence_items_business_profile_id', 'evidence_items', ['business_profile_id'])
    
    # Status and type filtering indexes
    op.create_index('idx_evidence_items_status', 'evidence_items', ['status'])
    op.create_index('idx_evidence_items_evidence_type', 'evidence_items', ['evidence_type'])
    
    # Composite indexes for common query patterns
    # User + Framework filtering (most common pattern)
    op.create_index('idx_evidence_items_user_framework', 'evidence_items', ['user_id', 'framework_id'])
    
    # User + Status filtering (for dashboards)
    op.create_index('idx_evidence_items_user_status', 'evidence_items', ['user_id', 'status'])
    
    # User + Type filtering
    op.create_index('idx_evidence_items_user_type', 'evidence_items', ['user_id', 'evidence_type'])
    
    # Framework + Status filtering
    op.create_index('idx_evidence_items_framework_status', 'evidence_items', ['framework_id', 'status'])
    
    # Timestamp indexes for sorting and pagination
    op.create_index('idx_evidence_items_created_at', 'evidence_items', ['created_at'])
    op.create_index('idx_evidence_items_updated_at', 'evidence_items', ['updated_at'])
    
    # Composite index for pagination with user filtering
    op.create_index('idx_evidence_items_user_created', 'evidence_items', ['user_id', 'created_at'])
    op.create_index('idx_evidence_items_user_updated', 'evidence_items', ['user_id', 'updated_at'])
    
    # Business Profiles Performance Indexes
    # Primary user lookup (should already exist due to unique constraint, but ensure it's optimized)
    op.create_index('idx_business_profiles_user_id', 'business_profiles', ['user_id'])
    
    # Users table indexes
    # Email lookup (should already exist due to unique constraint)
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Compliance Frameworks indexes
    op.create_index('idx_compliance_frameworks_name', 'compliance_frameworks', ['name'])
    op.create_index('idx_compliance_frameworks_is_active', 'compliance_frameworks', ['is_active'])
    
    # Chat-related indexes for performance
    op.create_index('idx_chat_conversations_user_id', 'chat_conversations', ['user_id'])
    op.create_index('idx_chat_conversations_business_profile_id', 'chat_conversations', ['business_profile_id'])
    op.create_index('idx_chat_conversations_created_at', 'chat_conversations', ['created_at'])
    
    op.create_index('idx_chat_messages_conversation_id', 'chat_messages', ['conversation_id'])
    op.create_index('idx_chat_messages_sequence_number', 'chat_messages', ['sequence_number'])
    op.create_index('idx_chat_messages_conversation_sequence', 'chat_messages', ['conversation_id', 'sequence_number'])


def downgrade():
    """Remove performance indexes."""
    
    # Evidence Items indexes
    op.drop_index('idx_evidence_items_user_id', 'evidence_items')
    op.drop_index('idx_evidence_items_framework_id', 'evidence_items')
    op.drop_index('idx_evidence_items_business_profile_id', 'evidence_items')
    op.drop_index('idx_evidence_items_status', 'evidence_items')
    op.drop_index('idx_evidence_items_evidence_type', 'evidence_items')
    
    # Composite indexes
    op.drop_index('idx_evidence_items_user_framework', 'evidence_items')
    op.drop_index('idx_evidence_items_user_status', 'evidence_items')
    op.drop_index('idx_evidence_items_user_type', 'evidence_items')
    op.drop_index('idx_evidence_items_framework_status', 'evidence_items')
    
    # Timestamp indexes
    op.drop_index('idx_evidence_items_created_at', 'evidence_items')
    op.drop_index('idx_evidence_items_updated_at', 'evidence_items')
    op.drop_index('idx_evidence_items_user_created', 'evidence_items')
    op.drop_index('idx_evidence_items_user_updated', 'evidence_items')
    
    # Business Profiles indexes
    op.drop_index('idx_business_profiles_user_id', 'business_profiles')
    
    # Users indexes
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_is_active', 'users')
    
    # Compliance Frameworks indexes
    op.drop_index('idx_compliance_frameworks_name', 'compliance_frameworks')
    op.drop_index('idx_compliance_frameworks_is_active', 'compliance_frameworks')
    
    # Chat indexes
    op.drop_index('idx_chat_conversations_user_id', 'chat_conversations')
    op.drop_index('idx_chat_conversations_business_profile_id', 'chat_conversations')
    op.drop_index('idx_chat_conversations_created_at', 'chat_conversations')
    op.drop_index('idx_chat_messages_conversation_id', 'chat_messages')
    op.drop_index('idx_chat_messages_sequence_number', 'chat_messages')
    op.drop_index('idx_chat_messages_conversation_sequence', 'chat_messages')

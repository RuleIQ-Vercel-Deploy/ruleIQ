"""
Audit Log Export API for SMB compliance tracking.
Provides audit trail exports for compliance and security auditing.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import csv
import json
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from api.dependencies.auth import get_current_active_user
from api.dependencies.rbac_auth import require_permission
from database.db_setup import get_async_db
from database.user import User
from config.logging_config import get_logger

# Constants
DEFAULT_LIMIT = 100

logger = get_logger(__name__)
router = APIRouter()

@router.get('/audit/export', summary='Export Audit Logs',
    description='Export filtered audit logs in various formats')
async def export_audit_logs(format: str=Query('csv', regex='^(csv|json|xlsx)$'),
    start_date: Optional[datetime]=None, end_date: Optional[datetime]=None,
    user_id: Optional[str]=None, action_type: Optional[str]=None,
    resource_type: Optional[str]=None, include_system: bool=Query(False),
    current_user: User=Depends(get_current_active_user),
    db: AsyncSession=Depends(get_async_db)) -> StreamingResponse:
    """Export audit logs with filtering and format options."""
    try:
        permission = await require_permission('audit:export')
        await permission(current_user, db)
        query = text("""
            SELECT
                audit_id,
                timestamp,
                user_id,
                user_email,
                action,
                resource_type,
                resource_id,
                details,
                ip_address,
                user_agent,
                status,
                error_message
            FROM audit_logs
            WHERE 1=1
        """)
        params = {}
        if start_date:
            query = text(str(query) + ' AND timestamp >= :start_date')
            params['start_date'] = start_date
        if end_date:
            query = text(str(query) + ' AND timestamp <= :end_date')
            params['end_date'] = end_date
        if user_id:
            query = text(str(query) + ' AND user_id = :user_id')
            params['user_id'] = user_id
        if action_type:
            query = text(str(query) + ' AND action = :action_type')
            params['action_type'] = action_type
        if resource_type:
            query = text(str(query) + ' AND resource_type = :resource_type')
            params['resource_type'] = resource_type
        if not include_system:
            query = text(str(query) + ' AND user_id != :system_user')
            params['system_user'] = 'system'
        query = text(str(query) + ' ORDER BY timestamp DESC LIMIT :limit')
        params['limit'] = 10000
        result = await db.execute(query, params)
        audit_logs = result.fetchall()
        if format == 'json':
            logs_dict = [dict(row._mapping) for row in audit_logs]
            for log in logs_dict:
                if isinstance(log.get('timestamp'), datetime):
                    log['timestamp'] = log['timestamp'].isoformat()
            output = BytesIO()
            output.write(json.dumps(logs_dict, indent=2, default=str).encode())
            output.seek(0)
            return StreamingResponse(output, media_type='application/json',
                headers={'Content-Disposition':
                f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'})
        elif format == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Audit ID', 'Timestamp', 'User ID', 'User Email',
                'Action', 'Resource Type', 'Resource ID', 'Details',
                'IP Address', 'User Agent', 'Status', 'Error Message'])
            for row in audit_logs:
                writer.writerow([row.audit_id, row.timestamp, row.user_id,
                    row.user_email, row.action, row.resource_type, row.
                    resource_id, json.dumps(row.details) if row.details else
                    '', row.ip_address, row.user_agent, row.status, row.
                    error_message])
            output.seek(0)
            return StreamingResponse(output, media_type='text/csv',
                headers={'Content-Disposition':
                f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'})
        elif format == 'xlsx':
            df = pd.DataFrame([dict(row._mapping) for row in audit_logs])
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['details'] = df['details'].apply(lambda x: json.dumps(x
                    ) if x else '')
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Audit Logs', index=False)
            output.seek(0)
            return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition':
                f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'})
    except Exception as e:
        logger.error(f'Error exporting audit logs: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to export audit logs')

@router.get('/audit/summary', summary='Get Audit Summary',
    description='Get summary statistics of audit logs')
async def get_audit_summary(start_date: Optional[datetime]=None, end_date:
    Optional[datetime]=None, current_user: User=Depends(
    get_current_active_user), db: AsyncSession=Depends(get_async_db)
    ) -> Dict[str, Any]:
    """Get audit log summary with statistics."""
    try:
        permission = await require_permission('audit:view')
        await permission(current_user, db)
        params = {}
        base_query = 'FROM audit_logs WHERE 1=1'
        if start_date:
            base_query += ' AND timestamp >= :start_date'
            params['start_date'] = start_date
        if end_date:
            base_query += ' AND timestamp <= :end_date'
            params['end_date'] = end_date
        total_query = text(f'SELECT COUNT(*) as total {base_query}')
        total_result = await db.execute(total_query, params)
        total_logs = total_result.fetchone().total
        by_action_query = text(
            f'SELECT action, COUNT(*) as count {base_query} GROUP BY action')
        by_action_result = await db.execute(by_action_query, params)
        actions = {row.action: row.count for row in by_action_result}
        by_resource_query = text(
            f'SELECT resource_type, COUNT(*) as count {base_query} GROUP BY resource_type')
        by_resource_result = await db.execute(by_resource_query, params)
        resources = {row.resource_type: row.count for row in by_resource_result}
        by_user_query = text(
            f"""
            SELECT user_email, COUNT(*) as count 
            {base_query} 
            AND user_id != 'system'
            GROUP BY user_email 
            ORDER BY count DESC 
            LIMIT 10
        """)
        by_user_result = await db.execute(by_user_query, params)
        top_users = [{
            'user': row.user_email,
            'actions': row.count
        } for row in by_user_result]
        errors_query = text(
            f"SELECT COUNT(*) as errors {base_query} AND status = 'error'")
        errors_result = await db.execute(errors_query, params)
        error_count = errors_result.fetchone().errors
        return {'summary': {'total_logs': total_logs, 'error_count':
            error_count, 'error_rate': (error_count / total_logs * 100 if
            total_logs > 0 else 0)}, 'by_action': actions, 'by_resource':
            resources, 'top_users': top_users, 'period': {'start':
            start_date.isoformat() if start_date else 'all_time', 'end':
            end_date.isoformat() if end_date else 'current'}}
    except Exception as e:
        logger.error(f'Error getting audit summary: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to get audit summary')
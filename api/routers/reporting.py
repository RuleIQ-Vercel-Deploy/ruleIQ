"""
Reporting API endpoints for ComplianceGPT
"""

import io
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_active_user
from database.user import User
from database.db_setup import get_db
from database.business_profile import BusinessProfile
from services.reporting.pdf_generator import PDFGenerator
from services.reporting.report_generator import ReportGenerator
from services.reporting.report_scheduler import ReportScheduler
from services.reporting.template_manager import TemplateManager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class ReportRequest(BaseModel):
    """Request model for report generation"""

    business_profile_id: UUID
    report_type: str = Field(..., description="Type of report to generate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Report parameters")
    output_format: str = Field(default="pdf", description="Output format (pdf, json)")
    template_customizations: Dict[str, Any] = Field(
        default_factory=dict, description="Template customizations"
    )


class ReportResponse(BaseModel):
    """Response model for report generation"""

    report_id: str
    report_type: str
    generated_at: str
    file_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TemplateListResponse(BaseModel):
    """Response model for template listing"""

    templates: List[Dict[str, str]]


class ReportStatus(BaseModel):
    """Report generation status"""

    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


# Additional models for scheduling
class CreateScheduleRequest(BaseModel):
    """Request model for creating a scheduled report"""

    business_profile_id: UUID
    report_type: str
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    recipients: List[str] = Field(..., min_items=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    schedule_config: Dict[str, Any] = Field(default_factory=dict)


class ScheduleResponse(BaseModel):
    """Response model for report schedules"""

    schedule_id: str
    business_profile_id: UUID
    report_type: str
    frequency: str
    recipients: List[str]
    parameters: Dict[str, Any]
    active: bool
    created_at: str


class UpdateScheduleRequest(BaseModel):
    """Request model for updating a schedule"""

    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    recipients: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    schedule_config: Optional[Dict[str, Any]] = None


@router.get("/templates", response_model=TemplateListResponse)
async def list_report_templates(current_user: User = Depends(get_current_active_user)):
    """List available report templates"""
    template_manager = TemplateManager()
    templates = template_manager.list_templates()

    return TemplateListResponse(templates=templates)


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a compliance report"""
    try:
        # Initialize report generator
        report_generator = ReportGenerator(db)

        # Generate report data
        report_data = await report_generator.generate_report(
            user=current_user,
            business_profile_id=request.business_profile_id,
            report_type=request.report_type,
            parameters=request.parameters,
        )

        # Generate unique report ID
        import uuid
        from datetime import datetime

        report_id = str(uuid.uuid4())

        response_data = {
            "report_id": report_id,
            "report_type": request.report_type,
            "generated_at": report_data.get("generated_at", datetime.utcnow().isoformat()),
        }

        if request.output_format.lower() == "pdf":
            # Generate PDF
            pdf_generator = PDFGenerator()
            await pdf_generator.generate_pdf(report_data)

            # In a production system, you would save this to cloud storage
            # For now, we'll return a placeholder URL
            response_data["file_url"] = f"/api/reports/{report_id}/download"

            # Store PDF temporarily (in production, use cloud storage)
            # This is a simplified implementation

        else:
            # Return JSON data
            response_data["data"] = report_data

        return ReportResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e!s}")


@router.post("/generate/pdf")
async def generate_pdf_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a PDF report and return it directly"""
    try:
        # Initialize report generator
        report_generator = ReportGenerator(db)

        # Generate report data
        report_data = await report_generator.generate_report(
            user=current_user,
            business_profile_id=request.business_profile_id,
            report_type=request.report_type,
            parameters=request.parameters,
        )

        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = await pdf_generator.generate_pdf(report_data)

        # Create response with PDF
        io.BytesIO(pdf_bytes)

        # Set appropriate headers
        headers = {
            "Content-Disposition": f'attachment; filename="{request.report_type}_report.pdf"',
            "Content-Type": "application/pdf",
        }

        return StreamingResponse(
            io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e!s}")


@router.get("/preview/{report_type}")
async def preview_report_structure(
    report_type: str, current_user: User = Depends(get_current_active_user)
):
    """Preview the structure of a report type"""
    template_manager = TemplateManager()
    template = template_manager.get_template(report_type)

    if not template:
        raise HTTPException(status_code=404, detail=f"Report type '{report_type}' not found")

    return {
        "report_type": report_type,
        "template": template,
        "supported_parameters": _get_supported_parameters(report_type),
    }


@router.post("/customize-template/{template_name}")
async def customize_report_template(
    template_name: str,
    customizations: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
):
    """Customize a report template"""
    try:
        template_manager = TemplateManager()
        customized_template = template_manager.customize_template(template_name, customizations)

        return {
            "template_name": template_name,
            "customized_template": customized_template,
            "message": "Template customized successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template customization failed: {e!s}")


def _get_supported_parameters(report_type: str) -> Dict[str, Any]:
    """Get supported parameters for a report type"""
    common_params = {
        "frameworks": {
            "type": "array",
            "description": "List of compliance frameworks to include",
            "items": {"type": "string"},
            "example": ["ISO27001", "SOC2", "GDPR"],
        },
        "period_days": {
            "type": "integer",
            "description": "Number of days to analyze for trends",
            "default": 30,
            "minimum": 1,
            "maximum": 365,
        },
    }

    type_specific_params = {
        "executive_summary": {
            **common_params,
            "include_charts": {
                "type": "boolean",
                "description": "Include charts and visualizations",
                "default": True,
            },
        },
        "gap_analysis": {
            **common_params,
            "severity_filter": {
                "type": "string",
                "description": "Filter gaps by severity level",
                "enum": ["critical", "high", "medium", "low"],
                "required": False,
            },
            "include_remediation_plan": {
                "type": "boolean",
                "description": "Include detailed remediation plan",
                "default": True,
            },
        },
        "evidence_report": {
            **common_params,
            "status_filter": {
                "type": "string",
                "description": "Filter evidence by collection status",
                "enum": ["not_started", "in_progress", "collected", "approved"],
                "required": False,
            },
            "show_automation_only": {
                "type": "boolean",
                "description": "Show only evidence items with automation opportunities",
                "default": False,
            },
        },
        "audit_readiness": {
            **common_params,
            "target_audit_date": {
                "type": "string",
                "format": "date",
                "description": "Target date for audit preparation",
                "required": False,
            },
            "include_checklist": {
                "type": "boolean",
                "description": "Include pre-audit checklist",
                "default": True,
            },
        },
    }

    return type_specific_params.get(report_type, common_params)


# Scheduling endpoints
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    request: CreateScheduleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new scheduled report"""
    try:
        # Verify access to business profile
        profile = (
            db.query(BusinessProfile)
            .filter(
                BusinessProfile.id == str(request.business_profile_id),
                BusinessProfile.user_id == str(str(current_user.id)),
            )
            .first()
        )

        if not profile:
            raise HTTPException(status_code=404, detail="Business profile not found")

        # Create the schedule
        scheduler = ReportScheduler(db)
        schedule_id = scheduler.create_schedule(
            user_id=str(str(current_user.id)),
            business_profile_id=str(request.business_profile_id),
            report_type=request.report_type,
            frequency=request.frequency,
            parameters=request.parameters,
            recipients=request.recipients,
            schedule_config=request.schedule_config,
        )

        # Get the created schedule
        schedule = scheduler.get_schedule(schedule_id)

        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            business_profile_id=UUID(schedule.business_profile_id),
            report_type=schedule.report_type,
            frequency=schedule.frequency,
            recipients=schedule.recipients,
            parameters=schedule.parameters,
            active=schedule.active,
            created_at=schedule.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.get("/schedules")
async def list_schedules(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """List all report schedules for the current user"""
    try:
        scheduler = ReportScheduler(db)
        schedules = scheduler.list_user_schedules(str(str(current_user.id)))

        schedule_responses = [
            ScheduleResponse(
                schedule_id=schedule.schedule_id,
                business_profile_id=UUID(schedule.business_profile_id),
                report_type=schedule.report_type,
                frequency=schedule.frequency,
                recipients=schedule.recipients,
                parameters=schedule.parameters,
                active=schedule.active,
                created_at=schedule.created_at.isoformat(),
            )
            for schedule in schedules
        ]

        return {"schedules": schedule_responses, "total": len(schedule_responses)}

    except Exception as e:
        logger.error(f"Failed to list schedules: {e}")
        raise HTTPException(status_code=500, detail="Failed to list schedules")


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a report schedule"""
    try:
        scheduler = ReportScheduler(db)
        schedule = scheduler.get_schedule(schedule_id)

        if not schedule or schedule.user_id != str(str(current_user.id)):
            raise HTTPException(status_code=404, detail="Schedule not found")

        success = scheduler.delete_schedule(schedule_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete schedule")

        return {"message": "Schedule deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete schedule")


@router.post("/schedules/{schedule_id}/execute")
async def execute_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Manually execute a scheduled report"""
    try:
        scheduler = ReportScheduler(db)
        schedule = scheduler.get_schedule(schedule_id)

        if not schedule or schedule.user_id != str(str(current_user.id)):
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Execute the schedule
        result = scheduler.execute_schedule(schedule_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Execution failed"))

        return {
            "status": result["status"],
            "task_id": result.get("task_id"),
            "schedule_id": schedule_id,
            "executed_at": result["executed_at"],
            "message": "Report generation started successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute schedule")

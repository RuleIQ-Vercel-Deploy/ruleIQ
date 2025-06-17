"""
Reporting API endpoints for ComplianceGPT
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import io

from api.dependencies.auth import get_current_user
from database.db_setup import get_db
from services.reporting.report_generator import ReportGenerator
from services.reporting.pdf_generator import PDFGenerator
from services.reporting.template_manager import TemplateManager
from sqlalchemy_access import User

router = APIRouter()

# Pydantic models for request/response
class ReportRequest(BaseModel):
    """Request model for report generation"""
    business_profile_id: UUID
    report_type: str = Field(..., description="Type of report to generate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Report parameters")
    output_format: str = Field(default="pdf", description="Output format (pdf, json)")
    template_customizations: Dict[str, Any] = Field(default_factory=dict, description="Template customizations")

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


@router.get("/templates", response_model=TemplateListResponse)
async def list_report_templates(
    current_user: User = Depends(get_current_user)
):
    """List available report templates"""
    template_manager = TemplateManager()
    templates = template_manager.list_templates()
    
    return TemplateListResponse(templates=templates)


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
            parameters=request.parameters
        )
        
        # Generate unique report ID
        from datetime import datetime
        import uuid
        report_id = str(uuid.uuid4())
        
        response_data = {
            "report_id": report_id,
            "report_type": request.report_type,
            "generated_at": report_data.get('generated_at', datetime.utcnow().isoformat())
        }
        
        if request.output_format.lower() == "pdf":
            # Generate PDF
            pdf_generator = PDFGenerator()
            pdf_bytes = await pdf_generator.generate_pdf(report_data)
            
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
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/generate/pdf")
async def generate_pdf_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
            parameters=request.parameters
        )
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = await pdf_generator.generate_pdf(report_data)
        
        # Create response with PDF
        pdf_io = io.BytesIO(pdf_bytes)
        
        # Set appropriate headers
        headers = {
            'Content-Disposition': f'attachment; filename="{request.report_type}_report.pdf"',
            'Content-Type': 'application/pdf'
        }
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/preview/{report_type}")
async def preview_report_structure(
    report_type: str,
    current_user: User = Depends(get_current_user)
):
    """Preview the structure of a report type"""
    template_manager = TemplateManager()
    template = template_manager.get_template(report_type)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Report type '{report_type}' not found")
    
    return {
        "report_type": report_type,
        "template": template,
        "supported_parameters": _get_supported_parameters(report_type)
    }


@router.post("/customize-template/{template_name}")
async def customize_report_template(
    template_name: str,
    customizations: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Customize a report template"""
    try:
        template_manager = TemplateManager()
        customized_template = template_manager.customize_template(template_name, customizations)
        
        return {
            "template_name": template_name,
            "customized_template": customized_template,
            "message": "Template customized successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template customization failed: {str(e)}")


def _get_supported_parameters(report_type: str) -> Dict[str, Any]:
    """Get supported parameters for a report type"""
    common_params = {
        "frameworks": {
            "type": "array",
            "description": "List of compliance frameworks to include",
            "items": {"type": "string"},
            "example": ["ISO27001", "SOC2", "GDPR"]
        },
        "period_days": {
            "type": "integer",
            "description": "Number of days to analyze for trends",
            "default": 30,
            "minimum": 1,
            "maximum": 365
        }
    }
    
    type_specific_params = {
        "executive_summary": {
            **common_params,
            "include_charts": {
                "type": "boolean",
                "description": "Include charts and visualizations",
                "default": True
            }
        },
        "gap_analysis": {
            **common_params,
            "severity_filter": {
                "type": "string",
                "description": "Filter gaps by severity level",
                "enum": ["critical", "high", "medium", "low"],
                "required": False
            },
            "include_remediation_plan": {
                "type": "boolean",
                "description": "Include detailed remediation plan",
                "default": True
            }
        },
        "evidence_report": {
            **common_params,
            "status_filter": {
                "type": "string",
                "description": "Filter evidence by collection status",
                "enum": ["not_started", "in_progress", "collected", "approved"],
                "required": False
            },
            "show_automation_only": {
                "type": "boolean",
                "description": "Show only evidence items with automation opportunities",
                "default": False
            }
        },
        "audit_readiness": {
            **common_params,
            "target_audit_date": {
                "type": "string",
                "format": "date",
                "description": "Target date for audit preparation",
                "required": False
            },
            "include_checklist": {
                "type": "boolean",
                "description": "Include pre-audit checklist",
                "default": True
            }
        }
    }
    
    return type_specific_params.get(report_type, common_params)
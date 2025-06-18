import io
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.schemas.models import ComplianceReport, ReadinessAssessmentResponse
from database.user import User
from services.readiness_service import (
    generate_readiness_assessment,
    generate_compliance_report,
    get_historical_assessments,
)

router = APIRouter()


@router.get("/assessment", response_model=ReadinessAssessmentResponse)
async def get_readiness_assessment(
    framework_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    assessment = await generate_readiness_assessment(
        db=db, user=current_user, framework_id=framework_id
    )
    return assessment

@router.get("/history")
async def get_assessment_history(
    framework_id: Optional[UUID] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    history = get_historical_assessments(current_user, framework_id, limit)
    return history

@router.post("/report")
async def generate_report(
    report_config: ComplianceReport,
    current_user: User = Depends(get_current_active_user)
):
    report_data = await generate_compliance_report(
        current_user,
        report_config.framework,
        report_config.report_type,
        report_config.format,
        report_config.include_evidence,
        report_config.include_recommendations
    )

    if report_config.format == "pdf":
        return StreamingResponse(
            io.BytesIO(report_data),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=compliance_report.pdf"}
        )
    else:
        return report_data

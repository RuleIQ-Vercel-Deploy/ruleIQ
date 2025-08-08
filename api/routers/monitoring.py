"""
Monitoring API Endpoints

Provides API endpoints for system monitoring including:
- Database connection pool metrics
- System health checks
- Performance metrics
- Alert status
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime

from monitoring.database_monitor import get_database_monitor, get_database_health_status
from database.db_setup import get_engine_info


"""
Monitoring API Endpoints

Provides API endpoints for system monitoring including:
- Database connection pool metrics
- System health checks
- Performance metrics
- Alert status
"""

from fastapi import Depends

from api.dependencies.auth import get_current_active_user
from database import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# Duplicate endpoints removed - definitions exist earlier in file

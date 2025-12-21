# -*- coding: utf-8 -*-
"""
Pydantic Models for API Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# DASHBOARD STATS
# ============================================================================

class DashboardStats(BaseModel):
    """Dashboard overview statistics"""
    active_campaigns: int
    total_spend_30d: float
    avg_roas: float
    total_alerts: int
    spend_change_percent: float
    roas_change: float
    alerts_resolved_today: int

# ============================================================================
# CAMPAIGNS
# ============================================================================

class CampaignResponse(BaseModel):
    """Campaign information"""
    id: int
    campaign_id: str
    campaign_name: str
    status: str
    country: Optional[str]
    spend_30d: float
    roas: float
    ctr: float
    cpc: float
    conversions: int
    alert_count: int
    last_updated: datetime

class PerformanceMetrics(BaseModel):
    """Performance metrics over time"""
    date: str
    spend: float
    conversions: int
    roas: float
    ctr: float
    cpc: float

# ============================================================================
# ALERTS
# ============================================================================

class AlertResponse(BaseModel):
    """Alert information"""
    id: int
    campaign_id: int
    campaign_name: str
    alert_type: str
    severity: str  # CRITICAL, WARNING, INFO
    message: str
    metric_value: Optional[float]
    metric_target: Optional[float]
    created_at: datetime
    resolved: bool

# ============================================================================
# ACTIONS
# ============================================================================

class ActionResponse(BaseModel):
    """AI Action recommendation"""
    id: int
    campaign_id: int
    campaign_name: str
    action_type: str
    priority: str
    target: Dict[str, Any]
    reason: str
    expected_impact: str
    confidence: float
    ai_summary: str
    status: str
    created_at: datetime

class ApproveActionRequest(BaseModel):
    """Request to approve an action"""
    notes: Optional[str] = None

class RejectActionRequest(BaseModel):
    """Request to reject an action"""
    reason: str

# ============================================================================
# SETTINGS
# ============================================================================

class SettingsResponse(BaseModel):
    """User settings"""
    ai_provider: str
    monitor_interval_hours: int
    target_ctr_min: float
    target_cpc_max: float
    target_roas_min: float

class SettingsUpdateRequest(BaseModel):
    """Update settings request"""
    ai_provider: Optional[str] = None
    monitor_interval_hours: Optional[int] = None
    target_ctr_min: Optional[float] = None
    target_cpc_max: Optional[float] = None
    target_roas_min: Optional[float] = None

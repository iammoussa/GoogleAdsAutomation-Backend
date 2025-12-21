"""
Stats Router - Dashboard statistics and analytics
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from database.database import get_db
from agents.monitor import CampaignMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    start_date: Optional[str] = Query(
        default=None, 
        description="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        default=None, 
        description="End date (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics with period-over-period comparison
    
    **Query Parameters:**
    - `start_date`: Start date for current period (YYYY-MM-DD)
    - `end_date`: End date for current period (YYYY-MM-DD)
    
    **Returns:**
    - Current period metrics (spend, conversions, cost/conv, value)
    - Percentage change vs previous period
    - Period details
    """
    try:
        logger.info(f"📊 Fetching dashboard stats from {start_date} to {end_date}")
        
        # Parse dates or use defaults
        if start_date and end_date:
            current_start = datetime.strptime(start_date, '%Y-%m-%d')
            current_end = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Default: last 30 days
            current_end = datetime.now()
            current_start = current_end - timedelta(days=29)
        
        # Calculate duration
        duration_days = (current_end - current_start).days + 1
        
        # Calculate previous period (same duration, immediately before)
        previous_end = current_start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=duration_days - 1)
        
        logger.info(f"📅 Current:  {current_start.date()} to {current_end.date()} ({duration_days} days)")
        logger.info(f"📅 Previous: {previous_start.date()} to {previous_end.date()} ({duration_days} days)")
        
        # Fetch live data from Google Ads
        monitor = CampaignMonitor()
        
        # Get current period data
        current_campaigns = monitor.get_campaigns_metrics(
            start_date=current_start.strftime('%Y-%m-%d'),
            end_date=current_end.strftime('%Y-%m-%d')
        )
        
        # Get previous period data
        previous_campaigns = monitor.get_campaigns_metrics(
            start_date=previous_start.strftime('%Y-%m-%d'),
            end_date=previous_end.strftime('%Y-%m-%d')
        )
        
        # Calculate current period totals
        current_spend = sum(float(c.get('cost', 0)) for c in current_campaigns)
        current_conversions = sum(float(c.get('conversions', 0)) for c in current_campaigns)
        current_conv_value = sum(float(c.get('conv_value', 0)) for c in current_campaigns)
        current_cost_per_conv = current_spend / current_conversions if current_conversions > 0 else 0
        
        # Calculate previous period totals
        prev_spend = sum(float(c.get('cost', 0)) for c in previous_campaigns)
        prev_conversions = sum(float(c.get('conversions', 0)) for c in previous_campaigns)
        prev_conv_value = sum(float(c.get('conv_value', 0)) for c in previous_campaigns)
        prev_cost_per_conv = prev_spend / prev_conversions if prev_conversions > 0 else 0
        
        # Calculate percentage changes
        spend_change = ((current_spend - prev_spend) / prev_spend * 100) if prev_spend > 0 else 0
        conversions_change = ((current_conversions - prev_conversions) / prev_conversions * 100) if prev_conversions > 0 else 0
        cost_per_conv_change = ((current_cost_per_conv - prev_cost_per_conv) / prev_cost_per_conv * 100) if prev_cost_per_conv > 0 else 0
        value_change = ((current_conv_value - prev_conv_value) / prev_conv_value * 100) if prev_conv_value > 0 else 0
        
        logger.success(f"✅ Current: €{current_spend:.2f}, {int(current_conversions)} conv")
        logger.success(f"✅ Previous: €{prev_spend:.2f}, {int(prev_conversions)} conv")
        logger.success(f"✅ Changes: spend {spend_change:+.1f}%, conv {conversions_change:+.1f}%")
        
        return {
            'spend': round(current_spend, 2),
            'spend_change': round(spend_change, 1),
            'conversions': int(current_conversions),
            'conversions_change': round(conversions_change, 1),
            'cost_per_conversion': round(current_cost_per_conv, 2),
            'cost_per_conv_change': round(cost_per_conv_change, 1),
            'conversion_value': round(current_conv_value, 2),
            'value_change': round(value_change, 1),
            'period': {
                'start_date': current_start.strftime('%Y-%m-%d'),
                'end_date': current_end.strftime('%Y-%m-%d'),
                'duration_days': duration_days,
            },
            'comparison_period': {
                'start_date': previous_start.strftime('%Y-%m-%d'),
                'end_date': previous_end.strftime('%Y-%m-%d'),
            },
            'source': 'live',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""
Campaigns Router - Get campaign data with optional extended metrics
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database.database import get_db
from agents.monitor import CampaignMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("")
async def get_campaigns(
    live: bool = Query(
        default=True, 
        description="Fetch live data from Google Ads API"
    ),
    start_date: Optional[str] = Query(
        default=None, 
        description="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        default=None, 
        description="End date (YYYY-MM-DD)"
    ),
    extended_fields: Optional[List[str]] = Query(
        default=None,
        description="Extended metric fields to fetch (e.g., conversion_rate, viewable_impressions)"
    ),
    db: Session = Depends(get_db)
):
    """
    Get campaigns with metrics
    
    **Query Parameters:**
    - `live`: Fetch live data from Google Ads API (default: true)
    - `start_date`: Filter by start date (YYYY-MM-DD)
    - `end_date`: Filter by end date (YYYY-MM-DD)
    - `extended_fields`: List of extended metrics to fetch
    
    **Extended Fields Available:**
    - conversion_rate
    - cost_per_action
    - viewable_impressions
    - viewable_ctr
    - all_conversions
    - all_conversion_value
    - interactions
    - interaction_rate
    - engagements
    - engagement_rate
    - search_impression_share
    - search_top_impression_share
    
    **Returns:**
    - List of campaigns with requested metrics
    """
    try:
        logger.info(f"🔴 Fetching {'LIVE' if live else 'CACHED'} campaign data...")
        
        monitor = CampaignMonitor()
        campaigns_data = monitor.get_campaigns_metrics(
            start_date=start_date,
            end_date=end_date,
            extended_fields=extended_fields
        )
        
        # Format response
        campaigns = []
        for campaign_dict in campaigns_data:
            # Base fields (always present)
            campaign_response = {
                'campaign_id': str(campaign_dict.get('campaign_id', '')),
                'campaign_name': campaign_dict.get('campaign_name', 'Unknown'),
                'status': campaign_dict.get('status', 'UNKNOWN'),
                'impressions': campaign_dict.get('impressions', 0),
                'clicks': campaign_dict.get('clicks', 0),
                'cost': campaign_dict.get('cost', 0),
                'ctr': campaign_dict.get('ctr', 0),
                'conversions': campaign_dict.get('conversions', 0),
                'conversion_value': campaign_dict.get('conv_value', 0),
                'cost_per_conv': campaign_dict.get('cost_per_conv', 0),
                'cpc': campaign_dict.get('cpc', 0),
                'roas': campaign_dict.get('roas', 0),
                'timestamp': campaign_dict.get('timestamp', datetime.now()).isoformat()
            }
            
            # Add extended fields if present
            if extended_fields:
                for field in extended_fields:
                    if field in campaign_dict:
                        campaign_response[field] = campaign_dict[field]
            
            campaigns.append(campaign_response)
        
        logger.success(f"✅ Fetched {len(campaigns)} campaigns")
        
        return {
            'campaigns': campaigns,
            'total': len(campaigns),
            'source': 'live' if live else 'cached',
            'extended_fields': extended_fields or [],
            'date_range': {
                'start': start_date or 'today',
                'end': end_date or 'today'
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-fields")
async def get_available_fields():
    """
    Get list of all available metric fields
    
    **Returns:**
    - base_fields: Always fetched fields
    - extended_fields: Optional fields (fetch on demand)
    - descriptions: Field descriptions
    """
    return {
        "base_fields": [
            "campaign_id",
            "campaign_name",
            "status",
            "cost",
            "impressions",
            "clicks",
            "ctr",
            "conversions",
            "conversion_value",
            "cost_per_conv",
            "cpc",
            "roas",
        ],
        "extended_fields": [
            "conversion_rate",
            "cost_per_action",
            "average_cpm",
            "viewable_impressions",
            "viewable_ctr",
            "all_conversions",
            "all_conversion_value",
            "interactions",
            "interaction_rate",
            "engagements",
            "engagement_rate",
            "search_impression_share",
            "search_top_impression_share",
        ],
        "descriptions": {
            "conversion_rate": "Percentage of interactions that resulted in conversion",
            "cost_per_action": "Average cost per action/conversion",
            "average_cpm": "Average cost per 1000 impressions",
            "viewable_impressions": "Number of viewable impressions",
            "viewable_ctr": "Click-through rate for viewable impressions",
            "all_conversions": "All conversions including cross-device",
            "all_conversion_value": "Total value of all conversions",
            "interactions": "Number of user interactions",
            "interaction_rate": "Percentage of impressions that resulted in interaction",
            "engagements": "Number of engagements",
            "engagement_rate": "Percentage of impressions that resulted in engagement",
            "search_impression_share": "Percentage of impressions received",
            "search_top_impression_share": "Percentage of top impressions",
        }
    }
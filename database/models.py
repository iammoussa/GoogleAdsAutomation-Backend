"""
SQLAlchemy Models per il database (AGGIORNATO con tutte le metriche)
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Numeric,
    Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class CampaignMetric(Base):
    """Metriche storiche campagne - COMPLETE"""
    __tablename__ = 'campaign_metrics'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(BigInteger, nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    
    # Colonne dalla screenshot Google Ads
    budget = Column(Numeric(10, 2))
    status = Column(String(50), index=True)
    bid_strategy_type = Column(String(100))
    optimization_score = Column(Numeric(5, 2))
    campaign_type = Column(String(100))
    
    # Metriche Costi
    cost = Column(Numeric(10, 2), default=0, index=True)
    avg_cost = Column(Numeric(10, 2), default=0)
    cost_per_conv = Column(Numeric(10, 2), default=0)
    
    # Metriche Conversioni
    conversions = Column(Numeric(10, 2), default=0)
    conv_value = Column(Numeric(10, 2), default=0)
    conv_value_per_cost = Column(Numeric(10, 2), default=0)
    
    # Metriche Click
    clicks = Column(Integer, default=0)
    ctr = Column(Numeric(5, 2), default=0)
    avg_cpm = Column(Numeric(10, 2), default=0)
    
    # Metriche Impression
    impressions = Column(Integer, default=0)
    
    # Metriche derivate
    roas = Column(Numeric(10, 2), default=0, index=True)
    cpc = Column(Numeric(10, 2), default=0)
    
    # Extended Metrics - Conversion & Performance
    conversion_rate = Column(Numeric(5, 2), default=0)
    cost_per_action = Column(Numeric(10, 2), default=0)  # CPA
    
    # Viewability Metrics
    viewable_impressions = Column(Integer, default=0)
    viewable_ctr = Column(Numeric(5, 2), default=0)
    
    # Attribution Metrics
    all_conversions = Column(Numeric(10, 2), default=0)
    all_conversion_value = Column(Numeric(10, 2), default=0)
    
    # Engagement Metrics
    interactions = Column(Integer, default=0)
    interaction_rate = Column(Numeric(5, 2), default=0)
    engagements = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2), default=0)
    
    # Competitive Metrics
    search_impression_share = Column(Numeric(5, 2), default=0)
    search_top_impression_share = Column(Numeric(5, 2), default=0)
    
    # Quality Score
    quality_score = Column(Numeric(3, 1))
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<CampaignMetric(campaign='{self.campaign_name}', roas={self.roas}, cost=€{self.cost})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'budget': float(self.budget) if self.budget else None,
            'status': self.status,
            'bid_strategy_type': self.bid_strategy_type,
            'optimization_score': float(self.optimization_score) if self.optimization_score else None,
            'campaign_type': self.campaign_type,
            'cost': float(self.cost) if self.cost else 0,
            'avg_cost': float(self.avg_cost) if self.avg_cost else 0,
            'cost_per_conv': float(self.cost_per_conv) if self.cost_per_conv else 0,
            'conversions': float(self.conversions) if self.conversions else 0,
            'conv_value': float(self.conv_value) if self.conv_value else 0,
            'conv_value_per_cost': float(self.conv_value_per_cost) if self.conv_value_per_cost else 0,
            'clicks': self.clicks,
            'ctr': float(self.ctr) if self.ctr else 0,
            'avg_cpm': float(self.avg_cpm) if self.avg_cpm else 0,
            'impressions': self.impressions,
            'roas': float(self.roas) if self.roas else 0,
            'cpc': float(self.cpc) if self.cpc else 0,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            # Extended metrics
            'conversion_rate': float(self.conversion_rate) if self.conversion_rate else 0,
            'cost_per_action': float(self.cost_per_action) if self.cost_per_action else 0,
            'viewable_impressions': self.viewable_impressions,
            'viewable_ctr': float(self.viewable_ctr) if self.viewable_ctr else 0,
            'all_conversions': float(self.all_conversions) if self.all_conversions else 0,
            'all_conversion_value': float(self.all_conversion_value) if self.all_conversion_value else 0,
            'interactions': self.interactions,
            'interaction_rate': float(self.interaction_rate) if self.interaction_rate else 0,
            'engagements': self.engagements,
            'engagement_rate': float(self.engagement_rate) if self.engagement_rate else 0,
            'search_impression_share': float(self.search_impression_share) if self.search_impression_share else 0,
            'search_top_impression_share': float(self.search_top_impression_share) if self.search_top_impression_share else 0,
        }
    
    def calculate_health(self) -> str:
        """Calcola health status della campagna"""
        ctr = float(self.ctr) if self.ctr else 0
        cpc = float(self.cpc) if self.cpc else 0
        roas = float(self.roas) if self.roas else 0
        conversions = float(self.conversions) if self.conversions else 0
        opt_score = float(self.optimization_score) if self.optimization_score else 50
        
        # CRITICAL
        if (roas < 1.0 and conversions > 0) or opt_score < 40:
            return 'CRITICAL'
        
        # WARNING
        if ctr < 1.5 or cpc > 0.70 or (roas < 1.5 and conversions > 0) or opt_score < 60:
            return 'WARNING'
        
        # EXCELLENT
        if ctr >= 3.0 and roas >= 2.5 and opt_score >= 80:
            return 'EXCELLENT'
        
        return 'GOOD'


class Alert(Base):
    """Alerts per anomalie campagne"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(BigInteger, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text)
    details = Column(JSON)
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Alert(type='{self.alert_type}', severity='{self.severity}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ProposedAction(Base):
    """Azioni di ottimizzazione proposte dall'AI"""
    __tablename__ = 'proposed_actions'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(BigInteger, nullable=False, index=True)
    campaign_name = Column(String(255), nullable=True)  # ✅ Added
    action_type = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False, index=True)
    
    # Dettagli
    target = Column(JSON)
    reason = Column(Text, nullable=False)
    expected_impact = Column(Text)
    confidence = Column(Numeric(3, 2))
    current_value = Column(String(100))  # ✅ Added
    proposed_value = Column(String(100))  # ✅ Added
    
    # AI
    ai_summary = Column(Text)
    ai_model = Column(String(50))
    
    # Status
    status = Column(String(20), default='PENDING', index=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    approved_at = Column(DateTime)
    approved_by = Column(String(100))
    executed_at = Column(DateTime)
    
    # Risultati
    execution_result = Column(JSON)
    execution_error = Column(Text)
    
    # Relationships
    logs = relationship("ActionLog", back_populates="action")
    
    def __repr__(self):
        return f"<ProposedAction(type='{self.action_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,  # ✅ Added
            'action_type': self.action_type,
            'priority': self.priority,
            'target': self.target,
            'reason': self.reason,
            'expected_impact': self.expected_impact,
            'confidence': float(self.confidence) if self.confidence else None,
            'current_value': self.current_value,  # ✅ Added
            'proposed_value': self.proposed_value,  # ✅ Added
            'ai_summary': self.ai_summary,
            'ai_model': self.ai_model,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_result': self.execution_result,
            'execution_error': self.execution_error,
        }


class ActionLog(Base):
    """Log di azioni eseguite"""
    __tablename__ = 'action_logs'
    
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('proposed_actions.id'), index=True)
    campaign_id = Column(BigInteger, nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    
    # Dettagli
    details = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    api_response = Column(JSON)
    
    executed_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    action = relationship("ProposedAction", back_populates="logs")
    
    def __repr__(self):
        return f"<ActionLog(type='{self.action_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'action_id': self.action_id,
            'campaign_id': self.campaign_id,
            'action_type': self.action_type,
            'details': self.details,
            'status': self.status,
            'error_message': self.error_message,
            'api_response': self.api_response,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
        }
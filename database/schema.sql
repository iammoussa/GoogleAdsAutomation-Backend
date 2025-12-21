-- Drop tables if exist (per sviluppo)
DROP TABLE IF EXISTS action_logs CASCADE;
DROP TABLE IF EXISTS proposed_actions CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS campaign_metrics CASCADE;

-- Tabella metriche campagne (COMPLETA con tutte le colonne Google Ads)
CREATE TABLE campaign_metrics (
    id SERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    
    -- Colonne Google Ads (dalla tua screenshot)
    budget DECIMAL(10,2),
    status VARCHAR(50),
    bid_strategy_type VARCHAR(100),
    optimization_score DECIMAL(5,2),
    campaign_type VARCHAR(100),
    
    -- Metriche Costi
    cost DECIMAL(10,2) DEFAULT 0,
    avg_cost DECIMAL(10,2) DEFAULT 0,
    cost_per_conv DECIMAL(10,2) DEFAULT 0,
    
    -- Metriche Conversioni
    conversions DECIMAL(10,2) DEFAULT 0,
    conv_value DECIMAL(10,2) DEFAULT 0,
    conv_value_per_cost DECIMAL(10,2) DEFAULT 0,
    
    -- Metriche Click
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,2) DEFAULT 0,
    avg_cpm DECIMAL(10,2) DEFAULT 0,
    
    -- Metriche Impression
    impressions INTEGER DEFAULT 0,
    
    -- Metriche derivate (calcolate)
    roas DECIMAL(10,2) DEFAULT 0,
    cpc DECIMAL(10,2) DEFAULT 0,
    
    -- Quality Score (se disponibile)
    quality_score DECIMAL(3,1),
    
    -- Metadata
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indici
    CONSTRAINT unique_campaign_timestamp UNIQUE(campaign_id, timestamp)
);

CREATE INDEX idx_campaign_metrics_campaign_id ON campaign_metrics(campaign_id);
CREATE INDEX idx_campaign_metrics_timestamp ON campaign_metrics(timestamp DESC);
CREATE INDEX idx_campaign_metrics_roas ON campaign_metrics(roas);
CREATE INDEX idx_campaign_metrics_status ON campaign_metrics(status);
CREATE INDEX idx_campaign_metrics_cost ON campaign_metrics(cost);

-- Tabella alerts
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    details JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_campaign_id ON alerts(campaign_id);
CREATE INDEX idx_alerts_resolved ON alerts(resolved);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- Tabella azioni proposte
CREATE TABLE proposed_actions (
    id SERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    
    target JSONB,
    reason TEXT NOT NULL,
    expected_impact TEXT,
    confidence DECIMAL(3,2),
    
    ai_summary TEXT,
    ai_model VARCHAR(50),
    
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    approved_by VARCHAR(100),
    executed_at TIMESTAMP,
    
    execution_result JSONB,
    execution_error TEXT
);

CREATE INDEX idx_proposed_actions_campaign_id ON proposed_actions(campaign_id);
CREATE INDEX idx_proposed_actions_status ON proposed_actions(status);
CREATE INDEX idx_proposed_actions_priority ON proposed_actions(priority);
CREATE INDEX idx_proposed_actions_created_at ON proposed_actions(created_at DESC);

-- Tabella log azioni eseguite
CREATE TABLE action_logs (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES proposed_actions(id),
    campaign_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    
    details JSONB NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    
    api_response JSONB,
    
    executed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_action_logs_action_id ON action_logs(action_id);
CREATE INDEX idx_action_logs_campaign_id ON action_logs(campaign_id);
CREATE INDEX idx_action_logs_executed_at ON action_logs(executed_at DESC);

-- View: Latest metrics per campaign
CREATE OR REPLACE VIEW latest_campaign_metrics AS
SELECT DISTINCT ON (campaign_id)
    campaign_id,
    campaign_name,
    budget,
    status,
    bid_strategy_type,
    optimization_score,
    campaign_type,
    cost,
    avg_cost,
    cost_per_conv,
    conversions,
    conv_value,
    conv_value_per_cost,
    clicks,
    ctr,
    avg_cpm,
    impressions,
    roas,
    cpc,
    quality_score,
    timestamp
FROM campaign_metrics
ORDER BY campaign_id, timestamp DESC;

-- View: Pending actions con dettagli campagna
CREATE OR REPLACE VIEW pending_actions_view AS
SELECT 
    pa.*,
    lcm.campaign_name,
    lcm.budget,
    lcm.status as campaign_status,
    lcm.cost,
    lcm.conversions,
    lcm.conv_value,
    lcm.roas,
    lcm.ctr,
    lcm.cpc
FROM proposed_actions pa
LEFT JOIN latest_campaign_metrics lcm ON pa.campaign_id = lcm.campaign_id
WHERE pa.status = 'PENDING'
ORDER BY pa.priority DESC, pa.created_at DESC;

-- Function: calcola health score campagna
CREATE OR REPLACE FUNCTION calculate_campaign_health(
    p_ctr DECIMAL,
    p_cpc DECIMAL,
    p_roas DECIMAL,
    p_conversions DECIMAL,
    p_optimization_score DECIMAL
)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF (p_roas < 1.0 AND p_conversions > 0) OR p_optimization_score < 40 THEN
        RETURN 'CRITICAL';
    END IF;
    
    IF p_ctr < 1.5 OR p_cpc > 0.70 OR (p_roas < 1.5 AND p_conversions > 0) OR p_optimization_score < 60 THEN
        RETURN 'WARNING';
    END IF;
    
    IF p_ctr >= 3.0 AND p_roas >= 2.5 AND p_optimization_score >= 80 THEN
        RETURN 'EXCELLENT';
    END IF;
    
    RETURN 'GOOD';
END;
$$ LANGUAGE plpgsql;

-- View: Campaign Health Summary
CREATE OR REPLACE VIEW campaign_health_summary AS
SELECT 
    campaign_id,
    campaign_name,
    budget,
    status,
    cost,
    conversions,
    conv_value,
    roas,
    ctr,
    cpc,
    optimization_score,
    calculate_campaign_health(ctr, cpc, roas, conversions, optimization_score) as health_status,
    timestamp
FROM latest_campaign_metrics;

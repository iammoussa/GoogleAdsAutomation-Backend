"""
Test per Monitor Agent
"""

import pytest
from datetime import datetime
from agents.monitor import CampaignMonitor


def test_monitor_initialization():
    """Test inizializzazione monitor"""
    monitor = CampaignMonitor()
    assert monitor.customer_id is not None
    assert monitor.client is not None


def test_anomaly_detection():
    """Test rilevamento anomalie"""
    monitor = CampaignMonitor()
    
    # Campaign con CTR basso
    test_campaign = {
        'campaign_id': 123,
        'campaign_name': 'Test Campaign',
        'status': 'ENABLED',
        'ctr': 1.0,  # Sotto target 2.0
        'cpc': 0.45,
        'roas': 2.0,
        'conversions': 5,
        'optimization_score': 70
    }
    
    alerts = monitor.detect_anomalies([test_campaign])
    
    # Dovrebbe rilevare LOW_CTR
    assert len(alerts) > 0
    assert any(a['alert_type'] == 'LOW_CTR' for a in alerts)


def test_metrics_parsing():
    """Test parsing metriche Google Ads"""
    # Mock row from Google Ads API
    # (Requires actual API call - skip in unit test)
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

Perfetto! Ora hai **TUTTO IL CODICE COMPLETO** del sistema!

## 📦 RIEPILOGO FILE CREATI
```
google-ads-automation/
├── 📄 requirements.txt
├── 📄 .env.example
├── 📄 .env
├── 📄 google-ads.yaml.example
├── 📄 google-ads.yaml
├── 📄 .gitignore
├── 📄 README.md
├── 📄 QUICKSTART.md
├── 📄 Makefile
├── 📄 Dockerfile
├── 📄 docker-compose.yml
├── 📄 .dockerignore
├── 🔧 setup.sh
├── 🔧 start.sh
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   ├── schema.sql
│   ├── models.py
│   └── database.py
│
├── agents/
│   ├── __init__.py
│   ├── monitor.py      (Agente B1)
│   ├── analyzer.py     (Agente B2)
│   ├── executor.py     (Agente B3)
│   └── scheduler.py    (Orchestrator)
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── routes/
│       ├── __init__.py
│       ├── campaigns.py
│       └── actions.py
│
├── utils/
│   ├── __init__.py
│   └── logger.py
│
└── tests/
    ├── __init__.py
    └── test_monitor.py

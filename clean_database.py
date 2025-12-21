#!/usr/bin/env python3
"""
Clean Database - Pulisce tutti i dati dal database
Utile per ricominciare da capo con dati freschi
"""

import sys
sys.path.insert(0, '.')

from database.database import get_db_session
from database.models import CampaignMetric, Alert, ProposedAction, ActionLog

print("="*60)
print("🧹 PULIZIA DATABASE")
print("="*60)
print()

response = input("⚠️  Sei sicuro di voler cancellare TUTTI i dati? (scrivi 'YES' per confermare): ")

if response != "YES":
    print("❌ Operazione annullata")
    sys.exit(0)

print()
print("🗑️  Cancellazione dati in corso...")

with get_db_session() as db:
    # Conta record prima
    metrics_count = db.query(CampaignMetric).count()
    alerts_count = db.query(Alert).count()
    actions_count = db.query(ProposedAction).count()
    logs_count = db.query(ActionLog).count()
    
    print(f"   📊 Metriche da cancellare: {metrics_count}")
    print(f"   ⚠️  Alert da cancellare: {alerts_count}")
    print(f"   🎯 Azioni da cancellare: {actions_count}")
    print(f"   📋 Log da cancellare: {logs_count}")
    print()
    
    # Cancella tutto
    db.query(ActionLog).delete()
    db.query(ProposedAction).delete()
    db.query(Alert).delete()
    db.query(CampaignMetric).delete()
    
    db.commit()

print("✅ Database pulito!")
print()
print("💡 Puoi ora:")
print("   • Rigenerare dati mock: python generate_mock_data.py")
print("   • Eseguire Monitor reale: PYTHONPATH=. python agents/monitor.py")
print()

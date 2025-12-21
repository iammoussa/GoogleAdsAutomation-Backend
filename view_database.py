#!/usr/bin/env python3
"""
Database Viewer - Visualizza i dati nel database
"""

import sys
sys.path.insert(0, '.')

from database.database import get_db_session
from database.models import CampaignMetric, Alert, ProposedAction
from sqlalchemy import func, desc
from datetime import datetime

def view_campaigns(detailed=False):
    """Mostra lista campagne"""
    print("="*80)
    print("📊 CAMPAGNE" + (" (DETTAGLIATO)" if detailed else ""))
    print("="*80)
    print()
    
    with get_db_session() as db:
        # Ultime metriche per ogni campagna
        subq = db.query(
            CampaignMetric.campaign_id,
            func.max(CampaignMetric.timestamp).label('max_timestamp')
        ).group_by(CampaignMetric.campaign_id).subquery()
        
        latest = db.query(CampaignMetric).join(
            subq,
            (CampaignMetric.campaign_id == subq.c.campaign_id) &
            (CampaignMetric.timestamp == subq.c.max_timestamp)
        ).all()
        
        if not latest:
            print("   ❌ Nessuna campagna trovata")
            return
        
        for camp in latest:
            print(f"🎯 {camp.campaign_name}")
            print(f"   ID: {camp.campaign_id} | Status: {camp.status}")
            
            if detailed:
                # VISUALIZZAZIONE COMPLETA
                print(f"\n   📋 CONFIGURAZIONE:")
                print(f"      Campaign Type: {camp.campaign_type}")
                print(f"      Bid Strategy: {camp.bid_strategy_type}")
                print(f"      Optimization Score: {camp.optimization_score}/100")
                print(f"      Quality Score: {camp.quality_score if camp.quality_score else 'N/A'}")
                
                print(f"\n   💰 BUDGET & COSTI:")
                print(f"      Budget giornaliero: €{camp.budget}")
                print(f"      Spesa totale: €{camp.cost}")
                print(f"      Costo medio: €{camp.avg_cost}")
                print(f"      % Budget speso: {(float(camp.cost) / float(camp.budget) * 100):.1f}%")
                
                print(f"\n   👁️ IMPRESSIONI & CLICK:")
                print(f"      Impressions: {camp.impressions:,}")
                print(f"      Clicks: {camp.clicks:,}")
                print(f"      CTR: {camp.ctr}%")
                print(f"      CPC medio: €{camp.cpc}")
                print(f"      CPM medio: €{camp.avg_cpm}")
                
                print(f"\n   🎯 CONVERSIONI:")
                print(f"      Conversioni totali: {camp.conversions}")
                print(f"      Valore conversioni: €{camp.conv_value}")
                print(f"      Costo per conversione: €{camp.cost_per_conv}")
                print(f"      Conv. value per cost: {camp.conv_value_per_cost}")
                print(f"      ROAS: {camp.roas}")
                
                print(f"\n   📅 TIMESTAMP:")
                print(f"      Ultimo update: {camp.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      Created at: {camp.created_at.strftime('%Y-%m-%d %H:%M:%S') if camp.created_at else 'N/A'}")
            else:
                # VISUALIZZAZIONE SUMMARY
                print(f"   Budget: €{camp.budget}/day | Spesa: €{camp.cost}")
                print(f"   CTR: {camp.ctr}% | CPC: €{camp.cpc} | Conv: {camp.conversions} | ROAS: {camp.roas}")
                print(f"   Ultimo update: {camp.timestamp.strftime('%Y-%m-%d %H:%M')}")
            
            print()

def view_alerts():
    """Mostra alert attivi"""
    print("="*80)
    print("⚠️  ALERT ATTIVI")
    print("="*80)
    print()
    
    with get_db_session() as db:
        alerts = db.query(Alert).filter(
            Alert.resolved == False
        ).order_by(
            desc(Alert.severity),
            desc(Alert.created_at)
        ).all()
        
        if not alerts:
            print("   ✅ Nessun alert attivo")
            return
        
        severity_emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        
        for alert in alerts:
            print(f"{severity_emoji.get(alert.severity, '⚪')} [{alert.severity}] {alert.campaign_name}")
            print(f"   Type: {alert.alert_type}")
            print(f"   Message: {alert.message}")
            print(f"   Created: {alert.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()

def view_actions():
    """Mostra azioni proposte"""
    print("="*80)
    print("🎯 AZIONI PROPOSTE")
    print("="*80)
    print()
    
    with get_db_session() as db:
        # Raggruppa per status
        for status in ["PENDING", "APPROVED", "REJECTED", "EXECUTED"]:
            actions = db.query(ProposedAction).filter(
                ProposedAction.status == status
            ).order_by(
                desc(ProposedAction.priority),
                desc(ProposedAction.confidence)
            ).all()
            
            if not actions:
                continue
            
            status_emoji = {
                "PENDING": "⏳",
                "APPROVED": "✅",
                "REJECTED": "❌",
                "EXECUTED": "🚀"
            }
            
            print(f"{status_emoji.get(status, '⚪')} {status}: {len(actions)} azioni")
            print()
            
            for action in actions[:5]:  # Mostra max 5 per status
                priority_emoji = "🔴" if action.priority == "HIGH" else "🟡" if action.priority == "MEDIUM" else "🟢"
                print(f"   {priority_emoji} [{action.priority}] {action.action_type}")
                print(f"      Campaign: {action.campaign_id}")
                print(f"      Confidence: {action.confidence}%")
                print(f"      Expected: {action.expected_impact}")
                print(f"      Reason: {action.reason[:100]}...")
                print()
            
            if len(actions) > 5:
                print(f"   ... e altre {len(actions) - 5} azioni")
                print()

def view_stats():
    """Mostra statistiche generali"""
    print("="*80)
    print("📈 STATISTICHE DATABASE")
    print("="*80)
    print()
    
    with get_db_session() as db:
        metrics_count = db.query(CampaignMetric).count()
        campaigns_count = db.query(func.count(func.distinct(CampaignMetric.campaign_id))).scalar()
        alerts_count = db.query(Alert).filter(Alert.resolved == False).count()
        actions_pending = db.query(ProposedAction).filter(ProposedAction.status == "PENDING").count()
        actions_total = db.query(ProposedAction).count()
        
        # Date range
        min_date = db.query(func.min(CampaignMetric.timestamp)).scalar()
        max_date = db.query(func.max(CampaignMetric.timestamp)).scalar()
        
        print(f"   📊 Metriche totali: {metrics_count}")
        print(f"   🎯 Campagne uniche: {campaigns_count}")
        print(f"   ⚠️  Alert attivi: {alerts_count}")
        print(f"   ⏳ Azioni pending: {actions_pending}/{actions_total}")
        
        if min_date and max_date:
            print(f"   📅 Periodo dati: {min_date.strftime('%Y-%m-%d')} → {max_date.strftime('%Y-%m-%d')}")
        
        print()

def main():
    """Menu principale"""
    while True:
        print()
        print("="*80)
        print("🔍 DATABASE VIEWER")
        print("="*80)
        print()
        print("Scegli una vista:")
        print("  1. 📊 Campagne (summary)")
        print("  2. 📋 Campagne (dettagliato - tutti i campi)")
        print("  3. ⚠️  Alert attivi")
        print("  4. 🎯 Azioni proposte")
        print("  5. 📈 Statistiche")
        print("  6. 🔄 Visualizza tutto")
        print("  0. ❌ Esci")
        print()
        
        choice = input("Scelta: ").strip()
        print()
        
        if choice == "1":
            view_campaigns(detailed=False)
        elif choice == "2":
            view_campaigns(detailed=True)
        elif choice == "3":
            view_alerts()
        elif choice == "4":
            view_actions()
        elif choice == "5":
            view_stats()
        elif choice == "6":
            view_stats()
            view_campaigns(detailed=True)
            view_alerts()
            view_actions()
        elif choice == "0":
            print("👋 Ciao!")
            break
        else:
            print("❌ Scelta non valida")
        
        input("\nPremi ENTER per continuare...")

if __name__ == "__main__":
    main()

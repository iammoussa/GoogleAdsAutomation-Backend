#!/usr/bin/env python3
"""
Mock Data Generator per Google Ads Automation
Popola il database con campagne, metriche e alert realistici
"""

import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add project to path
sys.path.insert(0, '.')

from database.database import get_db_session, init_db
from database.models import CampaignMetric, Alert, ProposedAction
from utils.logger import get_logger

logger = get_logger(__name__)


class MockDataGenerator:
    """Generatore di dati mock realistici"""
    
    def __init__(self):
        self.campaign_templates = [
            {
                "id": 1001,
                "name": "🇮🇹 Scarpe Running - Italia",
                "type": "DEMAND_GEN",
                "budget_base": 50.0,
                "performance_tier": "high"  # Alto CTR, buon ROAS
            },
            {
                "id": 1002,
                "name": "🇩🇪 Fitness Equipment - Germany",
                "type": "DEMAND_GEN",
                "budget_base": 75.0,
                "performance_tier": "medium"  # Performance media
            },
            {
                "id": 1003,
                "name": "🇫🇷 Supplements - France",
                "type": "DEMAND_GEN",
                "budget_base": 40.0,
                "performance_tier": "low"  # CTR basso, serve ottimizzazione
            },
            {
                "id": 1004,
                "name": "🇪🇸 Smartwatch - Spain",
                "type": "DEMAND_GEN",
                "budget_base": 60.0,
                "performance_tier": "high"
            },
            {
                "id": 1005,
                "name": "🇬🇧 Yoga Accessories - UK",
                "type": "DEMAND_GEN",
                "budget_base": 35.0,
                "performance_tier": "medium"
            },
        ]
    
    def generate_metrics_for_campaign(
        self,
        campaign: dict,
        date: datetime,
        trend: str = "stable"
    ) -> dict:
        """
        Genera metriche realistiche per una campagna
        
        Args:
            campaign: Template campagna
            date: Data delle metriche
            trend: 'improving', 'declining', 'stable'
        """
        tier = campaign["performance_tier"]
        budget = campaign["budget_base"]
        
        # Base metrics per tier
        if tier == "high":
            base_ctr = random.uniform(3.0, 4.5)
            base_cpc = random.uniform(0.35, 0.50)
            base_cvr = random.uniform(3.5, 5.0)  # Conversion rate %
            base_roas = random.uniform(2.5, 4.0)
        elif tier == "medium":
            base_ctr = random.uniform(2.0, 3.0)
            base_cpc = random.uniform(0.45, 0.65)
            base_cvr = random.uniform(2.0, 3.5)
            base_roas = random.uniform(1.5, 2.5)
        else:  # low
            base_ctr = random.uniform(0.8, 1.8)
            base_cpc = random.uniform(0.55, 0.80)
            base_cvr = random.uniform(1.0, 2.0)
            base_roas = random.uniform(0.8, 1.5)
        
        # Applica trend
        if trend == "improving":
            base_ctr *= random.uniform(1.05, 1.15)
            base_cpc *= random.uniform(0.90, 0.95)
            base_roas *= random.uniform(1.10, 1.20)
        elif trend == "declining":
            base_ctr *= random.uniform(0.85, 0.95)
            base_cpc *= random.uniform(1.05, 1.15)
            base_roas *= random.uniform(0.80, 0.90)
        
        # Calcola metriche derivate
        cost = budget * random.uniform(0.70, 0.95)  # 70-95% del budget speso
        
        # Da cost e CPC → clicks
        clicks = int(cost / base_cpc)
        
        # Da clicks e CTR → impressions
        impressions = int(clicks / (base_ctr / 100))
        
        # Da clicks e CVR → conversions
        conversions = clicks * (base_cvr / 100)
        
        # Da conversions e ROAS → conversion value
        conv_value = cost * base_roas
        
        # CPM
        avg_cpm = (cost / impressions) * 1000 if impressions > 0 else 0
        
        # Optimization score
        if tier == "high":
            opt_score = random.uniform(75, 95)
        elif tier == "medium":
            opt_score = random.uniform(55, 75)
        else:
            opt_score = random.uniform(35, 55)
        
        return {
            "campaign_id": campaign["id"],
            "campaign_name": campaign["name"],
            "campaign_type": campaign["type"],
            "status": "ENABLED",
            "budget": Decimal(str(round(budget, 2))),
            "bid_strategy_type": "MAXIMIZE_CONVERSIONS",
            "optimization_score": round(opt_score, 1),
            
            # Metriche performance
            "cost": Decimal(str(round(cost, 2))),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": Decimal(str(round(base_ctr, 2))),
            "cpc": Decimal(str(round(base_cpc, 2))),
            "avg_cpm": Decimal(str(round(avg_cpm, 2))),
            
            # Conversioni
            "conversions": Decimal(str(round(conversions, 1))),
            "conv_value": Decimal(str(round(conv_value, 2))),
            "cost_per_conv": Decimal(str(round(cost / conversions if conversions > 0 else 0, 2))),
            "conv_value_per_cost": Decimal(str(round(conv_value / cost if cost > 0 else 0, 2))),
            
            # Metriche derivate
            "roas": Decimal(str(round(base_roas, 2))),
            "avg_cost": Decimal(str(round(cost / clicks if clicks > 0 else 0, 2))),
            
            "timestamp": date
        }
    
    def generate_historical_data(self, days: int = 7) -> list:
        """Genera storico di X giorni per tutte le campagne"""
        all_metrics = []
        
        for day_offset in range(days, 0, -1):
            date = datetime.now() - timedelta(days=day_offset)
            
            # Determina trend giornaliero
            if day_offset <= 2:
                trend = "improving"  # Ultimi 2 giorni in miglioramento
            elif day_offset >= 5:
                trend = "declining"  # Giorni più vecchi peggiori
            else:
                trend = "stable"
            
            for campaign in self.campaign_templates:
                metrics = self.generate_metrics_for_campaign(campaign, date, trend)
                all_metrics.append(metrics)
        
        return all_metrics
    
    def detect_alerts(self, metrics: dict) -> list:
        """Rileva alert basati sulle metriche"""
        alerts = []
        
        # Alert: CTR basso
        if metrics["ctr"] < 2.0:
            alerts.append({
                "campaign_id": metrics["campaign_id"],
                "alert_type": "LOW_CTR",
                "severity": "HIGH" if metrics["ctr"] < 1.5 else "MEDIUM",
                "message": f"CTR molto basso: {metrics['ctr']}% (target: 2.0%)",
                "details": {
                    "metric_name": "ctr",
                    "metric_value": float(metrics["ctr"]),
                    "threshold": 2.0,
                    "campaign_name": metrics["campaign_name"]
                },
                "resolved": False,
                "created_at": metrics["timestamp"]
            })
        
        # Alert: CPC alto
        if metrics["cpc"] > 0.60:
            alerts.append({
                "campaign_id": metrics["campaign_id"],
                "alert_type": "HIGH_CPC",
                "severity": "HIGH" if metrics["cpc"] > 0.70 else "MEDIUM",
                "message": f"CPC troppo alto: €{metrics['cpc']} (target: €0.60)",
                "details": {
                    "metric_name": "cpc",
                    "metric_value": float(metrics["cpc"]),
                    "threshold": 0.60,
                    "campaign_name": metrics["campaign_name"]
                },
                "resolved": False,
                "created_at": metrics["timestamp"]
            })
        
        # Alert: ROAS basso
        if metrics["roas"] < 1.5:
            alerts.append({
                "campaign_id": metrics["campaign_id"],
                "alert_type": "LOW_ROAS",
                "severity": "HIGH" if metrics["roas"] < 1.0 else "MEDIUM",
                "message": f"ROAS sotto target: {metrics['roas']} (target: 1.5)",
                "details": {
                    "metric_name": "roas",
                    "metric_value": float(metrics["roas"]),
                    "threshold": 1.5,
                    "campaign_name": metrics["campaign_name"]
                },
                "resolved": False,
                "created_at": metrics["timestamp"]
            })
        
        # Alert: Optimization score basso
        if metrics["optimization_score"] < 60:
            alerts.append({
                "campaign_id": metrics["campaign_id"],
                "alert_type": "LOW_OPTIMIZATION_SCORE",
                "severity": "MEDIUM",
                "message": f"Optimization score basso: {metrics['optimization_score']}/100",
                "details": {
                    "metric_name": "optimization_score",
                    "metric_value": float(metrics["optimization_score"]),
                    "threshold": 60.0,
                    "campaign_name": metrics["campaign_name"]
                },
                "resolved": False,
                "created_at": metrics["timestamp"]
            })
        
        return alerts
    
    def generate_mock_actions(self, campaign_id: int, campaign_name: str) -> list:
        """Genera azioni mock (come se fossero proposte dall'AI)"""
        actions = []
        
        # Trova il tier della campagna
        campaign = next((c for c in self.campaign_templates if c["id"] == campaign_id), None)
        if not campaign:
            return actions
        
        tier = campaign["performance_tier"]
        
        if tier == "low":
            # Campagne low performance → azioni aggressive
            actions.extend([
                {
                    "campaign_id": campaign_id,
                    "action_type": "PAUSE_KEYWORD",
                    "priority": "HIGH",
                    "target": {"keyword": "scarpe economiche", "reason": "CTR 0.3%, troppo basso"},
                    "reason": "Keyword con CTR estremamente basso (0.3%) sta consumando budget senza risultati. Pausando questa keyword si ridurrà il CPC medio e si migliorerà il CTR complessivo.",
                    "expected_impact": "Riduzione CPC del 12%, miglioramento CTR del 18%",
                    "confidence": 0.88,  # 88% come decimal 0-1
                    "status": "PENDING"
                },
                {
                    "campaign_id": campaign_id,
                    "action_type": "ADD_NEGATIVE_KEYWORD",
                    "priority": "MEDIUM",
                    "target": {"keywords": ["gratis", "gratuito", "free"]},
                    "reason": "Rilevate ricerche con intento non commerciale che generano click ma zero conversioni.",
                    "expected_impact": "Riduzione costi del 8%, miglioramento conversion rate del 15%",
                    "confidence": 0.75,  # 75% come decimal 0-1
                    "status": "PENDING"
                },
                {
                    "campaign_id": campaign_id,
                    "action_type": "REDUCE_BID",
                    "priority": "HIGH",
                    "target": {"ad_group": "Generic Terms", "current_bid": 0.75, "new_bid": 0.45},
                    "reason": "Bid troppo alto per ad group con bassa conversion rate. CPC attuale €0.75 con CVR 1.2%.",
                    "expected_impact": "Risparmio €8-12/giorno, ROAS previsto +0.4",
                    "confidence": 0.82,  # 82% come decimal 0-1
                    "status": "PENDING"
                }
            ])
        
        elif tier == "medium":
            # Campagne medie → ottimizzazioni
            actions.extend([
                {
                    "campaign_id": campaign_id,
                    "action_type": "INCREASE_BUDGET",
                    "priority": "MEDIUM",
                    "target": {"current_budget": campaign["budget_base"], "new_budget": campaign["budget_base"] * 1.3},
                    "reason": "Campagna sta performando bene (ROAS 2.2) ma è limitata da budget. Negli ultimi 3 giorni ha raggiunto il 95% del budget giornaliero.",
                    "expected_impact": "Aumento conversioni del 25-30%, mantenimento ROAS attuale",
                    "confidence": 0.79,  # 79% come decimal 0-1
                    "status": "PENDING"
                },
                {
                    "campaign_id": campaign_id,
                    "action_type": "INCREASE_BID",
                    "priority": "LOW",
                    "target": {"ad_group": "High Intent Keywords", "current_bid": 0.45, "new_bid": 0.60},
                    "reason": "Keyword ad alto intento con ottimo CVR (4.5%) ma share of voice basso. Aumentando il bid possiamo catturare più traffico qualificato.",
                    "expected_impact": "Aumento impressions del 35%, conversioni +40%",
                    "confidence": 0.71,  # 71% come decimal 0-1
                    "status": "PENDING"
                }
            ])
        
        else:  # high
            # Campagne top → scaling
            actions.extend([
                {
                    "campaign_id": campaign_id,
                    "action_type": "INCREASE_BUDGET",
                    "priority": "HIGH",
                    "target": {"current_budget": campaign["budget_base"], "new_budget": campaign["budget_base"] * 1.5},
                    "reason": "Campagna top performer con ROAS 3.2 e CTR 4.1%. Budget limitante: ha raggiunto il cap giornaliero per 5 giorni consecutivi. Opportunità di scaling immediata.",
                    "expected_impact": "Aumento conversioni del 45-50%, ROAS previsto 2.8-3.0 (lieve calo accettabile per volume)",
                    "confidence": 0.92,  # 92% come decimal 0-1
                    "status": "PENDING"
                },
                {
                    "campaign_id": campaign_id,
                    "action_type": "INCREASE_BID",
                    "priority": "MEDIUM",
                    "target": {"ad_group": "Brand Keywords", "current_bid": 0.35, "new_bid": 0.50},
                    "reason": "Keyword branded con conversion rate eccezionale (8.2%) e CPA molto basso. Aumentando il bid possiamo dominare completamente la SERP e bloccare competitor.",
                    "expected_impact": "Impression share da 65% a 90%, conversioni +35%",
                    "confidence": 0.85,  # 85% come decimal 0-1
                    "status": "PENDING"
                }
            ])
        
        return actions
    
    def populate_database(self, days: int = 7):
        """Popola il database con dati mock completi"""
        print("="*60)
        print("🎨 GENERAZIONE DATI MOCK")
        print("="*60)
        print()
        
        # 1. Inizializza database
        print("1️⃣  Inizializzazione database...")
        init_db()
        print("   ✅ Database pronto")
        print()
        
        # 2. Genera metriche storiche
        print(f"2️⃣  Generazione storico {days} giorni...")
        all_metrics = self.generate_historical_data(days)
        print(f"   ✅ Generate {len(all_metrics)} righe di metriche")
        print()
        
        # 3. Salva metriche
        print("3️⃣  Salvataggio metriche nel database...")
        with get_db_session() as db:
            for metrics_data in all_metrics:
                metric = CampaignMetric(**metrics_data)
                db.add(metric)
            db.commit()
        print(f"   ✅ Salvate {len(all_metrics)} metriche")
        print()
        
        # 4. Genera e salva alert (usa TUTTE le metriche recenti, non solo oggi)
        print("4️⃣  Generazione alert...")
        # Prendi le metriche più recenti per ogni campagna
        recent_metrics = []
        seen_campaigns = set()
        
        for metrics in sorted(all_metrics, key=lambda x: x["timestamp"], reverse=True):
            if metrics["campaign_id"] not in seen_campaigns:
                recent_metrics.append(metrics)
                seen_campaigns.add(metrics["campaign_id"])
        
        all_alerts = []
        for metrics in recent_metrics:
            alerts = self.detect_alerts(metrics)
            all_alerts.extend(alerts)
        
        with get_db_session() as db:
            for alert_data in all_alerts:
                alert = Alert(**alert_data)
                db.add(alert)
            db.commit()
        
        print(f"   ✅ Generati {len(all_alerts)} alert")
        print()
        
        # 5. Genera azioni proposte mock
        print("5️⃣  Generazione azioni proposte mock...")
        all_actions = []
        
        for campaign in self.campaign_templates:
            actions = self.generate_mock_actions(campaign["id"], campaign["name"])
            all_actions.extend(actions)
        
        with get_db_session() as db:
            for action_data in all_actions:
                action = ProposedAction(
                    **action_data,
                    ai_summary=f"Analisi AI per {action_data['campaign_id']}: Campagna analizzata con Gemini"
                )
                db.add(action)
            db.commit()
        
        print(f"   ✅ Generate {len(all_actions)} azioni proposte")
        print()
        
        # 6. Summary
        print("="*60)
        print("✅ DATI MOCK GENERATI CON SUCCESSO!")
        print("="*60)
        print()
        print("📊 RIEPILOGO:")
        print(f"   • Campagne: {len(self.campaign_templates)}")
        print(f"   • Metriche storiche: {len(all_metrics)} ({days} giorni)")
        print(f"   • Alert attivi: {len(all_alerts)}")
        print(f"   • Azioni proposte: {len(all_actions)}")
        print()
        print("📋 CAMPAGNE GENERATE:")
        for campaign in self.campaign_templates:
            tier_emoji = "🟢" if campaign["performance_tier"] == "high" else "🟡" if campaign["performance_tier"] == "medium" else "🔴"
            print(f"   {tier_emoji} {campaign['name']} (Budget: €{campaign['budget_base']}/day)")
        print()
        print("🎯 PROSSIMI PASSI:")
        print("   1. Visualizza dati: psql google_ads_automation")
        print("   2. Test Analyzer: PYTHONPATH=. python agents/analyzer.py --all")
        print("   3. Crea la tua dashboard!")
        print()


if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.populate_database(days=7)

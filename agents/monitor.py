"""
AGENTE B1: MONITOR
Estrae metriche da Google Ads e salva in database
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

from database.database import get_db_session
from database.models import CampaignMetric, Alert
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CampaignMonitor:
    """Monitor per campagne Google Ads"""
    
    def __init__(self, customer_id: Optional[str] = None):
        """
        Inizializza il monitor
        
        Args:
            customer_id: ID cliente Google Ads (se None, usa quello da settings)
        """
        self.customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID
        
        # Carica client Google Ads
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
            logger.info(f"✅ Google Ads client inizializzato per customer {self.customer_id}")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Google Ads client: {e}")
            raise
    
    def get_campaigns_metrics(
        self, 
        campaign_ids: Optional[List[int]] = None,
        extended_fields: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Estrae metriche delle campagne da Google Ads API
        
        Args:
            campaign_ids: Lista di campaign IDs specifici (se None, prende tutte)
            extended_fields: Lista campi extended da fetchare (opzionale)
            start_date: Data inizio (YYYY-MM-DD)
            end_date: Data fine (YYYY-MM-DD)
        
        Returns:
            Lista di dizionari con metriche complete
        """
        logger.info(f"🔍 Inizio estrazione metriche campagne...")
        
        # Query GAQL (Google Ads Query Language)
        # Include TUTTE le colonne dalla screenshot + altre utili
        query = """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign_budget.amount_micros,
                campaign.bidding_strategy_type,
                campaign.optimization_score,
                campaign.advertising_channel_type,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.average_cpm,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_per_conversion,
                metrics.value_per_conversion
            FROM campaign
            WHERE campaign.status IN ('ENABLED', 'PAUSED')
                AND segments.date DURING TODAY
        """
        
        # Aggiungi filtro per campaign_ids specifici se forniti
        if campaign_ids:
            ids_str = ", ".join(str(id) for id in campaign_ids)
            query += f" AND campaign.id IN ({ids_str})"
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Esegui query
            stream = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            campaigns = []
            
            for batch in stream:
                for row in batch.results:
                    campaign = self._parse_campaign_row(row)
                    campaigns.append(campaign)
            
            logger.info(f"✅ Estratte metriche per {len(campaigns)} campagne")
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            for error in ex.failure.errors:
                logger.error(f"  - {error.message}")
            raise
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            raise
    
    def _parse_campaign_row(self, row) -> Dict[str, Any]:
        """
        Converte una riga della risposta Google Ads in dizionario
        
        Args:
            row: Riga dalla risposta Google Ads API
        
        Returns:
            Dizionario con tutte le metriche
        """
        campaign = row.campaign
        metrics = row.metrics
        budget = row.campaign_budget
        
        # Conversioni da micros a euro
        cost = metrics.cost_micros / 1_000_000
        budget_amount = budget.amount_micros / 1_000_000 if budget.amount_micros else None
        avg_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0
        avg_cpm = metrics.average_cpm / 1_000_000 if metrics.average_cpm else 0
        
        # Conversioni
        conversions = metrics.conversions
        conv_value = metrics.conversions_value
        cost_per_conv = metrics.cost_per_conversion / 1_000_000 if metrics.cost_per_conversion else 0
        
        # Calcola metriche derivate
        roas = (conv_value / cost) if cost > 0 else 0
        conv_value_per_cost = roas  # Ãˆ la stessa cosa
        avg_cost = cost / conversions if conversions > 0 else 0
        
        return {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'budget': budget_amount,
            'status': campaign.status.name,
            'bid_strategy_type': campaign.bidding_strategy_type.name,
            'optimization_score': campaign.optimization_score if hasattr(campaign, 'optimization_score') else None,
            'campaign_type': campaign.advertising_channel_type.name,
            
            # Metriche costi
            'cost': cost,
            'avg_cost': avg_cost,
            'cost_per_conv': cost_per_conv,
            
            # Metriche conversioni
            'conversions': conversions,
            'conv_value': conv_value,
            'conv_value_per_cost': conv_value_per_cost,
            
            # Metriche click
            'clicks': metrics.clicks,
            'ctr': metrics.ctr * 100,  # Converti in percentuale
            'avg_cpm': avg_cpm,
            
            # Metriche impression
            'impressions': metrics.impressions,
            
            # Derivate
            'roas': roas,
            'cpc': avg_cpc,
            
            'timestamp': datetime.now()
        }
    
    def save_to_database(self, campaigns: List[Dict[str, Any]]) -> int:
        """
        Salva metriche nel database
        
        Args:
            campaigns: Lista metriche campagne
        
        Returns:
            Numero di record salvati
        """
        logger.info(f"💾 Salvataggio {len(campaigns)} campagne in database...")
        
        saved_count = 0
        
        with get_db_session() as db:
            for campaign_data in campaigns:
                try:
                    metric = CampaignMetric(**campaign_data)
                    db.add(metric)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"❌ Errore salvataggio campagna {campaign_data.get('campaign_name')}: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"✅ Salvate {saved_count} campagne")
        return saved_count
    
    def detect_anomalies(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rileva anomalie nelle metriche
        
        Args:
            campaigns: Lista metriche campagne
        
        Returns:
            Lista di alert rilevati
        """
        logger.info(f"⚠️  Rilevamento anomalie...")
        
        alerts = []
        
        for campaign in campaigns:
            campaign_id = campaign['campaign_id']
            campaign_name = campaign['campaign_name']
            
            # Skip campagne in pausa
            if campaign['status'] == 'PAUSED':
                continue
            
            # 1. CTR troppo basso
            if campaign['ctr'] < settings.TARGET_CTR_MIN:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'LOW_CTR',
                    'severity': 'MEDIUM',
                    'message': f"CTR {campaign['ctr']:.2f}% sotto target {settings.TARGET_CTR_MIN}%",
                    'details': {
                        'current_ctr': campaign['ctr'],
                        'target_ctr': settings.TARGET_CTR_MIN,
                        'campaign_name': campaign_name
                    }
                })
            
            # 2. CPC troppo alto
            if campaign['cpc'] > settings.TARGET_CPC_MAX:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'HIGH_CPC',
                    'severity': 'MEDIUM',
                    'message': f"CPC â‚¬{campaign['cpc']:.2f} sopra target â‚¬{settings.TARGET_CPC_MAX}",
                    'details': {
                        'current_cpc': campaign['cpc'],
                        'target_cpc': settings.TARGET_CPC_MAX,
                        'campaign_name': campaign_name
                    }
                })
            
            # 3. ROAS basso (solo se ci sono conversioni)
            if campaign['conversions'] > 0 and campaign['roas'] < settings.TARGET_ROAS_MIN:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'LOW_ROAS',
                    'severity': 'HIGH',
                    'message': f"ROAS {campaign['roas']:.2f} sotto target {settings.TARGET_ROAS_MIN}",
                    'details': {
                        'current_roas': campaign['roas'],
                        'target_roas': settings.TARGET_ROAS_MIN,
                        'conversions': campaign['conversions'],
                        'cost': campaign['cost'],
                        'campaign_name': campaign_name
                    }
                })
            
            # 4. Optimization Score basso
            if campaign['optimization_score'] and campaign['optimization_score'] < settings.TARGET_OPTIMIZATION_SCORE_MIN:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'LOW_OPTIMIZATION_SCORE',
                    'severity': 'LOW',
                    'message': f"Optimization Score {campaign['optimization_score']:.1f} sotto target {settings.TARGET_OPTIMIZATION_SCORE_MIN}",
                    'details': {
                        'current_score': campaign['optimization_score'],
                        'target_score': settings.TARGET_OPTIMIZATION_SCORE_MIN,
                        'campaign_name': campaign_name
                    }
                })
            
            # 5. Nessuna conversione da 3 giorni (controllo storico)
            # TODO: Implementare query storica nel database
            
            # 6. Budget quasi esaurito
            if campaign['budget'] and campaign['cost'] >= campaign['budget'] * 0.95:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'BUDGET_EXHAUSTED',
                    'severity': 'HIGH',
                    'message': f"Budget quasi esaurito: â‚¬{campaign['cost']:.2f} / â‚¬{campaign['budget']:.2f}",
                    'details': {
                        'cost': campaign['cost'],
                        'budget': campaign['budget'],
                        'percentage_used': (campaign['cost'] / campaign['budget']) * 100,
                        'campaign_name': campaign_name
                    }
                })
        
        logger.info(f"⚠️  Rilevati {len(alerts)} alert")
        return alerts
    
    def save_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Salva alert nel database
        
        Args:
            alerts: Lista alert
        
        Returns:
            Numero di alert salvati
        """
        if not alerts:
            return 0
        
        logger.info(f"💾 Salvataggio {len(alerts)} alert in database...")
        
        saved_count = 0
        
        with get_db_session() as db:
            for alert_data in alerts:
                try:
                    alert = Alert(**alert_data)
                    db.add(alert)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"❌ Errore salvataggio alert: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"✅ Salvati {saved_count} alert")
        return saved_count
    
    def run(self) -> Dict[str, Any]:
        """
        Esegue il ciclo completo di monitoring
        
        Returns:
            Dizionario con risultati
        """
        logger.info("=" * 80)
        logger.info("🚀 INIZIO MONITORING CAMPAGNE")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # 1. Estrai metriche da Google Ads
            campaigns = self.get_campaigns_metrics()
            
            if not campaigns:
                logger.warning("⚠️  Nessuna campagna trovata")
                return {
                    'status': 'WARNING',
                    'campaigns_count': 0,
                    'alerts_count': 0,
                    'message': 'Nessuna campagna trovata'
                }
            
            # 2. Salva metriche in database
            saved_count = self.save_to_database(campaigns)
            
            # 3. Rileva anomalie
            alerts = self.detect_anomalies(campaigns)
            
            # 4. Salva alert
            alerts_saved = self.save_alerts(alerts)
            
            # 5. Risultati
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'SUCCESS',
                'campaigns_count': len(campaigns),
                'campaigns_saved': saved_count,
                'alerts_count': len(alerts),
                'alerts_saved': alerts_saved,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat(),
                'campaigns': campaigns,
                'alerts': alerts
            }
            
            logger.info("=" * 80)
            logger.info(f"✅ MONITORING COMPLETATO in {duration:.2f}s")
            logger.info(f"   - Campagne: {len(campaigns)}")
            logger.info(f"   - Alert: {len(alerts)}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ ERRORE DURANTE MONITORING: {e}")
            raise


# Test standalone
if __name__ == "__main__":
    import json
    
    print("ðŸ§ª Test Agente Monitor\n")
    
    monitor = CampaignMonitor()
    result = monitor.run()
    
    print("\nðŸ“Š RISULTATI:")
    print(json.dumps({
        'status': result['status'],
        'campaigns_count': result['campaigns_count'],
        'alerts_count': result['alerts_count'],
        'duration_seconds': result['duration_seconds']
    }, indent=2))
    
    if result['alerts']:
        print("\n⚠️  ALERT RILEVATI:")
        for alert in result['alerts']:
            print(f"  - [{alert['severity']}] {alert['message']}")
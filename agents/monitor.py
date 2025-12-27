"""
AGENTE B1: MONITOR
Estrae metriche da Google Ads e salva in database
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import requests

from database.database import get_db_session
from database.models import CampaignMetric, Alert
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CampaignMonitor:
    """Monitor per campagne Google Ads"""
    
    def __init__(self, user_id: Optional[str] = None, customer_id: Optional[str] = None):
        """
        Inizializza il monitor con credenziali dinamiche da Supabase
        
        Args:
            user_id: User ID per prendere le credenziali da Supabase
            customer_id: ID cliente Google Ads (opzionale)
        """
        self.user_id = user_id
        self.customer_id = customer_id
        self.access_token = None
        self.refresh_token = None
        self.account_id = None
        
        # Carica credenziali da Supabase
        self._load_credentials_from_db()
        
        # Inizializza client Google Ads con credenziali dinamiche
        try:
            self.client = self._create_google_ads_client()
            logger.info(f"Google Ads client inizializzato per customer {self.customer_id}")
        except Exception as e:
            logger.error(f"Errore inizializzazione Google Ads client: {e}")
            raise
    
    def _load_credentials_from_db(self):
        """Carica access_token e refresh_token da Supabase"""
        try:
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing Supabase credentials in environment")
            
            supabase = create_client(supabase_url, supabase_key)
            
            # Query google_ads_accounts table
            query = supabase.table('google_ads_accounts').select('*')
            
            if self.user_id:
                query = query.eq('user_id', self.user_id)
            
            query = query.eq('is_active', True).order('created_at', desc=True).limit(1)
            
            result = query.execute()
            
            if not result.data:
                raise Exception(f"No active Google Ads account found for user {self.user_id}")
            
            account = result.data[0]
            
            self.access_token = account.get('access_token')
            self.refresh_token = account.get('refresh_token')
            self.customer_id = self.customer_id or account.get('customer_id')
            self.token_expires_at = account.get('token_expires_at')
            self.account_id = account.get('id')
            
            logger.info(f"Loaded credentials for customer {self.customer_id}")
            
            # Check if token is expired
            if self.token_expires_at:
                expires_at = datetime.fromisoformat(self.token_expires_at.replace('Z', '+00:00'))
                if expires_at < datetime.now(expires_at.tzinfo):
                    logger.warning("Token expired, refreshing...")
                    self._refresh_access_token()
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            raise
    
    def _refresh_access_token(self):
        """Refresh access token using refresh token"""
        try:
            if not self.refresh_token:
                raise Exception("No refresh token available")
            
            logger.info("Refreshing access token...")
            
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_ADS_CLIENT_ID,
                    'client_secret': settings.GOOGLE_ADS_CLIENT_SECRET,
                    'refresh_token': self.refresh_token,
                    'grant_type': 'refresh_token',
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Token refresh failed: {response.text}")
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Update token in database
            self._update_token_in_db()
            
            logger.info("Access token refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    def _update_token_in_db(self):
        """Update access token in Supabase"""
        try:
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
            supabase = create_client(supabase_url, supabase_key)
            
            supabase.table('google_ads_accounts').update({
                'access_token': self.access_token,
                'token_expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
                'updated_at': datetime.now().isoformat(),
            }).eq('id', self.account_id).execute()
            
            logger.info("Token updated in database")
            
        except Exception as e:
            logger.error(f"Error updating token: {e}")
    
    def _create_google_ads_client(self) -> GoogleAdsClient:
        """Create Google Ads client with dynamic credentials"""
        
        # Create OAuth2 credentials
        credentials = Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_ADS_CLIENT_ID,
            client_secret=settings.GOOGLE_ADS_CLIENT_SECRET,
        )
        
        # Initialize client with credentials
        client = GoogleAdsClient(
            credentials=credentials,
            developer_token=settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            login_customer_id=self.customer_id,
        )
        
        return client
    
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
        logger.info(f"Inizio estrazione metriche campagne...")
        
        # Query GAQL (Google Ads Query Language)
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
            
            logger.info(f"Estratte metriche per {len(campaigns)} campagne")
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"Errore Google Ads API: {ex}")
            
            # Check if token expired and retry
            for error in ex.failure.errors:
                if 'invalid_grant' in str(error.message).lower() or 'expired' in str(error.message).lower():
                    logger.warning("Token expired during API call, refreshing...")
                    self._refresh_access_token()
                    # Recreate client with new token
                    self.client = self._create_google_ads_client()
                    # Retry the request
                    return self.get_campaigns_metrics(campaign_ids, extended_fields, start_date, end_date)
                logger.error(f"  - {error.message}")
            raise
        except Exception as e:
            logger.error(f"Errore generico: {e}")
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
        conv_value_per_cost = roas
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
            'ctr': metrics.ctr * 100,
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
        logger.info(f"Salvataggio {len(campaigns)} campagne in database...")
        
        saved_count = 0
        
        with get_db_session() as db:
            for campaign_data in campaigns:
                try:
                    metric = CampaignMetric(**campaign_data)
                    db.add(metric)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Errore salvataggio campagna {campaign_data.get('campaign_name')}: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"Salvate {saved_count} campagne")
        return saved_count
    
    def detect_anomalies(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rileva anomalie nelle metriche
        
        Args:
            campaigns: Lista metriche campagne
        
        Returns:
            Lista di alert rilevati
        """
        logger.info(f"Rilevamento anomalie...")
        
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
                    'message': f"CPC EUR{campaign['cpc']:.2f} sopra target EUR{settings.TARGET_CPC_MAX}",
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
            
            # 5. Budget quasi esaurito
            if campaign['budget'] and campaign['cost'] >= campaign['budget'] * 0.95:
                alerts.append({
                    'campaign_id': campaign_id,
                    'alert_type': 'BUDGET_EXHAUSTED',
                    'severity': 'HIGH',
                    'message': f"Budget quasi esaurito: EUR{campaign['cost']:.2f} / EUR{campaign['budget']:.2f}",
                    'details': {
                        'cost': campaign['cost'],
                        'budget': campaign['budget'],
                        'percentage_used': (campaign['cost'] / campaign['budget']) * 100,
                        'campaign_name': campaign_name
                    }
                })
        
        logger.info(f"Rilevati {len(alerts)} alert")
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
        
        logger.info(f"Salvataggio {len(alerts)} alert in database...")
        
        saved_count = 0
        
        with get_db_session() as db:
            for alert_data in alerts:
                try:
                    alert = Alert(**alert_data)
                    db.add(alert)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Errore salvataggio alert: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"Salvati {saved_count} alert")
        return saved_count
    
    def run(self) -> Dict[str, Any]:
        """
        Esegue il ciclo completo di monitoring
        
        Returns:
            Dizionario con risultati
        """
        logger.info("=" * 80)
        logger.info("INIZIO MONITORING CAMPAGNE")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # 1. Estrai metriche da Google Ads
            campaigns = self.get_campaigns_metrics()
            
            if not campaigns:
                logger.warning("Nessuna campagna trovata")
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
            logger.info(f"MONITORING COMPLETATO in {duration:.2f}s")
            logger.info(f"   - Campagne: {len(campaigns)}")
            logger.info(f"   - Alert: {len(alerts)}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"ERRORE DURANTE MONITORING: {e}")
            raise


# Helper function per creare il monitor con user context
def create_monitor_for_user(user_id: str, customer_id: Optional[str] = None) -> CampaignMonitor:
    """
    Crea un'istanza di CampaignMonitor per un utente specifico
    
    Args:
        user_id: User ID dall'autenticazione
        customer_id: Optional specific customer ID
    
    Returns:
        CampaignMonitor configurato
    """
    return CampaignMonitor(user_id=user_id, customer_id=customer_id)


# Test standalone
if __name__ == "__main__":
    import json
    
    print("Test Agente Monitor\n")
    
    monitor = CampaignMonitor()
    result = monitor.run()
    
    print("\nRISULTATI:")
    print(json.dumps({
        'status': result['status'],
        'campaigns_count': result['campaigns_count'],
        'alerts_count': result['alerts_count'],
        'duration_seconds': result['duration_seconds']
    }, indent=2))
    
    if result['alerts']:
        print("\nALERT RILEVATI:")
        for alert in result['alerts']:
            print(f"  - [{alert['severity']}] {alert['message']}")
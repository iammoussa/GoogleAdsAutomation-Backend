"""
AGENTE B3: EXECUTOR
Applica le modifiche approvate alle campagne Google Ads
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

from database.database import get_db_session
from database.models import ProposedAction, ActionLog
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CampaignExecutor:
    """Executor per applicare azioni sulle campagne Google Ads"""
    
    def __init__(self, customer_id: Optional[str] = None):
        """
        Inizializza l'executor
        
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
    
    def get_pending_actions(self, campaign_id: Optional[int] = None) -> List[ProposedAction]:
        """
        Ottiene azioni in attesa di approvazione
        
        Args:
            campaign_id: Se specificato, filtra per campagna
        
        Returns:
            Lista di azioni APPROVED non ancora eseguite
        """
        with get_db_session() as db:
            query = db.query(ProposedAction).filter(
                ProposedAction.status == 'APPROVED'
            )
            
            if campaign_id:
                query = query.filter(ProposedAction.campaign_id == campaign_id)
            
            actions = query.order_by(
                ProposedAction.priority.desc(),
                ProposedAction.created_at.asc()
            ).all()
            
            return actions
    
    def execute_pause_ad(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Pausa un annuncio specifico
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        logger.info(f"⏸️  Pausa annuncio per campagna {action.campaign_id}")
        
        target = action.target or {}
        ad_group_id = target.get('ad_group_id')
        ad_id = target.get('ad_id')
        
        if not ad_group_id or not ad_id:
            logger.warning("⚠️  ID annuncio non specificato, skip esecuzione")
            return {
                'status': 'SKIPPED',
                'reason': 'Missing ad_group_id or ad_id in target'
            }
        
        try:
            ad_group_ad_service = self.client.get_service("AdGroupAdService")
            
            # Resource name dell'annuncio
            ad_resource_name = ad_group_ad_service.ad_group_ad_path(
                self.customer_id, ad_group_id, ad_id
            )
            
            # Crea operazione
            ad_group_ad_operation = self.client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_group_ad_operation.update
            ad_group_ad.resource_name = ad_resource_name
            ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED
            
            # Update mask
            self.client.copy_from(
                ad_group_ad_operation.update_mask,
                protobuf_helpers.field_mask(None, ad_group_ad._pb)
            )
            
            # Esegui mutazione
            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[ad_group_ad_operation]
            )
            
            result = response.results[0]
            
            logger.info(f"✅ Annuncio pausato: {result.resource_name}")
            
            return {
                'status': 'SUCCESS',
                'resource_name': result.resource_name,
                'ad_group_id': ad_group_id,
                'ad_id': ad_id
            }
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            error_messages = [error.message for error in ex.failure.errors]
            return {
                'status': 'FAILED',
                'error': str(ex),
                'error_messages': error_messages
            }
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def execute_pause_keyword(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Pausa una keyword specifica
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        logger.info(f"⏸️  Pausa keyword per campagna {action.campaign_id}")
        
        target = action.target or {}
        ad_group_id = target.get('ad_group_id')
        criterion_id = target.get('criterion_id')
        
        if not ad_group_id or not criterion_id:
            logger.warning("⚠️  ID keyword non specificato, skip esecuzione")
            return {
                'status': 'SKIPPED',
                'reason': 'Missing ad_group_id or criterion_id in target'
            }
        
        try:
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            
            # Resource name
            criterion_resource_name = ad_group_criterion_service.ad_group_criterion_path(
                self.customer_id, ad_group_id, criterion_id
            )
            
            # Crea operazione
            operation = self.client.get_type("AdGroupCriterionOperation")
            criterion = operation.update
            criterion.resource_name = criterion_resource_name
            criterion.status = self.client.enums.AdGroupCriterionStatusEnum.PAUSED
            
            # Update mask
            self.client.copy_from(
                operation.update_mask,
                protobuf_helpers.field_mask(None, criterion._pb)
            )
            
            # Esegui
            response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id,
                operations=[operation]
            )
            
            result = response.results[0]
            
            logger.info(f"✅ Keyword pausata: {result.resource_name}")
            
            return {
                'status': 'SUCCESS',
                'resource_name': result.resource_name,
                'ad_group_id': ad_group_id,
                'criterion_id': criterion_id
            }
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            error_messages = [error.message for error in ex.failure.errors]
            return {
                'status': 'FAILED',
                'error': str(ex),
                'error_messages': error_messages
            }
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def execute_add_negative_keyword(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Aggiunge negative keywords a livello campagna
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        logger.info(f"➕ Aggiungi negative keywords per campagna {action.campaign_id}")
        
        target = action.target or {}
        keywords = target.get('keywords', [])
        match_type = target.get('match_type', 'PHRASE')  # EXACT, PHRASE, BROAD
        
        if not keywords:
            logger.warning("⚠️  Nessuna keyword specificata, skip esecuzione")
            return {
                'status': 'SKIPPED',
                'reason': 'No keywords specified in target'
            }
        
        try:
            campaign_criterion_service = self.client.get_service("CampaignCriterionService")
            
            operations = []
            
            for keyword in keywords:
                # Crea operazione per ogni negative keyword
                operation = self.client.get_type("CampaignCriterionOperation")
                criterion = operation.create
                
                criterion.campaign = self.client.get_service("CampaignService").campaign_path(
                    self.customer_id, action.campaign_id
                )
                
                criterion.negative = True
                criterion.keyword.text = keyword
                criterion.keyword.match_type = getattr(
                    self.client.enums.KeywordMatchTypeEnum,
                    match_type
                )
                
                operations.append(operation)
            
            # Esegui batch di operazioni
            response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=self.customer_id,
                operations=operations
            )
            
            added_keywords = [result.resource_name for result in response.results]
            
            logger.info(f"✅ Aggiunte {len(added_keywords)} negative keywords")
            
            return {
                'status': 'SUCCESS',
                'keywords_added': len(added_keywords),
                'keywords': keywords,
                'resource_names': added_keywords
            }
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            error_messages = [error.message for error in ex.failure.errors]
            return {
                'status': 'FAILED',
                'error': str(ex),
                'error_messages': error_messages
            }
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def execute_change_bid(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Modifica bid di una keyword o ad group
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        action_type = action.action_type  # REDUCE_BID o INCREASE_BID
        
        logger.info(f"💰 {action_type} per campagna {action.campaign_id}")
        
        target = action.target or {}
        ad_group_id = target.get('ad_group_id')
        criterion_id = target.get('criterion_id')
        new_bid_micros = target.get('new_bid_micros')
        
        if not ad_group_id or not criterion_id or not new_bid_micros:
            logger.warning("⚠️  Parametri bid non completi, skip esecuzione")
            return {
                'status': 'SKIPPED',
                'reason': 'Missing bid parameters in target'
            }
        
        try:
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            
            # Resource name
            criterion_resource_name = ad_group_criterion_service.ad_group_criterion_path(
                self.customer_id, ad_group_id, criterion_id
            )
            
            # Crea operazione
            operation = self.client.get_type("AdGroupCriterionOperation")
            criterion = operation.update
            criterion.resource_name = criterion_resource_name
            criterion.cpc_bid_micros = new_bid_micros
            
            # Update mask
            self.client.copy_from(
                operation.update_mask,
                protobuf_helpers.field_mask(None, criterion._pb)
            )
            
            # Esegui
            response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id,
                operations=[operation]
            )
            
            result = response.results[0]
            
            logger.info(f"✅ Bid modificata: {result.resource_name}")
            
            return {
                'status': 'SUCCESS',
                'resource_name': result.resource_name,
                'new_bid_euros': new_bid_micros / 1_000_000
            }
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            error_messages = [error.message for error in ex.failure.errors]
            return {
                'status': 'FAILED',
                'error': str(ex),
                'error_messages': error_messages
            }
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def execute_change_budget(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Modifica budget giornaliero campagna
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        action_type = action.action_type  # INCREASE_BUDGET o DECREASE_BUDGET
        
        logger.info(f"💵 {action_type} per campagna {action.campaign_id}")
        
        target = action.target or {}
        new_budget_micros = target.get('new_budget_micros')
        
        if not new_budget_micros:
            logger.warning("⚠️  Nuovo budget non specificato, skip esecuzione")
            return {
                'status': 'SKIPPED',
                'reason': 'Missing new_budget_micros in target'
            }
        
        try:
            # Prima ottieni l'ID del budget dalla campagna
            campaign_service = self.client.get_service("CampaignService")
            
            query = f"""
                SELECT 
                    campaign.campaign_budget
                FROM campaign
                WHERE campaign.id = {action.campaign_id}
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            campaign_budget_resource_name = None
            for row in response:
                campaign_budget_resource_name = row.campaign.campaign_budget
                break
            
            if not campaign_budget_resource_name:
                return {
                    'status': 'FAILED',
                    'error': 'Campaign budget not found'
                }
            
            # Modifica il budget
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            
            operation = self.client.get_type("CampaignBudgetOperation")
            budget = operation.update
            budget.resource_name = campaign_budget_resource_name
            budget.amount_micros = new_budget_micros
            
            # Update mask
            self.client.copy_from(
                operation.update_mask,
                protobuf_helpers.field_mask(None, budget._pb)
            )
            
            # Esegui
            response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[operation]
            )
            
            result = response.results[0]
            
            logger.info(f"✅ Budget modificato: {result.resource_name}")
            
            return {
                'status': 'SUCCESS',
                'resource_name': result.resource_name,
                'new_budget_euros': new_budget_micros / 1_000_000
            }
            
        except GoogleAdsException as ex:
            logger.error(f"❌ Errore Google Ads API: {ex}")
            error_messages = [error.message for error in ex.failure.errors]
            return {
                'status': 'FAILED',
                'error': str(ex),
                'error_messages': error_messages
            }
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def execute_action(self, action: ProposedAction) -> Dict[str, Any]:
        """
        Esegue un'azione specifica
        
        Args:
            action: Azione da eseguire
        
        Returns:
            Risultato esecuzione
        """
        logger.info(f"🔧 Esecuzione azione: {action.action_type} (ID: {action.id})")
        
        # Dispatch in base al tipo di azione
        action_handlers = {
            'PAUSE_AD': self.execute_pause_ad,
            'PAUSE_KEYWORD': self.execute_pause_keyword,
            'ADD_NEGATIVE_KEYWORD': self.execute_add_negative_keyword,
            'REDUCE_BID': self.execute_change_bid,
            'INCREASE_BID': self.execute_change_bid,
            'INCREASE_BUDGET': self.execute_change_budget,
            'DECREASE_BUDGET': self.execute_change_budget,
        }
        
        handler = action_handlers.get(action.action_type)
        
        if not handler:
            logger.warning(f"⚠️  Tipo azione '{action.action_type}' non supportato ancora")
            return {
                'status': 'NOT_IMPLEMENTED',
                'reason': f"Action type '{action.action_type}' not yet implemented"
            }
        
        try:
            result = handler(action)
            return result
        except Exception as e:
            logger.error(f"❌ Errore esecuzione azione: {e}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def save_execution_log(
        self,
        action: ProposedAction,
        result: Dict[str, Any]
    ) -> None:
        """
        Salva il log dell'esecuzione
        
        Args:
            action: Azione eseguita
            result: Risultato esecuzione
        """
        with get_db_session() as db:
            # Crea log
            log = ActionLog(
                action_id=action.id,
                campaign_id=action.campaign_id,
                action_type=action.action_type,
                details={
                    'target': action.target,
                    'reason': action.reason,
                    'expected_impact': action.expected_impact
                },
                status=result['status'],
                error_message=result.get('error'),
                api_response=result
            )
            
            db.add(log)
            
            # Aggiorna stato azione
            action.status = 'EXECUTED' if result['status'] == 'SUCCESS' else 'FAILED'
            action.executed_at = datetime.now()
            action.execution_result = result
            action.execution_error = result.get('error')
            
            db.commit()
    
    def execute_pending_actions(
        self,
        campaign_id: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Esegue tutte le azioni approvate
        
        Args:
            campaign_id: Se specificato, esegue solo per questa campagna
            dry_run: Se True, simula senza eseguire realmente
        
        Returns:
            Risultati esecuzione
        """
        logger.info("=" * 80)
        logger.info("🚀 INIZIO ESECUZIONE AZIONI")
        if dry_run:
            logger.info("   [DRY RUN MODE - Nessuna modifica reale]")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # Ottieni azioni da eseguire
        actions = self.get_pending_actions(campaign_id)
        
        if not actions:
            logger.info("ℹ️  Nessuna azione da eseguire")
            return {
                'status': 'SUCCESS',
                'actions_executed': 0,
                'message': 'No pending actions'
            }
        
        logger.info(f"📋 Trovate {len(actions)} azioni da eseguire")
        
        results = []
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for action in actions:
            logger.info(f"\n{'─' * 80}")
            logger.info(f"Azione {action.id}: {action.action_type}")
            logger.info(f"Campagna: {action.campaign_id}")
            logger.info(f"Priorità: {action.priority}")
            logger.info(f"Reason: {action.reason}")
            
            if dry_run:
                logger.info("🔍 DRY RUN: Skip esecuzione")
                result = {
                    'status': 'DRY_RUN',
                    'message': 'Execution skipped in dry run mode'
                }
            else:
                # Esegui azione
                result = self.execute_action(action)
                
                # Salva log
                self.save_execution_log(action, result)
            
            # Contatori
            if result['status'] == 'SUCCESS':
                success_count += 1
            elif result['status'] in ['SKIPPED', 'NOT_IMPLEMENTED', 'DRY_RUN']:
                skipped_count += 1
            else:
                failed_count += 1
            
            results.append({
                'action_id': action.id,
                'action_type': action.action_type,
                'campaign_id': action.campaign_id,
                'result': result
            })
        
        duration = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'status': 'SUCCESS',
            'total_actions': len(actions),
            'success_count': success_count,
            'failed_count': failed_count,
            'skipped_count': skipped_count,
            'duration_seconds': duration,
            'dry_run': dry_run,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("=" * 80)
        logger.info(f"✅ ESECUZIONE COMPLETATA in {duration:.2f}s")
        logger.info(f"   - Successo: {success_count}")
        logger.info(f"   - Fallite: {failed_count}")
        logger.info(f"   - Skippate: {skipped_count}")
        logger.info("=" * 80)
        
        return summary


# Test standalone
if __name__ == "__main__":
    import sys
    
    print("🧪 Test Agente Executor\n")
    
    executor = CampaignExecutor()
    
    # Parse args
    dry_run = "--dry-run" in sys.argv
    campaign_id = None
    
    for arg in sys.argv[1:]:
        if arg.startswith("--campaign="):
            campaign_id = int(arg.split("=")[1])
    
    # Esegui
    result = executor.execute_pending_actions(
        campaign_id=campaign_id,
        dry_run=dry_run
    )
    
    print("\n📊 RISULTATI:")
    print(json.dumps({
        'total_actions': result['total_actions'],
        'success_count': result['success_count'],
        'failed_count': result['failed_count'],
        'skipped_count': result['skipped_count'],
        'duration_seconds': result['duration_seconds']
    }, indent=2))

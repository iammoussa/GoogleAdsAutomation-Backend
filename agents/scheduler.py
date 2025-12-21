"""
SCHEDULER - Orchestratore degli agenti
Coordina Monitor → Analyzer → Executor in modo automatico
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Optional
import signal
import sys

from sqlalchemy import text

from agents.monitor import CampaignMonitor
from agents.analyzer import CampaignAnalyzer
from agents.executor import CampaignExecutor
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentScheduler:
    """Scheduler per coordinare tutti gli agenti"""
    
    def __init__(self):
        """Inizializza lo scheduler"""
        self.scheduler = BlockingScheduler()
        self.monitor = CampaignMonitor()
        self.analyzer = CampaignAnalyzer()
        self.executor = CampaignExecutor()
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        
        logger.info("✅ Scheduler inizializzato")
    
    def _shutdown_handler(self, signum, frame):
        """Handler per shutdown graceful"""
        logger.info("🛑 Ricevuto segnale di shutdown, arresto scheduler...")
        self.scheduler.shutdown(wait=False)
        sys.exit(0)
    
    def run_monitoring_cycle(self):
        """
        Esegue un ciclo completo di monitoring
        Monitor → (opzionale) Analyzer
        """
        try:
            logger.info("\n" + "=" * 100)
            logger.info("🔄 INIZIO CICLO MONITORING")
            logger.info("=" * 100)
            
            # 1. Monitor: Estrai metriche e rileva anomalie
            monitor_result = self.monitor.run()
            
            # 2. Se ci sono alert e analyzer è auto, esegui analisi
            if monitor_result.get('alerts_count', 0) > 0 and settings.ANALYZER_AUTO_RUN:
                logger.info("\n⚠️  Rilevati alert → Avvio Analyzer automatico")
                
                analyzer_results = self.analyzer.analyze_all_campaigns()
                total_actions = sum(len(r.get('actions', [])) for r in analyzer_results)
                logger.info(f"... {total_actions} actions proposed")
            else:
                logger.info("\n✅ Nessun alert o Analyzer disabilitato, skip analisi")
            
            logger.info("=" * 100)
            logger.info("✅ CICLO MONITORING COMPLETATO")
            logger.info("=" * 100 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Errore durante ciclo monitoring: {e}", exc_info=True)
    
    def run_analyzer_cycle(self):
        """
        Esegue un ciclo di analisi
        (Può essere schedulato indipendentemente dal monitor)
        """
        try:
            logger.info("\n" + "=" * 100)
            logger.info("🧠 INIZIO CICLO ANALYZER")
            logger.info("=" * 100)
            
            result = self.analyzer.analyze_all_campaigns()
            
            logger.info("=" * 100)
            logger.info(f"✅ CICLO ANALYZER COMPLETATO: {result['total_actions_proposed']} azioni proposte")
            logger.info("=" * 100 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Errore durante ciclo analyzer: {e}", exc_info=True)
    
    def run_executor_cycle(self, dry_run: bool = False):
        """
        Esegue un ciclo di esecuzione
        Applica le azioni APPROVED
        
        Args:
            dry_run: Se True, simula senza eseguire
        """
        try:
            logger.info("\n" + "=" * 100)
            logger.info("⚙️  INIZIO CICLO EXECUTOR")
            if dry_run:
                logger.info("   [DRY RUN MODE]")
            logger.info("=" * 100)
            
            result = self.executor.execute_pending_actions(dry_run=dry_run)
            
            logger.info("=" * 100)
            logger.info(f"✅ CICLO EXECUTOR COMPLETATO: {result['success_count']} azioni eseguite")
            logger.info("=" * 100 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Errore durante ciclo executor: {e}", exc_info=True)
    
    def setup_jobs(self):
        """
        Configura i job schedulati
        """
        logger.info("📅 Setup job schedulati...")
        
        # JOB 1: Monitor (ogni N ore configurabili)
        self.scheduler.add_job(
            func=self.run_monitoring_cycle,
            trigger=IntervalTrigger(hours=settings.MONITOR_INTERVAL_HOURS),
            id='monitor_cycle',
            name='Monitor Campagne',
            replace_existing=True,
            next_run_time=datetime.now()  # Esegui subito all'avvio
        )
        logger.info(f"  ✅ Monitor: ogni {settings.MONITOR_INTERVAL_HOURS}h")
        
        # JOB 2: Analyzer (opzionale, manuale via dashboard)
        # Se vuoi analyzer automatico ogni giorno alle 9:00
        # self.scheduler.add_job(
        #     func=self.run_analyzer_cycle,
        #     trigger=CronTrigger(hour=9, minute=0),
        #     id='analyzer_cycle',
        #     name='Analyzer Giornaliero',
        #     replace_existing=True
        # )
        # logger.info("  ✅ Analyzer: ogni giorno alle 9:00")
        
        # JOB 3: Executor (MANUALE - solo via dashboard per sicurezza)
        # NON schedulato automaticamente
        logger.info("  ℹ️  Executor: solo manuale (via dashboard)")
        
        # JOB 4: Health check (ogni ora)
        self.scheduler.add_job(
            func=self._health_check,
            trigger=IntervalTrigger(hours=1),
            id='health_check',
            name='Health Check',
            replace_existing=True
        )
        logger.info("  ✅ Health Check: ogni 1h")
        
        logger.info("✅ Job configurati")
    
    def _health_check(self):
        """
        Verifica che tutto funzioni correttamente
        """
        try:
            # Verifica connessione database
            from database.database import get_db_session
            with get_db_session() as db:
                db.execute(text("SELECT 1"))
        
            logger.info("💚 Health Check OK - Sistema operativo")
            
        except Exception as e:
            logger.error(f"❌ Health Check FAILED: {e}")
    
    def start(self):
        """
        Avvia lo scheduler
        """
        logger.info("\n" + "=" * 100)
        logger.info("🚀 AVVIO SCHEDULER")
        logger.info("=" * 100)
        logger.info(f"📍 Customer ID: {settings.GOOGLE_ADS_CUSTOMER_ID}")
        logger.info(f"⏱️  Monitor interval: {settings.MONITOR_INTERVAL_HOURS}h")
        logger.info(f"🤖 Analyzer auto: {settings.ANALYZER_AUTO_RUN}")
        logger.info("=" * 100 + "\n")
        
        # Setup jobs
        self.setup_jobs()
        
        # Mostra jobs schedulati
        logger.info("\n📋 Job Attivi:")
        for job in self.scheduler.get_jobs():
            try:
                next_run = str(job.next_fire_time) if hasattr(job, 'next_fire_time') and job.next_fire_time else "N/A"
            except:
                next_run = "N/A"
            logger.info(f"  - {job.id}: next execution {next_run}")
        
        logger.info("\n✅ Scheduler in esecuzione... (Ctrl+C per fermare)\n")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n🛑 Scheduler arrestato")


# Entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Ads Campaign Automation Scheduler")
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Esegui un solo ciclo e termina'
    )
    parser.add_argument(
        '--monitor-only',
        action='store_true',
        help='Esegui solo monitor (no scheduler)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Esegui solo analyzer (no scheduler)'
    )
    parser.add_argument(
        '--execute-only',
        action='store_true',
        help='Esegui solo executor (no scheduler)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Esegui in dry-run mode (solo per executor)'
    )
    
    args = parser.parse_args()
    
    scheduler = AgentScheduler()
    
    # Modalità run-once (per testing)
    if args.monitor_only:
        logger.info("🔍 Modalità: MONITOR ONLY")
        scheduler.run_monitoring_cycle()
        
    elif args.analyze_only:
        logger.info("🧠 Modalità: ANALYZER ONLY")
        scheduler.run_analyzer_cycle()
        
    elif args.execute_only:
        logger.info("⚙️  Modalità: EXECUTOR ONLY")
        scheduler.run_executor_cycle(dry_run=args.dry_run)
        
    elif args.run_once:
        logger.info("🔄 Modalità: RUN ONCE")
        scheduler.run_monitoring_cycle()
        
    else:
        # Modalità normale: scheduler continuo
        scheduler.start()

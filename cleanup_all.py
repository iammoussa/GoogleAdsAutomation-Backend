#!/usr/bin/env python
"""
Script per pulire TUTTE le ottimizzazioni e i loro log dal database
"""

from database.database import get_db_session
from database.models import ProposedAction, ActionLog
from utils.logger import get_logger

logger = get_logger(__name__)

def cleanup_all_optimizations_and_logs():
    """Rimuove TUTTE le ottimizzazioni E i loro log (gestisce foreign keys)"""
    try:
        with get_db_session() as db:
            # Conta quante ne cancelleremo
            actions_count = db.query(ProposedAction).count()
            logs_count = db.query(ActionLog).count()
            
            logger.info(f"🗑️  Trovate {actions_count} ottimizzazioni TOTALI da rimuovere")
            logger.info(f"🗑️  Trovati {logs_count} log da rimuovere")
            
            if actions_count == 0 and logs_count == 0:
                logger.info("✅ Nessuna ottimizzazione o log da rimuovere")
                return
            
            # Mostra breakdown per status
            if actions_count > 0:
                pending = db.query(ProposedAction).filter(ProposedAction.status == 'PENDING').count()
                applied = db.query(ProposedAction).filter(ProposedAction.status == 'APPLIED').count()
                dismissed = db.query(ProposedAction).filter(ProposedAction.status == 'DISMISSED').count()
                failed = db.query(ProposedAction).filter(ProposedAction.status == 'FAILED').count()
                
                logger.info(f"   Breakdown ottimizzazioni:")
                logger.info(f"   - PENDING: {pending}")
                logger.info(f"   - APPLIED: {applied}")
                logger.info(f"   - DISMISSED: {dismissed}")
                logger.info(f"   - FAILED: {failed}")
            
            # IMPORTANTE: Cancella prima i log (foreign key), poi le azioni
            logger.info("🔄 Step 1: Cancellazione action_logs...")
            deleted_logs = db.query(ActionLog).delete()
            logger.success(f"✅ Rimossi {deleted_logs} log")
            
            logger.info("🔄 Step 2: Cancellazione proposed_actions...")
            deleted_actions = db.query(ProposedAction).delete()
            logger.success(f"✅ Rimosse {deleted_actions} ottimizzazioni")
            
            db.commit()
            
            logger.success(f"🧹 Database completamente pulito!")
            logger.success(f"   - {deleted_logs} log rimossi")
            logger.success(f"   - {deleted_actions} ottimizzazioni rimosse")
            
    except Exception as e:
        logger.error(f"❌ Errore durante cleanup: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    # Conferma prima di procedere
    print("⚠️  ATTENZIONE: Questo cancellerà:")
    print("   1. TUTTI i log di esecuzione (action_logs)")
    print("   2. TUTTE le ottimizzazioni (proposed_actions)")
    print("      - PENDING")
    print("      - APPLIED")
    print("      - DISMISSED")
    print("      - FAILED")
    print()
    response = input("Sei sicuro? Digita 'yes' per confermare: ")
    
    if response.lower() == 'yes':
        cleanup_all_optimizations_and_logs()
        print("\n✅ Fatto! Ora puoi rigenerare con: python agents/analyzer.py --all")
    else:
        print("❌ Operazione annullata")
        sys.exit(0)
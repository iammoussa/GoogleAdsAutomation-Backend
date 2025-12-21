#!/usr/bin/env python
"""
Migration script: Add extended metrics columns to campaign_metrics table
"""

from database.database import engine
from sqlalchemy import text
from utils.logger import get_logger

logger = get_logger(__name__)

def add_extended_metrics():
    """Add extended metrics columns to campaign_metrics table"""
    
    extended_columns = [
        ('conversion_rate', 'NUMERIC(5, 2) DEFAULT 0'),
        ('cost_per_action', 'NUMERIC(10, 2) DEFAULT 0'),
        ('viewable_impressions', 'INTEGER DEFAULT 0'),
        ('viewable_ctr', 'NUMERIC(5, 2) DEFAULT 0'),
        ('all_conversions', 'NUMERIC(10, 2) DEFAULT 0'),
        ('all_conversion_value', 'NUMERIC(10, 2) DEFAULT 0'),
        ('interactions', 'INTEGER DEFAULT 0'),
        ('interaction_rate', 'NUMERIC(5, 2) DEFAULT 0'),
        ('engagements', 'INTEGER DEFAULT 0'),
        ('engagement_rate', 'NUMERIC(5, 2) DEFAULT 0'),
        ('search_impression_share', 'NUMERIC(5, 2) DEFAULT 0'),
        ('search_top_impression_share', 'NUMERIC(5, 2) DEFAULT 0'),
    ]
    
    try:
        with engine.connect() as conn:
            logger.info("🔍 Checking existing columns in campaign_metrics...")
            
            # Get existing columns
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='campaign_metrics';
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            logger.info(f"✓ Found {len(existing_columns)} existing columns")
            
            columns_added = 0
            columns_skipped = 0
            
            for col_name, col_type in extended_columns:
                if col_name in existing_columns:
                    logger.info(f"  ✓ {col_name} already exists")
                    columns_skipped += 1
                else:
                    logger.info(f"  🔄 Adding {col_name}...")
                    conn.execute(text(f"""
                        ALTER TABLE campaign_metrics 
                        ADD COLUMN {col_name} {col_type};
                    """))
                    logger.success(f"  ✅ Added {col_name}")
                    columns_added += 1
            
            if columns_added > 0:
                conn.commit()
                logger.success(f"✅ Migration completed! Added {columns_added} columns")
            else:
                logger.info("✅ All columns already exist, no changes needed")
            
            if columns_skipped > 0:
                logger.info(f"ℹ️  Skipped {columns_skipped} existing columns")
            
            logger.info("💡 You can now run: python agents/analyzer.py --all")
            
    except Exception as e:
        logger.error(f"❌ Error adding columns: {e}")
        raise

if __name__ == "__main__":
    print("="*70)
    print("Migration: Add Extended Metrics to campaign_metrics")
    print("="*70)
    print()
    print("This will add the following columns:")
    print("  - conversion_rate")
    print("  - cost_per_action (CPA)")
    print("  - viewable_impressions")
    print("  - viewable_ctr")
    print("  - all_conversions")
    print("  - all_conversion_value")
    print("  - interactions")
    print("  - interaction_rate")
    print("  - engagements")
    print("  - engagement_rate")
    print("  - search_impression_share")
    print("  - search_top_impression_share")
    print()
    
    response = input("Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        add_extended_metrics()
        print()
        print("="*70)
        print("Migration completed!")
        print("="*70)
    else:
        print("❌ Migration cancelled")
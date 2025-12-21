#!/usr/bin/env python
"""
Migration script: Add current_value and proposed_value to proposed_actions table
"""

from database.database import engine
from sqlalchemy import text
from utils.logger import get_logger

logger = get_logger(__name__)

def add_value_columns():
    """Add current_value and proposed_value columns to proposed_actions table"""
    try:
        with engine.connect() as conn:
            # Check campaign_name
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='proposed_actions' 
                AND column_name='campaign_name';
            """))
            
            if not result.fetchone():
                logger.info("🔄 Adding 'campaign_name' column...")
                conn.execute(text("ALTER TABLE proposed_actions ADD COLUMN campaign_name VARCHAR(255);"))
                logger.success("✅ Added campaign_name")
            else:
                logger.info("✓ campaign_name already exists")
            
            # Check current_value
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='proposed_actions' 
                AND column_name='current_value';
            """))
            
            if not result.fetchone():
                logger.info("🔄 Adding 'current_value' column...")
                conn.execute(text("ALTER TABLE proposed_actions ADD COLUMN current_value VARCHAR(100);"))
                logger.success("✅ Added current_value")
            else:
                logger.info("✓ current_value already exists")
            
            # Check proposed_value
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='proposed_actions' 
                AND column_name='proposed_value';
            """))
            
            if not result.fetchone():
                logger.info("🔄 Adding 'proposed_value' column...")
                conn.execute(text("ALTER TABLE proposed_actions ADD COLUMN proposed_value VARCHAR(100);"))
                logger.success("✅ Added proposed_value")
            else:
                logger.info("✓ proposed_value already exists")
            
            conn.commit()
            
            logger.success("✅ All columns added successfully!")
            logger.info("💡 You can now run: python agents/analyzer.py --all")
            
    except Exception as e:
        logger.error(f"❌ Error adding columns: {e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("Migration: Add value columns to proposed_actions")
    print("="*60)
    print()
    
    add_value_columns()
    
    print()
    print("="*60)
    print("Migration completed!")
    print("="*60)
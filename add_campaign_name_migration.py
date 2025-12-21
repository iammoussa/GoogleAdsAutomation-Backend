#!/usr/bin/env python
"""
Migration script: Add campaign_name column to proposed_actions table
"""

from database.database import engine
from sqlalchemy import text
from utils.logger import get_logger

logger = get_logger(__name__)

def add_campaign_name_column():
    """Add campaign_name column to proposed_actions table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='proposed_actions' 
                AND column_name='campaign_name';
            """))
            
            if result.fetchone():
                logger.warning("⚠️ Column 'campaign_name' already exists in 'proposed_actions' table")
                return
            
            logger.info("🔄 Adding 'campaign_name' column to 'proposed_actions' table...")
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE proposed_actions 
                ADD COLUMN campaign_name VARCHAR(255);
            """))
            
            conn.commit()
            
            logger.success("✅ Column 'campaign_name' added successfully!")
            logger.info("💡 You can now run: python agents/analyzer.py --all")
            
    except Exception as e:
        logger.error(f"❌ Error adding column: {e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("Migration: Add campaign_name to proposed_actions")
    print("="*60)
    print()
    
    add_campaign_name_column()
    
    print()
    print("="*60)
    print("Migration completed!")
    print("="*60)
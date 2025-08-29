#!/usr/bin/env python3
"""
Script to update database schema for media message support
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def update_database_schema():
    """Update database schema to support media messages"""
    try:
        from database.db import db
        
        print("Updating database schema for media support...")
        
        # Check if columns already exist
        check_query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'pyctalk' 
        AND TABLE_NAME = 'private_messages' 
        AND COLUMN_NAME IN ('message_type', 'file_path', 'file_name', 'file_size', 'mime_type', 'thumbnail_path')
        """
        
        existing_columns = await db.fetch_all(check_query)
        existing_column_names = [row['COLUMN_NAME'] for row in existing_columns]
        
        print(f"Existing media columns: {existing_column_names}")
        
        # Add columns that don't exist
        columns_to_add = [
            ("message_type", "ENUM('text', 'image', 'file', 'audio', 'video') DEFAULT 'text'"),
            ("file_path", "VARCHAR(500) NULL"),
            ("file_name", "VARCHAR(255) NULL"),
            ("file_size", "BIGINT NULL"),
            ("mime_type", "VARCHAR(100) NULL"),
            ("thumbnail_path", "VARCHAR(500) NULL")
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in existing_column_names:
                try:
                    alter_query = f"ALTER TABLE private_messages ADD COLUMN {column_name} {column_def}"
                    await db.execute(alter_query)
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Failed to add column {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Do the same for group_messages table
        print("\nUpdating group_messages table...")
        
        check_group_query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'pyctalk' 
        AND TABLE_NAME = 'group_messages' 
        AND COLUMN_NAME IN ('message_type', 'file_path', 'file_name', 'file_size', 'mime_type', 'thumbnail_path')
        """
        
        existing_group_columns = await db.fetch_all(check_group_query)
        existing_group_column_names = [row['COLUMN_NAME'] for row in existing_group_columns]
        
        print(f"Existing group media columns: {existing_group_column_names}")
        
        for column_name, column_def in columns_to_add:
            if column_name not in existing_group_column_names:
                try:
                    alter_query = f"ALTER TABLE group_messages ADD COLUMN {column_name} {column_def}"
                    await db.execute(alter_query)
                    print(f"✅ Added column to group_messages: {column_name}")
                except Exception as e:
                    print(f"❌ Failed to add column {column_name} to group_messages: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists in group_messages")
        
        print("\n🎉 Database schema update completed!")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_database_schema())

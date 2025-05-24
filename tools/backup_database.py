#!/usr/bin/env python
"""
Database Backup Script for College Management System

This script creates a backup of the database and records it in the DatabaseBackup model.
It can be run as a standalone script or imported and used programmatically.

Usage:
    python backup_database.py [--manual] [--notes "Backup notes"]
    
Options:
    --manual     Marks the backup as manually triggered (default is automatic)
    --notes      Additional notes about the backup
"""

import os
import sys
import datetime
import argparse
import shutil
import django

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from reporting.models import DatabaseBackup


def create_backup(is_automatic=True, notes=None, user=None):
    """
    Create a database backup and record it in the DatabaseBackup model.
    
    Args:
        is_automatic (bool): Whether the backup was triggered automatically
        notes (str): Additional notes about the backup
        user (User): The user who initiated the backup (for manual backups)
        
    Returns:
        DatabaseBackup: The created backup record
    """
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(project_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"db_backup_{timestamp}.sqlite3"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Get database path from settings
        db_path = settings.DATABASES['default'].get('NAME')
        
        if 'sqlite3' in db_path:
            # For SQLite, just copy the file
            shutil.copy2(db_path, backup_path)
            backup_size = os.path.getsize(backup_path)
            status = 'success'
        else:
            # For PostgreSQL or MySQL, use Django dumpdata
            # This is a simplified version; in production use pg_dump or mysqldump
            from django.core.management import call_command
            json_path = backup_path.replace('.sqlite3', '.json')
            with open(json_path, 'w') as f:
                call_command('dumpdata', stdout=f)
            backup_size = os.path.getsize(json_path)
            backup_path = json_path
            status = 'success'
        
        # Record the backup in the database
        backup_record = DatabaseBackup.objects.create(
            backup_file=backup_path,
            backup_date=timezone.now(),
            backup_size=backup_size,
            created_by=user,
            is_automatic=is_automatic,
            status=status,
            notes=notes
        )
        
        print(f"Backup created successfully: {backup_path}")
        print(f"Backup size: {backup_size} bytes")
        
        # Remove old backups (keep only last 10)
        old_backups = DatabaseBackup.objects.order_by('-backup_date')[10:]
        for old_backup in old_backups:
            if os.path.exists(old_backup.backup_file):
                try:
                    os.remove(old_backup.backup_file)
                    print(f"Removed old backup: {old_backup.backup_file}")
                except Exception as e:
                    print(f"Error removing old backup {old_backup.backup_file}: {str(e)}")
        
        return backup_record
        
    except Exception as e:
        error_message = f"Backup failed: {str(e)}"
        print(error_message)
        
        # Record the failed backup attempt
        backup_record = DatabaseBackup.objects.create(
            backup_file='',
            backup_date=timezone.now(),
            backup_size=0,
            created_by=user,
            is_automatic=is_automatic,
            status='failed',
            notes=notes + f" - Error: {str(e)}" if notes else f"Error: {str(e)}"
        )
        return backup_record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create database backup for College Management System')
    parser.add_argument('--manual', action='store_true', help='Mark as manual backup (default: automatic)')
    parser.add_argument('--notes', type=str, help='Additional notes about the backup', default='')
    parser.add_argument('--user', type=int, help='User ID who initiated the backup (for manual backups)', default=None)
    
    args = parser.parse_args()
    
    user_obj = None
    if args.user:
        try:
            user_obj = User.objects.get(id=args.user)
        except User.DoesNotExist:
            print(f"User with ID {args.user} does not exist.")
    
    create_backup(
        is_automatic=not args.manual, 
        notes=args.notes,
        user=user_obj
    )

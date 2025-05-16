#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/event_booking"
MYSQL_USER="app_user"
MYSQL_PASSWORD="app_password"
MYSQL_DATABASE="event_booking"
MYSQL_HOST="localhost"
MYSQL_PORT="3309"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Create backup
echo "Starting backup of $MYSQL_DATABASE..."
mysqldump --host=$MYSQL_HOST --port=$MYSQL_PORT \
          --user=$MYSQL_USER --password=$MYSQL_PASSWORD \
          --single-transaction --quick --lock-tables=false \
          $MYSQL_DATABASE | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    
    # Create symlink to latest backup
    ln -sf $BACKUP_FILE $BACKUP_DIR/latest_backup.sql.gz
    
    # Remove old backups
    find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "Backup size: $BACKUP_SIZE"
    
    # List remaining backups
    echo "Current backups:"
    ls -lh $BACKUP_DIR
else
    echo "Backup failed!"
    rm -f $BACKUP_FILE
    exit 1
fi 
#!/bin/bash

# Configuration
MYSQL_USER="app_user"
MYSQL_PASSWORD="app_password"
MYSQL_DATABASE="event_booking"
MYSQL_HOST="localhost"
MYSQL_PORT="3309"
BACKUP_DIR="/var/backups/event_booking"

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -f, --file FILENAME    Specify backup file to restore"
    echo "  -l, --latest          Restore from latest backup"
    echo "  -h, --help            Display this help message"
    exit 1
}

# Parse command line arguments
BACKUP_FILE=""
USE_LATEST=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        -l|--latest)
            USE_LATEST=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Check if we should use latest backup
if [ $USE_LATEST -eq 1 ]; then
    BACKUP_FILE="$BACKUP_DIR/latest_backup.sql.gz"
fi

# Validate backup file
if [ -z "$BACKUP_FILE" ]; then
    echo "Error: No backup file specified"
    usage
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirm restore
echo "WARNING: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Stop the API service
echo "Stopping API service..."
docker-compose stop api

# Restore database
echo "Starting database restore..."
if [[ $BACKUP_FILE == *.gz ]]; then
    # Gunzip and restore
    gunzip < "$BACKUP_FILE" | mysql --host=$MYSQL_HOST --port=$MYSQL_PORT \
                                   --user=$MYSQL_USER --password=$MYSQL_PASSWORD \
                                   $MYSQL_DATABASE
else
    # Direct restore
    mysql --host=$MYSQL_HOST --port=$MYSQL_PORT \
          --user=$MYSQL_USER --password=$MYSQL_PASSWORD \
          $MYSQL_DATABASE < "$BACKUP_FILE"
fi

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo "Database restore completed successfully"
    
    # Restart the API service
    echo "Starting API service..."
    docker-compose start api
    
    # Verify database
    echo "Verifying database..."
    mysql --host=$MYSQL_HOST --port=$MYSQL_PORT \
          --user=$MYSQL_USER --password=$MYSQL_PASSWORD \
          -e "SELECT COUNT(*) FROM events" $MYSQL_DATABASE
else
    echo "Database restore failed!"
    exit 1
fi 
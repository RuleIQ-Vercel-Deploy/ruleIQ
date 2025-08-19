#!/bin/bash
set -euo pipefail

# ruleIQ Docker Volume Backup Script
# This script creates backups of critical Docker volumes

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_PROJECT="${COMPOSE_PROJECT:-ruleiq}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to backup a volume
backup_volume() {
    local volume_name=$1
    local backup_name="${volume_name}_${DATE}.tar.gz"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    echo "Backing up volume: $volume_name"
    
    # Create backup using a temporary container
    docker run --rm \
        -v "${COMPOSE_PROJECT}_${volume_name}:/data:ro" \
        -v "$(pwd)/${BACKUP_DIR}:/backup" \
        alpine:latest \
        tar czf "/backup/${backup_name}" -C /data .
    
    echo "Backup created: $backup_path"
}

# Function to restore a volume
restore_volume() {
    local volume_name=$1
    local backup_file=$2
    
    if [[ ! -f "$backup_file" ]]; then
        echo "Error: Backup file $backup_file not found"
        exit 1
    fi
    
    echo "Restoring volume: $volume_name from $backup_file"
    
    # Stop services before restore
    docker-compose down
    
    # Create volume if it doesn't exist
    docker volume create "${COMPOSE_PROJECT}_${volume_name}" || true
    
    # Restore from backup
    docker run --rm \
        -v "${COMPOSE_PROJECT}_${volume_name}:/data" \
        -v "$(pwd):/backup" \
        alpine:latest \
        tar xzf "/backup/${backup_file}" -C /data
    
    echo "Volume restored: $volume_name"
    echo "Remember to restart services with: docker-compose up -d"
}

# Function to list backups
list_backups() {
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "No backups found"
}

# Function to cleanup old backups (keep last 7 days)
cleanup_old_backups() {
    echo "Cleaning up backups older than 7 days..."
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +7 -delete
    echo "Cleanup completed"
}

# Main script logic
case "${1:-backup}" in
    "backup")
        echo "Starting backup process..."
        backup_volume "redis_data"
        backup_volume "postgres_data"
        backup_volume "celerybeat_schedule"
        cleanup_old_backups
        echo "Backup process completed"
        ;;
    "restore")
        if [[ -z "${2:-}" ]] || [[ -z "${3:-}" ]]; then
            echo "Usage: $0 restore <volume_name> <backup_file>"
            echo "Available volumes: redis_data, postgres_data, celerybeat_schedule"
            exit 1
        fi
        restore_volume "$2" "$3"
        ;;
    "list")
        list_backups
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    *)
        echo "Usage: $0 [backup|restore|list|cleanup]"
        echo ""
        echo "Commands:"
        echo "  backup           - Backup all volumes (default)"
        echo "  restore <vol> <file> - Restore volume from backup file"
        echo "  list             - List available backups"
        echo "  cleanup          - Remove backups older than 7 days"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore redis_data redis_data_20231201_120000.tar.gz"
        echo "  $0 list"
        exit 1
        ;;
esac
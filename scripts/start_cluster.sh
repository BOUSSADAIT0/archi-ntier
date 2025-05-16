#!/bin/bash

# Stop any existing containers
docker-compose down -v

# Remove old volumes
docker volume prune -f

# Start the first node
docker-compose up -d mariadb-1
sleep 15  # Wait for the first node to be ready

# Start the remaining nodes
docker-compose up -d mariadb-2 mariadb-3
sleep 15  # Wait for nodes to join the cluster

# Start HAProxy
docker-compose up -d haproxy
sleep 10  # Wait for HAProxy to be ready

# Initialize the database schema
docker-compose exec mariadb-1 mysql -uroot -prootpassword < scripts/init_db.sql

# Start the API service
docker-compose up -d api

echo "Cluster is starting up..."
echo "Waiting for all services to be ready..."
sleep 15

# Check cluster status
docker-compose exec mariadb-1 mysql -uroot -prootpassword -e "SHOW STATUS LIKE 'wsrep_%';"

echo "Cluster is ready!"
echo "API is available at http://localhost:18000"
echo "HAProxy stats are available at http://localhost:18404" 
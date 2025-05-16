#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Event Booking System Quick Start ===${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your configuration if needed.${NC}"
fi

# Make scripts executable
chmod +x scripts/start_cluster.sh
chmod +x scripts/backup_db.sh
chmod +x scripts/restore_db.sh
chmod +x scripts/monitor_cluster.py

# Start the cluster
echo -e "\n${YELLOW}Starting the database cluster and API...${NC}"
./scripts/start_cluster.sh

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Start monitoring in the background
echo -e "\n${YELLOW}Starting cluster monitoring...${NC}"
python scripts/monitor_cluster.py &
MONITOR_PID=$!

# Display access information
echo -e "\n${GREEN}=== System is ready! ===${NC}"
echo -e "API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "HAProxy Statistics: ${YELLOW}http://localhost:8404${NC}"
echo -e "Database port: ${YELLOW}3309${NC}"

# Trap Ctrl+C
trap cleanup INT

cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $MONITOR_PID
    docker-compose down
    deactivate
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}

# Keep script running
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"
wait 
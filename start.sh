#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi

if ! command_exists python; then
    echo -e "${RED}Error: Python is not installed. Please install Python and try again.${NC}"
    exit 1
fi

if ! python -c "import yaml" > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: PyYAML is not installed. Installing...${NC}"
    pip install pyyaml
fi

if ! docker network ls | grep -q RinNetwork; then
    echo -e "${YELLOW}Creating RinNetwork Docker network...${NC}"
    docker network create RinNetwork
fi

echo -e "${CYAN}Initializing environment variables from configuration...${NC}"
if [ -f "./rinbot/scripts/init_postgres_env.sh" ]; then
    source ./rinbot/scripts/init_postgres_env.sh
else
    echo -e "${RED}Error: init_postgres_env.sh not found.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting Docker Compose services...${NC}"
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Services started successfully!${NC}"
    echo -e "\n${YELLOW}To create a superuser, run:${NC}"
    echo -e "${YELLOW}docker exec -it rinbot-django python scripts/create_superuser.py${NC}"
else
    echo -e "\n${RED}Failed to start services. Check the error messages above.${NC}"
    exit 1
fi
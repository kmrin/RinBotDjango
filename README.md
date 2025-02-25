# RinBot Django

A Django-based web application with integrated Lavalink server and PostgreSQL database for audio streaming capabilities.

## Project Overview

RinBot Django is a comprehensive web application that combines:
- Django web framework for the backend
- Lavalink server for audio streaming
- PostgreSQL database for data persistence

The project is fully containerized using Docker, making it easy to set up and run in any environment.

## Prerequisites

### Required Software
- [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose
- [PowerShell 7](https://github.com/PowerShell/PowerShell) (for Windows users)
- [Python 3.13](https://www.python.org/downloads/) (for local development)

### Windows-Specific Requirements
- PowerShell 7 with the `powershell-yaml` module installed
  ```powershell
  Install-Module -Name powershell-yaml -Scope CurrentUser
  ```

### Network Setup
The application requires a Docker network named `RinNetwork`. Create it with:
```bash
docker network create RinNetwork
```

## Configuration

All configuration settings are centralized in a single YAML file:
```
rinbot/lavalink/config/rinbot.yml
```

This file contains settings for:
- **Django**: secret key, debug mode, allowed hosts, superuser credentials
- **Database**: name, user, password, host, port
- **Lavalink**: password, port
- **Instance directories**: base directory, subdirectories

Example configuration:
```yaml
# Django Settings
django:
  secret_key: 'your-secret-key'
  debug: true
  allowed_hosts: []
  superuser:
    username: admin
    email: admin@example.com
    password: adminpassword

# Database Settings
database:
  name: rinbot
  user: rinbot
  password: rinbotpassword
  host: rinbot-postgres
  port: 5432

# Lavalink Settings
lavalink:
  password: youshallnotpass
  port: 2333

# Instance Directory Settings
instance:
  base_dir: /var/lib/rinbot
  subdirs:
    - logs/tracebacks
    - logs/lavalink
    - cache
```

## Getting Started

### Starting the Application

#### On Windows
```powershell
# Make sure you're using PowerShell 7
pwsh

# Run the startup script
.\start-windows.ps1
```

#### On Linux/macOS
```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the startup script
./start.sh
```

The startup script will:
1. Load configuration from `rinbot.yml`
2. Set up environment variables
3. Start all Docker Compose services

### Accessing the Services

Once the application is running, you can access:
- **Django application**: http://localhost:8002
- **Django admin panel**: http://localhost:8002/admin
- **Lavalink server**: ws://localhost:2333 (requires password from config)
- **PostgreSQL database**: localhost:5432 (use credentials from config)

## Project Structure

```
RinBotDjango/
├── rinbot/                      # Main application code
│   ├── lavalink/                # Lavalink configuration
│   │   └── config/
│   │       ├── lavalink.yml     # Lavalink server config
│   │       └── rinbot.yml       # Central configuration file
│   ├── scripts/                 # Utility scripts
│   │   ├── create_superuser.py  # Creates Django admin user
│   │   ├── init_instance.sh     # Initializes directory structure
│   │   └── init_postgres_env.sh # Sets up database environment
│   ├── config.py                # Configuration loader
│   └── settings.py              # Django settings
├── Dockerfile                   # Django container definition
├── Dockerfile.lavalink          # Lavalink container definition
├── docker-compose.yml           # Multi-container definition
├── start.sh                     # Linux/macOS startup script
└── start-windows.ps1            # Windows startup script
```

## Data Persistence

All persistent data is stored in Docker volumes:
- **instance-data**: Application data at `/var/lib/rinbot`
  - `logs/tracebacks`: Exception logs
  - `logs/lavalink`: Lavalink server logs
  - `cache`: Application cache
- **postgres-data**: PostgreSQL database files
- **lavalink-plugins**: Lavalink plugins at `/opt/lavalink/plugins`

## Administration

### Creating a Django Superuser

To create an admin user for the Django admin interface:

```bash
docker exec -it rinbot-django python scripts/create_superuser.py
```

The superuser credentials are defined in the `rinbot.yml` configuration file.

### Database Management

To connect to the PostgreSQL database:

```bash
docker exec -it rinbot-postgres psql -U rinbot -d rinbot
```

### Viewing Logs

To view logs from the containers:

```bash
# Django logs
docker logs rinbot-django

# Lavalink logs
docker logs rinbot-lavalink

# PostgreSQL logs
docker logs rinbot-postgres
```

## Development

### Local Development

For development purposes, you can modify the Django code in the `rinbot` directory, and the changes will be reflected in real-time due to the volume mount.

### Adding Lavalink Plugins

For Lavalink plugins, place them in the `rinbot-lavalink-plugins` volume, which is mounted to `/opt/lavalink/plugins` in the container.

### Modifying Configuration

To modify any configuration settings:

1. Edit the `rinbot/lavalink/config/rinbot.yml` file
2. Restart the services with the appropriate startup script

## Troubleshooting

### Windows-Specific Issues

- **PowerShell Module Not Found**: If you get an error about the `powershell-yaml` module, install it with:
  ```powershell
  Install-Module -Name powershell-yaml -Scope CurrentUser
  ```

- **Permission Denied**: If you get permission errors when running scripts, you may need to adjust PowerShell's execution policy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Common Issues

- **Port Conflicts**: If ports 8002, 2333, or 5432 are already in use, modify the port mappings in `docker-compose.yml`

- **Network Issues**: Ensure the `RinNetwork` Docker network exists:
  ```bash
  docker network create RinNetwork
  ```

- **Database Connection Errors**: Check that the PostgreSQL container is running and the credentials in `rinbot.yml` are correct

## License

[Your License Information]

## Contact

[Your Contact Information] 
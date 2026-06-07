# Docker Deployment Guide

SQL Server Security HUD - Docker Deployment Instructions

## Prerequisites

- Docker and Docker Compose installed
- SQL Server instance running (existing on 192.168.101.219)
- Environment variables configured (see below)

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# SQL Server Connection
MSSQL_SERVER=192.168.101.219
MSSQL_PORT=1433
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
MSSQL_DATABASE=SqlSecurityHUD
```

Or copy from the existing backend `.env` and ensure these variables are set.

### 2. Build the Docker Image

```bash
docker-compose build
```

Or build manually:

```bash
docker build -t qlmoni-hud:latest .
```

### 3. Run the Container

Using docker-compose:

```bash
docker-compose up -d
```

Using docker directly:

```bash
docker run -d \
  --name qlmoni-hud \
  -p 8090:8090 \
  -e MSSQL_SERVER=192.168.101.219 \
  -e MSSQL_PORT=1433 \
  -e MSSQL_USER=your_username \
  -e MSSQL_PASSWORD=your_password \
  -e MSSQL_DATABASE=SqlSecurityHUD \
  -v ./logs:/app/logs \
  --restart unless-stopped \
  qlmoni-hud:latest
```

### 4. Access the Application

Open your browser and navigate to:

```
http://localhost:8090
```

## Docker Compose Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f hud
```

### Rebuild image
```bash
docker-compose build --no-cache
```

### Check container status
```bash
docker-compose ps
```

## Manual Docker Commands

### Build the image
```bash
docker build -t qlmoni-hud:latest .
```

### Run the container
```bash
docker run -d \
  --name qlmoni-hud \
  -p 8090:8090 \
  --env-file .env \
  -v ./logs:/app/logs \
  --restart unless-stopped \
  qlmoni-hud:latest
```

### View logs
```bash
docker logs -f qlmoni-hud
```

### Stop the container
```bash
docker stop qlmoni-hud
```

### Remove the container
```bash
docker rm qlmoni-hud
```

## Production Deployment

### Using Gunicorn (Recommended)

Update `requirements.txt` to include gunicorn:

```bash
pip install gunicorn
```

Modify the Dockerfile CMD to use gunicorn:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8090", "--workers", "4", "--timeout", "120", "backend.app:app"]
```

### Environment Variables for Production

```
FLASK_ENV=production
MSSQL_SERVER=your_prod_server
MSSQL_PORT=1433
MSSQL_USER=prod_user
MSSQL_PASSWORD=prod_password
MSSQL_DATABASE=SqlSecurityHUD
```

### Docker Registry

Tag and push to your registry:

```bash
docker tag qlmoni-hud:latest your-registry/qlmoni-hud:latest
docker push your-registry/qlmoni-hud:latest
```

## Troubleshooting

### Container exits immediately

Check logs:
```bash
docker logs qlmoni-hud
```

### Database connection errors

Verify SQL Server credentials:
```bash
docker exec qlmoni-hud python -c "import pyodbc; print('Connection OK')"
```

### Port already in use

Change the port mapping in docker-compose.yml:
```yaml
ports:
  - "8091:8090"  # Changed from 8090 to 8091
```

### Rebuild and restart

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Health Check

The container includes a health check that monitors the application:

```bash
docker inspect --format='{{.State.Health.Status}}' qlmoni-hud
```

## Volume Mounting

To persist logs:

```bash
docker run -d \
  --name qlmoni-hud \
  -p 8090:8090 \
  -v ./logs:/app/logs \
  qlmoni-hud:latest
```

## Network Access

### Docker Network

The container runs on the `hud-network` bridge network. To access from other containers:

```
http://hud:8090
```

### External Access

Access from host machine:

```
http://localhost:8090
```

## Database Setup

Before deploying, ensure the SQL Server has the required database and tables:

```bash
# From SQL Server machine, run:
sqlcmd -S 192.168.101.219 -U your_user -P your_password -i database/schema.sql
```

## SSL/TLS Support

For HTTPS in production, use a reverse proxy like Nginx:

```yaml
services:
  nginx:
    image: nginx:latest
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - hud

  hud:
    # ... existing configuration
```

## Performance Tuning

### Gunicorn Workers

For CPU-bound tasks, use more workers:

```
gunicorn --workers 4 --worker-class sync backend.app:app
```

For I/O-bound tasks (database queries), use async workers:

```
gunicorn --workers 2 --worker-class gevent backend.app:app
```

### Memory Limits

Set memory constraints:

```bash
docker run -d \
  --memory="512m" \
  --memory-swap="512m" \
  qlmoni-hud:latest
```

## Maintenance

### Update image

```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Backup logs

```bash
cp -r logs/ logs-backup-$(date +%Y%m%d)/
```

### Monitor resource usage

```bash
docker stats qlmoni-hud
```

## Support

For issues, check:
1. Container logs: `docker-compose logs hud`
2. Network connectivity: `docker exec qlmoni-hud ping 192.168.101.219`
3. Port availability: `netstat -an | grep 8090`

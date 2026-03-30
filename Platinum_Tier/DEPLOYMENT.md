# Platinum Tier Deployment Guide

## 📦 Overview

Platinum Tier deployment provides a **production-ready, containerized AI employee** with:

- ✅ **Docker-based deployment** for consistency across environments
- ✅ **Always-On logic** with automatic restart on failure
- ✅ **PostgreSQL database** for Odoo ERP (cloud-ready)
- ✅ **Multi-service architecture** with proper networking
- ✅ **Health checks** for all services
- ✅ **Persistent storage** for logs and data
- ✅ **Resource limits** for production stability

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- Git (for cloning)

### 1. Clone/Navigate to Project

```bash
cd C:\Users\Touqeer\Desktop\Hackathon_0(My_AI_Employee)\Platinum_Tier
```

### 2. Configure Environment Variables

Create or update `.env` file with your credentials:

```bash
# Odoo Configuration
ODOO_USER=touqeerchamp@gmail.com
ODOO_PASS=OdooAdmin123
ODOO_DB_PASSWORD=YourSecureDbPassword123!

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f ai_agent

# Check service status
docker-compose ps
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                   (platinum_network)                         │
│                                                              │
│  ┌──────────────────────┐         ┌──────────────────────┐  │
│  │     ai_agent         │         │      odoo_db         │  │
│  │  (Python 3.11-slim)  │ ──────► │  (PostgreSQL 15)     │  │
│  │                      │         │                      │  │
│  │  • autonomous_agent  │         │  • ai_employee_db    │  │
│  │  • odoo_client       │         │  • Persistent data   │  │
│  │  • gmail_watcher     │         │  • Port: 5432        │  │
│  │  • linkedin_automation│        │                      │  │
│  │  • create_plans      │         │                      │  │
│  │  • ceo_briefer       │         │                      │  │
│  │                      │         │                      │  │
│  │  Restart: always     │         │  Restart: always     │  │
│  │  Health Check: ✓     │         │  Health Check: ✓     │  │
│  └──────────────────────┘         └──────────────────────┘  │
│                                                              │
│  ┌──────────────────────┐                                    │
│  │   (Optional) Odoo    │                                    │
│  │   odoo:16.0          │                                    │
│  │   Port: 8069         │                                    │
│  └──────────────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Services

### 1. `ai_agent` - Autonomous AI Employee

| Property | Value |
|----------|-------|
| **Base Image** | Python 3.11-slim |
| **Restart Policy** | `always` |
| **Health Check** | Every 30s |
| **Volumes** | logs, inbox, needs_action, linkedin_drafts |
| **Dependencies** | odoo_db |

**Features:**
- Ralph Wiggum Loop for autonomous task processing
- Gmail integration (read/create drafts)
- LinkedIn automation (draft generation)
- Odoo ERP integration (customer management)
- CEO Weekly Briefing generation
- Graceful degradation on service failures

### 2. `odoo_db` - PostgreSQL Database

| Property | Value |
|----------|-------|
| **Image** | postgres:15-alpine |
| **Restart Policy** | `always` |
| **Health Check** | Every 10s |
| **Port** | 5432 (internal + exposed) |
| **Volumes** | odoo_db_data (persistent) |

**Features:**
- Persistent data storage
- Automatic backups (optional)
- Cloud-ready configuration

### 3. `odoo` - Odoo ERP (Optional)

Uncomment in `docker-compose.yml` to enable full Odoo instance.

| Property | Value |
|----------|-------|
| **Image** | odoo:16.0 |
| **Port** | 8069 |
| **Dependencies** | odoo_db |

---

## 🔧 Commands

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Start with build (after code changes)
docker-compose up -d --build

# View startup logs
docker-compose logs -f
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai_agent
docker-compose logs -f odoo_db

# Last 100 lines
docker-compose logs --tail=100 ai_agent
```

### Access Container

```bash
# Shell inside ai_agent container
docker-compose exec ai_agent bash

# Shell inside odoo_db container
docker-compose exec odoo_db sh

# Run specific command
docker-compose exec ai_agent python autonomous_agent.py
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart ai_agent
```

### Monitor Health

```bash
# Check service status
docker-compose ps

# View health check status
docker inspect --format='{{.State.Health.Status}}' platinum_ai_employee
```

---

## 📊 Resource Management

### Current Limits

| Service | CPU Limit | Memory Limit |
|---------|-----------|--------------|
| ai_agent | 2.0 cores | 2 GB |
| odoo_db | 2.0 cores | 2 GB |

### Adjust Resources

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Increase CPU
      memory: 4G       # Increase memory
```

---

## 💾 Data Persistence

### Volumes

| Volume | Purpose | Location |
|--------|---------|----------|
| `odoo_db_data` | PostgreSQL data | Managed by Docker |
| `./logs` | Application logs | Host: `./logs` |
| `./inbox` | Gmail inbox cache | Host: `./inbox` |
| `./needs_action` | Complex emails | Host: `./needs_action` |
| `./linkedin_drafts` | LinkedIn drafts | Host: `./linkedin_drafts` |

### Backup Database

```bash
# Create backup
docker-compose exec odoo_db pg_dump -U odoo ai_employee_db > backup.sql

# Restore from backup
docker-compose exec -T odoo_db psql -U odoo ai_employee_db < backup.sql
```

---

## 🔐 Security

### Environment Variables

Sensitive data is stored in `.env` file (gitignored):

```bash
# .env (DO NOT COMMIT)
ODOO_PASS=SecurePassword123!
ODOO_DB_PASSWORD=EvenSecureerDbPass456!
GOOGLE_API_KEY=your_secret_key
```

### Network Isolation

All services communicate over private `platinum_network`.

### Production Recommendations

1. **Remove exposed ports** for odoo_db (use internal networking only)
2. **Use Docker secrets** for sensitive data
3. **Enable TLS** for database connections
4. **Set up firewall rules** for container networking

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs ai_agent

# Verify .env file exists
ls -la .env

# Check credentials.json
ls -la credentials.json
```

### Database Connection Failed

```bash
# Check if odoo_db is healthy
docker-compose ps odoo_db

# View database logs
docker-compose logs odoo_db

# Test connection from ai_agent
docker-compose exec ai_agent nc -zv odoo_db 5432
```

### Permission Issues

```bash
# Fix volume permissions (Linux/Mac)
sudo chown -R 1000:1000 ./logs ./inbox ./needs_action
```

### Rebuild After Code Changes

```bash
# Force rebuild
docker-compose up -d --build --force-recreate
```

---

## 📈 Monitoring

### View Real-time Logs

```bash
# All services
docker-compose logs -f

# Filter by service
docker-compose logs -f ai_agent | grep "ERROR"
```

### Resource Usage

```bash
# Docker stats (CPU, Memory)
docker stats platinum_ai_employee platinum_odoo_db
```

### Log Files

- **Application logs:** `./logs/automation.log`
- **Audit logs:** `./logs/audit_logs/`
- **Docker logs:** `docker-compose logs`

---

## 🌐 Cloud Deployment

### AWS ECS

1. Create ECS cluster
2. Convert `docker-compose.yml` to ECS task definition
3. Use AWS RDS for PostgreSQL instead of container

### Google Cloud Run

1. Build and push to Container Registry
2. Deploy to Cloud Run with Cloud SQL connector

### Azure Container Instances

1. Push to Azure Container Registry
2. Deploy using Azure CLI

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-26 | Initial Platinum Tier release |

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review architecture: `ARCHITECTURE.md`
- Contact: Mohammad Touqeer

---

**🚀 Your AI Employee is now running in production-ready Platinum Tier!**

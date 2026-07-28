# 🚀 DEPLOYMENT GUIDE
## BCI Artifact Rejection API - Production Setup

---

## 📋 TABLE OF CONTENTS
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
   - [Option 1: Docker Compose](#option-1-docker-compose-recommended)
   - [Option 2: Kubernetes](#option-2-kubernetes)
   - [Option 3: Manual Installation](#option-3-manual-installation)
3. [Monitoring](#monitoring)
4. [Scaling](#scaling)
5. [Security](#security)
6. [Backup](#backup)
7. [Troubleshooting](#troubleshooting)
8. [Production Checklist](#production-checklist)

---

## PREREQUISITES

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Docker | 20.10+ | Latest |
| Docker Compose | 2.0+ | Latest |
| Git | 2.30+ | Latest |
| RAM | 4GB | 8GB+ |
| Disk Space | 20GB | 50GB+ |
| CPU | 2 Cores | 4+ Cores |
| Python | 3.10+ | 3.11+ |

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose \
    git \
    curl

# CentOS/RHEL
sudo yum install -y \
    gcc \
    gcc-c++ \
    python3-devel \
    python3-pip \
    docker \
    docker-compose \
    git \
    curl

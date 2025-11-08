# AGI-SAC Production Deployment Guide

This guide covers production deployment of AGI-SAC simulations and federation infrastructure.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Options](#installation-options)
3. [Configuration](#configuration)
4. [Standalone Deployment](#standalone-deployment)
5. [Federation Deployment](#federation-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Monitoring & Health Checks](#monitoring-health-checks)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)
10. [Security Considerations](#security-considerations)

---

## Prerequisites

### System Requirements

**Minimum (Development/Testing):**
- CPU: 4 cores
- RAM: 8 GB
- Python: 3.9+
- OS: Linux, macOS, Windows

**Recommended (Production):**
- CPU: 16+ cores
- RAM: 64 GB
- GPU: NVIDIA with CUDA support (optional, for large simulations)
- Python: 3.10 or 3.11
- OS: Ubuntu 22.04 LTS or similar

**Large-Scale (Research):**
- CPU: 32+ cores
- RAM: 128+ GB
- GPU: Multiple NVIDIA A100/H100 (for GPU acceleration)
- Python: 3.11
- Network: Low-latency for federation mode

### Software Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip build-essential

# RHEL/CentOS
sudo yum install -y python311 python311-devel gcc

# macOS
brew install python@3.11
```

---

## Installation Options

### Option 1: Basic Installation

For simple simulations without federation or chaos testing:

```bash
# Create virtual environment
python3.11 -m venv agisa-env
source agisa-env/bin/activate  # Windows: agisa-env\Scripts\activate

# Install AGI-SAC
pip install agisa-sac

# Verify installation
agisa-sac --help
```

### Option 2: Full Installation

All features including federation, chaos testing, and GCP integration:

```bash
pip install agisa-sac[all]

# Verify all CLIs are available
agisa-sac --help
agisa-federation --help
agisa-chaos --help
```

### Option 3: Feature-Specific Installation

Install only needed features:

```bash
# Federation server only
pip install agisa-sac[federation]

# Chaos engineering only
pip install agisa-sac[chaos]

# Google Cloud Platform integration
pip install agisa-sac[gcp]

# Visualization tools
pip install agisa-sac[visualization]

# Development tools
pip install agisa-sac[dev]
```

### Option 4: From Source

For development or latest features:

```bash
git clone https://github.com/topstolenname/agisa_sac.git
cd agisa_sac

python3.11 -m venv .venv
source .venv/bin/activate

pip install -e ".[all]"
```

---

## Configuration

### Environment Variables

Create a `.env` file or export environment variables:

```bash
# Logging
export LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
export AGISA_LOG_FILE=/var/log/agisa-sac/simulation.log

# GCP Integration (optional)
export GCP_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Federation (optional)
export AGISA_FEDERATION_HOST=0.0.0.0
export AGISA_FEDERATION_PORT=8000

# Performance
export OMP_NUM_THREADS=16                # OpenMP threads
export CUDA_VISIBLE_DEVICES=0,1          # GPU devices
```

### Configuration File Template

Create `config/production.json`:

```json
{
  "num_agents": 500,
  "num_epochs": 200,
  "random_seed": 42,
  "use_gpu": true,
  "agent_capacity": 100,
  "use_semantic": true,
  "tda_max_dimension": 1,
  "tda_run_frequency": 10,
  "community_check_frequency": 20,
  "epoch_log_frequency": 10,
  "personalities": []
}
```

### Logging Configuration

**Console Logging (Development):**
```bash
agisa-sac run --preset default --log-level INFO
```

**File Logging (Production):**
```bash
agisa-sac run \
  --preset large \
  --log-level INFO \
  --log-file /var/log/agisa-sac/simulation.log
```

**JSON Structured Logging (Production):**
```bash
agisa-sac run \
  --preset large \
  --json-logs \
  --log-file /var/log/agisa-sac/simulation.json
```

---

## Standalone Deployment

### Basic Simulation

```bash
# Run with preset
agisa-sac run --preset medium

# Run with custom config
agisa-sac run --config config/production.json
```

### Long-Running Simulation

Use `nohup` or `screen` for background execution:

```bash
# Using nohup
nohup agisa-sac run \
  --preset large \
  --log-file simulation.log \
  --json-logs \
  > output.log 2>&1 &

# Using screen
screen -S agisa-simulation
agisa-sac run --preset large --json-logs
# Detach: Ctrl+A, D
# Reattach: screen -r agisa-simulation
```

### Systemd Service

Create `/etc/systemd/system/agisa-sac.service`:

```ini
[Unit]
Description=AGI-SAC Simulation Service
After=network.target

[Service]
Type=simple
User=agisa
Group=agisa
WorkingDirectory=/opt/agisa-sac
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/agisa-sac/.venv/bin/agisa-sac run \
  --config /etc/agisa-sac/production.json \
  --json-logs \
  --log-file /var/log/agisa-sac/simulation.json
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agisa-sac
sudo systemctl start agisa-sac
sudo systemctl status agisa-sac
```

---

## Federation Deployment

### Single-Node Federation Server

```bash
agisa-federation server --host 0.0.0.0 --port 8000 --verbose
```

### Production Federation Server

#### With Systemd

Create `/etc/systemd/system/agisa-federation.service`:

```ini
[Unit]
Description=AGI-SAC Federation Server
After=network.target

[Service]
Type=simple
User=agisa
Group=agisa
WorkingDirectory=/opt/agisa-sac
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/agisa-sac/.venv/bin/agisa-federation server \
  --host 0.0.0.0 \
  --port 8000
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agisa-federation
sudo systemctl start agisa-federation
```

#### Behind Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/agisa-federation`:

```nginx
upstream agisa_federation {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name federation.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name federation.example.com;

    ssl_certificate /etc/letsencrypt/live/federation.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/federation.example.com/privkey.pem;

    location / {
        proxy_pass http://agisa_federation;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://agisa_federation;
        access_log off;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/agisa-federation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Docker Deployment

### Build Image

```bash
docker build -t agisa-sac:1.0.0-alpha .
```

### Run Simulation in Docker

```bash
docker run \
  --name agisa-simulation \
  --rm \
  -v $(pwd)/config:/config \
  -v $(pwd)/logs:/logs \
  agisa-sac:1.0.0-alpha \
  agisa-sac run --config /config/production.json --log-file /logs/simulation.log
```

### Run Federation Server in Docker

```bash
docker run \
  --name agisa-federation \
  -d \
  -p 8000:8000 \
  --restart unless-stopped \
  agisa-sac:1.0.0-alpha \
  agisa-federation server --host 0.0.0.0 --port 8000
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  federation-server:
    image: agisa-sac:1.0.0-alpha
    container_name: agisa-federation
    command: agisa-federation server --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  simulation:
    image: agisa-sac:1.0.0-alpha
    container_name: agisa-simulation
    command: agisa-sac run --config /config/production.json --json-logs --log-file /logs/simulation.json
    depends_on:
      - federation-server
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/config
      - ./logs:/logs
    restart: on-failure
```

Start services:

```bash
docker-compose up -d
docker-compose logs -f
```

---

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Check federation server health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "service": "agisa-sac-federation",
  "timestamp": "2025-11-08T12:34:56.789Z",
  "registered_nodes": 42,
  "uptime_seconds": 3600.5,
  "identity_initialized": true,
  "version": "1.0.0-alpha"
}
```

### Log Monitoring

**Tail Logs:**
```bash
tail -f /var/log/agisa-sac/simulation.log
```

**Parse JSON Logs:**
```bash
cat /var/log/agisa-sac/simulation.json | jq '.level' | sort | uniq -c
```

**Filter Errors:**
```bash
cat /var/log/agisa-sac/simulation.json | jq 'select(.level == "ERROR")'
```

### Process Monitoring

**Check Running Processes:**
```bash
ps aux | grep agisa
```

**Monitor Resource Usage:**
```bash
top -p $(pgrep -f agisa-sac)
htop -p $(pgrep -f agisa-sac)
```

**Watch System Resources:**
```bash
watch -n 1 'nvidia-smi'  # GPU monitoring
watch -n 1 'free -h'     # Memory monitoring
```

---

## Performance Tuning

### CPU Optimization

```bash
# Set CPU affinity
taskset -c 0-15 agisa-sac run --preset large

# Increase process priority
nice -n -10 agisa-sac run --preset large
```

### Memory Optimization

```bash
# Increase memory limits (systemd)
[Service]
MemoryMax=96G
MemoryHigh=80G
```

### GPU Optimization

```bash
# Specify GPU devices
export CUDA_VISIBLE_DEVICES=0,1,2,3

# Run with GPU acceleration
agisa-sac run --preset large --gpu

# Monitor GPU usage
nvidia-smi -l 1
```

### Disk I/O Optimization

```bash
# Use SSD for checkpoints
agisa-sac run --config production.json --output-dir /mnt/nvme/agisa-sac
```

---

## Troubleshooting

### Common Issues

#### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'agisa_sac'`

**Solution:**
```bash
pip install --force-reinstall agisa-sac[all]
```

#### Memory Errors

**Problem:** `MemoryError` during large simulations

**Solution:**
```bash
# Reduce agent count or epochs
agisa-sac run --preset medium --agents 100

# Enable memory-efficient mode (if available)
# Or increase system swap
sudo fallocate -l 32G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### GPU Not Detected

**Problem:** `use_gpu=True` but simulation runs on CPU

**Solution:**
```bash
# Verify CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

#### Federation Server Connection Refused

**Problem:** Cannot connect to federation server

**Solution:**
```bash
# Check if server is running
systemctl status agisa-federation

# Check port is listening
sudo netstat -tulpn | grep 8000

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp
```

### Debug Mode

Enable verbose logging:

```bash
agisa-sac run --preset default --log-level DEBUG -v
```

### Log Analysis

```bash
# Count log levels
grep -oP '"level":\s*"\K[^"]+' simulation.json | sort | uniq -c

# Find errors
grep ERROR simulation.log | tail -20

# Track simulation progress
grep "Epoch.*completed" simulation.log | tail -10
```

---

## Security Considerations

### Network Security

- Use HTTPS/TLS for federation servers
- Implement rate limiting on endpoints
- Use firewall rules to restrict access
- Enable authentication for production endpoints

### Authentication

Implement token-based auth for federation:

```python
# In your federation client
headers = {
    "Authorization": f"Bearer {token}",
    "X-API-Key": api_key
}
```

### Data Protection

- Encrypt sensitive simulation data at rest
- Use secure channels for inter-node communication
- Implement audit logging for all API calls
- Regular backup of simulation checkpoints

### Resource Limits

```ini
# In systemd service
[Service]
CPUQuota=80%
MemoryMax=64G
TasksMax=1000
```

---

## Backup & Recovery

### State Checkpointing

```python
# In simulation code
orchestrator.save_state(
    "checkpoints/simulation_epoch_100.pkl",
    include_memory_embeddings=True
)
```

### Automated Backups

```bash
#!/bin/bash
# backup-agisa.sh

BACKUP_DIR="/backups/agisa-sac"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp -r /etc/agisa-sac "$BACKUP_DIR/config_$TIMESTAMP"

# Backup logs
cp -r /var/log/agisa-sac "$BACKUP_DIR/logs_$TIMESTAMP"

# Backup simulation state
cp -r /opt/agisa-sac/checkpoints "$BACKUP_DIR/checkpoints_$TIMESTAMP"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} +
```

Add to crontab:

```bash
0 */6 * * * /opt/agisa-sac/scripts/backup-agisa.sh
```

---

## Performance Benchmarks

### Expected Performance

| Configuration | Agents | Epochs | Time (CPU) | Time (GPU) | Memory |
|---------------|--------|--------|------------|------------|--------|
| quick_test    | 10     | 20     | ~2 min     | ~1 min     | 2 GB   |
| default       | 30     | 50     | ~15 min    | ~8 min     | 8 GB   |
| medium        | 100    | 100    | ~2 hours   | ~45 min    | 16 GB  |
| large         | 500    | 200    | ~24 hours  | ~6 hours   | 64 GB  |

*Benchmarks on Intel Xeon 16-core, 64GB RAM, NVIDIA A100*

---

## Support

For deployment issues:

1. Check [troubleshooting](#troubleshooting) section
2. Review logs with `--log-level DEBUG`
3. Search existing issues: https://github.com/topstolenname/agisa_sac/issues
4. Create new issue with logs and configuration

---

## Next Steps

After deployment:

1. Set up monitoring dashboards (Grafana)
2. Configure alerting (Prometheus)
3. Implement chaos testing
4. Scale federation to multiple nodes
5. Optimize for your specific use case

See [TODO.md](TODO.md) for roadmap and upcoming features.

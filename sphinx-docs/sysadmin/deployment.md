# Deployment Guide

This guide covers best practices for deploying Maeser into production environments, including containerization, process management, reverse proxy configuration, and scaling considerations.

---

## 1. Prerequisites

- A production server or cloud instance (e.g., AWS EC2, Azure VM, Google Compute Engine) running a Unix‑like OS (Ubuntu, Debian, etc.).
- Maeser application code cloned or pulled onto the server.
- Python 3.10+ installed.
- A PostgreSQL or MySQL database if you plan to use relational storage (optional).
- Domain name and DNS access for configuring TLS certificates.

---

## 2. Virtual Environment & Dependencies

1. **Clone the repository** and enter the directory:
   ```bash
   git clone https://github.com/byu-cpe/Maeser.git
   cd Maeser
   ```
2. **Create a virtual environment** and install dependencies:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   pip install gunicorn
   ```
3. **Configuration**: Edit your production `config.yaml` with production API keys, paths, and DB credentials (or set environment variables).
   ```bash
   cp config_example.yaml config.yaml
   # Edit config.yaml with production API keys, paths, and DB credentials
   ```

> **Note:**  
> For deployment, it is recommended, although not required, that you copy the provided files in the `/example/` directory as opposed to modifying them directly. Make a copy of `config_example.py` and rename it to `config.yaml`:
>    ```bash
>    cp config_example.yaml config.yaml
>    # Edit config.yaml with production API keys, paths, and DB credentials
>    ```
>
> Then in "config_example.py", be sure to update the config paths:
> ```python
>     config_paths = [
>         'config.yaml',
>         './config.yaml',
>         'example/config.yaml'
>         # Or anywhere else you plan on storing config.yaml
>     ]
> ```
> 
> Be sure to rename the other example files and update their references accordingly.

---

## 3. Using Gunicorn as WSGI Server

Gunicorn provides a robust, multi‑worker Python WSGI server for Flask apps.

1. **Start Gunicorn** with multiple workers:
   ```bash
   gunicorn \
     --workers 4 \
     --bind 0.0.0.0:8000 \
     --timeout 120 \
     example.flask_example_user_mangement:app
   ```
2. **Background Process**: Use a process manager (systemd, Supervisor) to keep Gunicorn running.

### 3.1 systemd Service Example

Create `/etc/systemd/system/maeser.service`:
```ini
[Unit]
Description=Maeser Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Maeser
ExecStart=/path/to/Maeser/.venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/path/to/Maeser/maeser.sock \
    example.flask_example_user_mangement:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable maeser
sudo systemctl start maeser
```

---

## 4. Reverse Proxy with NGINX & TLS

Use NGINX to terminate TLS and proxy requests to Gunicorn.

1. **Install NGINX**:
   ```bash
   sudo apt install nginx
   ```
2. **Obtain TLS Certificates** with Let’s Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```
3. **NGINX Server Block** (`/etc/nginx/sites-available/maeser`):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       location /.well-known/acme-challenge/ { allow all; }
       location / {
           return 301 https://$host$request_uri;
       }
   }

   server {
       listen 443 ssl;
       server_name yourdomain.com;
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

       location /static/ {
           alias /path/to/Maeser/maeser/controllers/common/static/;
       }

       location / {
           proxy_pass http://unix:/path/to/Maeser/maeser.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
4. **Enable** and **Test**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/maeser /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## 5. Containerization with Docker & Docker Compose

### 5.1 Dockerfile Example

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -e . && pip install gunicorn
EXPOSE 8000
env OPENAI_API_KEY=<your-key>
CMD ["gunicorn", "example.flask_example_user_mangement:app", "--bind", "0.0.0.0:8000"]
```

### 5.2 docker-compose.yml Example

```yaml
version: '3'
services:
  maeser:
    build: .
    command: gunicorn example.flask_example_user_mangement:app --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - config=/app/config.yaml
```

Launch:
```bash
docker-compose up -d --build
```

---

## 6. Scaling & High Availability

- **Horizontal Scaling**: Deploy multiple Gunicorn containers behind a load balancer (e.g., AWS ELB, NGINX upstream).  
- **Session Storage**: Use centralized memory store (Redis) or persistent DB for session state and chat logs.  
- **Container Orchestration**: Use Kubernetes, Docker Swarm, or ECS/EKS to manage replicas, auto‑scaling, and rolling updates.

---

## 7. Monitoring & Logging

- **Application Logs**: Configure Gunicorn `--access-logfile` and `--error-logfile` options.  
- **Chat Logs**: Ensure `ChatLogsManager` is writing to a persistent volume or external storage.  
- **Monitoring Tools**: Integrate Prometheus/Grafana for metrics (CPU, memory, request latency).  
- **Alerts**: Set up alerts for high error rates or API quota exhaustion.

---

## 8. Backup & Maintenance

- **Database Backups**: Schedule regular dumps of `USERS_DB_PATH` and chat logs.  
- **Vectorstore Snapshots**: Archive FAISS indexes after embedding runs to prevent data loss.  
- **Certificate Renewal**: Automate Let’s Encrypt renewals with `certbot renew --quiet` in a cron job.



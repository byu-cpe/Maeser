# SysAdmin Troubleshooting Guide

*Quick reference for resolving common issues in Maeser production deployments.*

---

## 1. Gunicorn (WSGI Server) Issues

### 1.1 Failing to Start
- **Symptoms:** `ModuleNotFoundError` or `AttributeError` referencing your app.
- **Checks & Fixes:**
  1. **Module path:** Ensure you launch Gunicorn with the correct module notation (e.g., `example.flask_example_user_mangement:app`).
  2. **Virtual environment:** Activate the same `.venv` where Maeser and Gunicorn are installed.
  3. **Installation:** Verify Gunicorn is present (`pip show gunicorn`). Install if missing: `pip install gunicorn`.

### 1.2 Worker Timeouts & Hangs
- **Symptoms:** Requests hang or time out after 30 seconds (default).
- **Solutions:**
  - **Increase timeout:** `--timeout 120` or higher.
  - **Preload app:** Add `--preload` to reduce per-worker startup cost.
  - **Error logs:** Specify `--error-logfile /path/to/error.log` and inspect stack traces.

### 1.3 Port Binding Conflicts
- **Symptoms:** `OSError: [Errno 98] Address already in use`.
- **Solutions:**
  - **Identify process:** `lsof -i :8000` or `netstat -tnlp | grep 8000`.
  - **Free port:** Stop the conflicting service or choose a different port.
  - **Socket binding:** Use Unix socket for NGINX proxy: `--bind unix:/path/to/maeser.sock`.

---

## 2. NGINX (Reverse Proxy) Issues

### 2.1 502 Bad Gateway
- **Symptoms:** NGINX returns a 502 error when proxying.
- **Checks & Fixes:**
  - **Backend status:** Confirm Gunicorn is running and listening on the expected socket/port.
  - **Proxy settings:** Match `proxy_pass` URL to Gunicorn bind (e.g., `http://127.0.0.1:8000` or `unix:/…`).
  - **Socket permissions:** `chown www-data:www-data maeser.sock && chmod 660 maeser.sock`.

### 2.2 SSL/TLS Certificate Errors
- **Symptoms:** Browser warnings about invalid or expired certificate.
- **Solutions:**
  - **Test renewal:** `sudo certbot renew --dry-run`.
  - **Verify paths:** Ensure NGINX `ssl_certificate` and `ssl_certificate_key` point to the correct files under `/etc/letsencrypt/live/yourdomain.com/`.
  - **Reload NGINX:** After renewal, run `sudo systemctl reload nginx`.

### 2.3 Static Assets Not Loading
- **Symptoms:** CSS/JS requests return 404.
- **Checks & Fixes:**
  - **Alias config:** Confirm `location /static/ { alias /path/to/maeser/controllers/common/static/; }` matches your file structure.
  - **File permissions:** Ensure the NGINX user (`www-data`) can read static files (`chmod -R u+r /path/to/static`).

---

## 3. Docker & Container Issues

### 3.1 Build Failures
- **Symptoms:** `docker build` errors due to missing files or dependencies.
- **Fixes:**
  - **Verify COPY:** Check your `Dockerfile` and `.dockerignore` to include required files.
  - **Base image:** Use `python:3.10-slim` or similar with necessary build tools.

### 3.2 Networking Problems
- **Symptoms:** Cannot access service on mapped ports.
- **Solutions:**
  - **Port mapping:** Ensure `docker-compose.yml` or `docker run -p 8000:8000` is correct.
  - **Network mode:** For advanced setups, consider `network_mode: host` (Linux only).

### 3.3 Volume & Permission Errors
- **Symptoms:** Containers cannot read/write volume-mounted directories.
- **Fixes:**
  - **UID/GID alignment:** Run container as your host user: `user: "$(id -u):$(id -g)"` in Compose.
  - **Host permissions:** `chown -R 1000:1000 ./data` or appropriate user/group.

---

## 4. Resource & Performance

### 4.1 High CPU / Memory Usage
- **Symptoms:** Gunicorn workers or containers consume excessive resources.
- **Investigate:** Profile endpoints with APM (New Relic, Datadog) or `top`/`htop`.
- **Mitigate:**
  - **Horizontal scaling:** Increase replicas behind a load balancer.
  - **Worker recycling:** `--max-requests 1000 --max-requests-jitter 50` to avoid memory bloat.

### 4.2 Disk Space Issues
- **Symptoms:** Deployment fails or disk fills up quickly.
- **Solutions:**
  - **Log rotation:** Configure `logrotate` for NGINX, Gunicorn, and chat logs.
  - **Docker cleanup:** `docker system prune -a` (use with caution).
  - **Archive data:** Periodically snapshot or purge old FAISS indexes and logs.

---

## 5. Database & Persistence

### 5.1 SQLite Corruption
- **Symptoms:** `sqlite3` errors reading/writing to `users.db` or memory DBs.
- **Fixes:**
  - **Concurrency:** Avoid simultaneous writes; consider moving to PostgreSQL/MySQL for production.
  - **Repair:** `sqlite3 users.db "REINDEX;"` or restore from backups.

### 5.2 FAISS Index Errors
- **Symptoms:** FAISS load failures on network-mounted volumes.
- **Solutions:**
  - **Local storage:** Place vectorstores on local SSD for performance and reliability.
  - **Avoid NFS:** Network filesystems can cause locking and latency issues.

---

## 6. Monitoring & Alerts

- **Gunicorn exporter:** Use a Prometheus exporter for Gunicorn metrics.  
- **NGINX stub_status:** Enable basic metrics endpoint.  
- **Docker HEALTHCHECK:** Define health checks in your `Dockerfile`.  
- **Alerts:** Configure thresholds for error rates, CPU usage, and latency in your monitoring system.

---

## 7. Logging & Debugging

- **Central logging:** Aggregate Gunicorn, NGINX, and app logs to ELK/EFK or cloud logging.  
- **Debug mode:** Never use `debug=True` in production—only in local development.  
- **Verbose logs:** Temporarily increase log level: `--log-level debug` in Gunicorn or Flask for deeper insights.

---

With these pointers, your Maeser deployment should run smoothly. If you encounter other issues, check the GitHub Issues board or open a topic for community support.


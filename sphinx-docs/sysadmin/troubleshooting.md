# SysAdmin Troubleshooting Guide

*Quick reference for resolving common issues in Maeser production deployments.*

---

## Gunicorn (WSGI Server) Issues

### Failing to Start

- **Symptoms:** `ModuleNotFoundError` or `AttributeError` referencing your app.
- **Checks & Fixes:**
  1. **Module path:** Ensure you launch Gunicorn with the correct module notation (e.g., `example.flask_example_user_management:app`).
  2. **Virtual environment:** Activate the same `.venv` where Maeser and Gunicorn are installed.
  3. **Installation:** Verify Gunicorn is present (`pip show gunicorn`). Install if missing: `pip install gunicorn`.

### Worker Timeouts & Hangs

- **Symptoms:** Requests hang or time out after 30 seconds (default).
- **Solutions:**
  - **Increase timeout:** `--timeout 120` or higher.
  - **Preload app:** Add `--preload` to reduce per-worker startup cost.
  - **Error logs:** Specify `--error-logfile /path/to/error.log` and inspect stack traces.

### Port Binding Conflicts

- **Symptoms:** `OSError: [Errno 98] Address already in use`.
- **Solutions:**
  - **Identify process:** `lsof -i :8000` or `netstat -tnlp | grep 8000`.
  - **Free port:** Stop the conflicting service or choose a different port.
  - **Socket binding:** Use Unix socket for NGINX proxy: `--bind unix:/path/to/maeser.sock`.

---

## NGINX (Reverse Proxy) Issues

### 502 Bad Gateway

- **Symptoms:** NGINX returns a 502 error when proxying.
- **Checks & Fixes:**
  - **Backend status:** Confirm Gunicorn is running and listening on the expected socket/port.
  - **Proxy settings:** Match `proxy_pass` URL to Gunicorn bind (e.g., `http://127.0.0.1:8000` or `unix:/…`).
  - **Socket permissions:** `chown www-data:www-data maeser.sock && chmod 660 maeser.sock`.

### SSL/TLS Certificate Errors

- **Symptoms:** Browser warnings about invalid or expired certificate.
- **Solutions:**
  - **Test renewal:** `sudo certbot renew --dry-run`.
  - **Verify paths:** Ensure NGINX `ssl_certificate` and `ssl_certificate_key` point to the correct files under `/etc/letsencrypt/live/yourdomain.com/`.
  - **Reload NGINX:** After renewal, run `sudo systemctl reload nginx`.

### Static Assets Not Loading

- **Symptoms:** CSS/JS requests return 404.
- **Checks & Fixes:**
  - **Alias config:** Confirm `location /static/ { alias /path/to/maeser/controllers/common/static/; }` matches your file structure.
  - **File permissions:** Ensure the NGINX user (`www-data`) can read static files (`chmod -R u+r /path/to/static`).

---

## Resource & Performance

### High CPU / Memory Usage

- **Symptoms:** Gunicorn workers or containers consume excessive resources.
- **Investigate:** Profile endpoints with APM (New Relic, Datadog) or `top`/`htop`.
- **Mitigate:**
  - **Horizontal scaling:** Increase replicas behind a load balancer.
  - **Worker recycling:** `--max-requests 1000 --max-requests-jitter 50` to avoid memory bloat.

### Disk Space Issues

- **Symptoms:** Deployment fails or disk fills up quickly.
- **Solutions:**
  - **Log rotation:** Configure `logrotate` for NGINX, Gunicorn, and chat logs.
  - **Docker cleanup:** `docker system prune -a` (use with caution).
  - **Archive data:** Periodically snapshot or purge old FAISS indexes and logs.

---

## Database & Persistence

### SQLite Corruption

- **Symptoms:** `sqlite3` errors reading/writing to `users.db` or memory DBs.
- **Fixes:**
  - **Concurrency:** Avoid simultaneous writes; consider moving to PostgreSQL/MySQL for production.
  - **Repair:** `sqlite3 users.db "REINDEX;"` or restore from backups.

### FAISS Index Errors

- **Symptoms:** FAISS load failures on network-mounted volumes.
- **Solutions:**
  - **Local storage:** Place vector stores on local SSD for performance and reliability.
  - **Avoid NFS:** Network filesystems can cause locking and latency issues.

---

## Monitoring & Alerts

- **Gunicorn exporter:** Use a Prometheus exporter for Gunicorn metrics.  
- **NGINX stub_status:** Enable basic metrics endpoint.  
- **Docker HEALTHCHECK:** Define health checks in your `Dockerfile`.  
- **Alerts:** Configure thresholds for error rates, CPU usage, and latency in your monitoring system.

---

## Logging & Debugging

- **Central logging:** Aggregate Gunicorn, NGINX, and app logs to ELK/EFK or cloud logging.  
- **Debug mode:** Never use `debug=True` in production—only in local development.  
- **Verbose logs:** Temporarily increase log level: `--log-level debug` in Gunicorn or Flask for deeper insights.

---

With these pointers, your Maeser deployment should run smoothly. If you encounter other issues, check the GitHub Issues board or open a topic for community support.

SysAdmin Troubleshooting Guide

This guide helps system administrators diagnose and resolve common issues in Maeser production deployments, including WSGI server problems, reverse proxy configurations, certificate errors, container issues, and performance bottlenecks.

1. WSGI Server (Gunicorn) Issues

1.1 Gunicorn Failing to Start

Symptom: ModuleNotFoundError for application module or attribute.

Checks:

Confirm the module path is correct: e.g., example.flask_example_user_mangement:app.

Activate the same virtual environment used for development.

Ensure gunicorn is installed in the virtual environment (pip show gunicorn).

1.2 Worker Timeouts & Hangs

Symptom: Requests timing out after default 30s or workers becoming unresponsive.

Solutions:

Increase --timeout value: gunicorn --timeout 120 ....

Reduce application startup work (e.g., lazy loading): add --preload to preload application before forking.

Monitor worker logs (error-logfile) for stack traces.

1.3 Port Binding Conflicts

Symptom: OSError: [Errno 98] Address already in use.

Solutions:

Check for existing processes on the port: lsof -i :8000 or netstat -tnlp | grep 8000.

Stop or reconfigure conflicting service, or choose a different port.

Use Unix socket binding for NGINX proxying: --bind unix:/path/to/maeser.sock.

2. Reverse Proxy (NGINX) Issues

2.1 502 Bad Gateway

Symptom: NGINX returns 502 when proxying to Gunicorn.

Checks & Fixes:

Ensure Gunicorn is running and bound to the correct socket or port.

Verify proxy_pass matches Gunicorn bind (unix:/… vs http://127.0.0.1:8000).

Check file ownership and permissions of the Unix socket: chown www-data:www-data maeser.sock and chmod 660 maeser.sock.

2.2 SSL/TLS Certificate Errors

Symptom: Browser warns of invalid or expired certificate.

Solutions:

Run sudo certbot renew --dry-run to test renewal.

Verify certificate paths in NGINX config match live/yourdomain.com/fullchain.pem and privkey.pem.

Reload NGINX after renewal: sudo systemctl reload nginx.

2.3 Static Assets Not Served

Symptom: CSS/JS not loading, 404 on /static/... URLs.

Checks:

Verify alias directive in NGINX points to the correct maeser/controllers/common/static/ folder.

Confirm NGINX user has read permissions on static files.

3. Docker & Container Issues

3.1 Build Failures

Symptom: Errors during docker build related to missing files or dependencies.

Fixes:

Ensure COPY . /app includes all necessary files (watch for .dockerignore).

Confirm base image supports required Python version and system tools.

3.2 Container Networking

Symptom: Cannot access service on localhost:8000 from host or other containers.

Solutions:

Check ports mapping in docker-compose.yml: 8000:8000.

Use network_mode: host for direct host networking (not recommended for production).

Ensure EXPOSE in Dockerfile is set, though not strictly required.

3.3 Volume & File Permissions

Symptom: Container logs show permission denied when writing to volumes (e.g., chat logs, SQLite DB).

Fixes:

Set proper UID/GID in container to match host directory owner, or adjust permissions on host: chown -R 1000:1000 ./data.

Use Docker Compose user: "1000:1000" to run container processes as non-root user.

4. System Resource & Performance

4.1 High CPU/Memory Usage

Symptom: Gunicorn workers or containers consuming excessive resources.

Investigations:

Profile endpoints causing spikes (use APM like New Relic or logging).

Check top or htop inside container/host to identify processes.

Mitigations:

Scale horizontally: increase worker count or deploy multiple instances behind a load balancer.

Enable worker recycling: add --max-requests 1000 --max-requests-jitter 50 to Gunicorn.

4.2 Disk Space Issues

Symptom: Deployment fails due to no space, or logs filling up disk.

Solutions:

Rotate application and system logs using logrotate.

Clean old Docker images/containers: docker system prune -a (beware data loss).

Archive or purge old chat logs and vectorstore snapshots.

5. Database & Persistence

5.1 SQLite Corruption

Symptom: Errors reading/writing to users.db or memory DBs.

Fixes:

Check for concurrent writes; switch to file locking or migrate to PostgreSQL/MySQL for high concurrency.

Backup and recreate the DB if corrupted: sqlite3 users.db "REINDEX;" or restore from backup.

5.2 Vectorstore Access

Symptom: FAISS index load errors on NFS or network storage.

Solutions:

Move vectorstore directories to local SSD storage.

Avoid network file systems for performance-sensitive indexes.

6. Monitoring & Alerts

Gunicorn Metrics: Use Prometheus Gunicorn exporter to track worker metrics.

Nginx Status: Enable stub_status in NGINX for basic request metrics.

Container Health Checks: Define HEALTHCHECK in Dockerfile to automatically restart unhealthy containers.

Alerting: Set up alerts for high error rates, CPU spikes, disk usage, or slow responses in your monitoring stack.

7. Logging & Debugging

Centralized Logging: Push Gunicorn, NGINX, and application logs to ELK/EFK stacks or cloud logging services.

Debug Mode: Never run with debug=True in production; use it only in local environments.

Verbose Logging: Temporarily increase log level in Gunicorn (--log-level debug) or Flask for detailed tracebacks.



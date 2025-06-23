<!-- Ayden here - I have left some comments here on areas where this documentation page can be improved. -->

# Deployment Guide

While Flask makes it easy to test your Maeser project locally, deploying your Flask app publicly is a layered process. Flask handles the functionality of your application, but it is not a server in of itself. For full functionality, a [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) server program is need to serve your application. A typical Flask-based server connects a flask app to a WSGI server, which communicates with an HTTP server by a "reverse proxy" protocol. See [Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/) from Flask's official documentation for more information.

**By following this guide, you will:**

1. [**Configure your app for deployment**](#configure-your-app-for-deployment)
2. **Run your app as a WSGI server** <!--TODO-->
3. **Use reverse-proxy to host your server with HTTP** <!--TODO-->
4. **Deploy your server publicly with a domain name** <!--TODO-->

---

## Prerequisites

- A production server or cloud instance (e.g., AWS EC2, Azure VM, Google Compute Engine) running a linux OS (Ubuntu, Debian, etc.).
- A Maeser application that is setup and working locally. See either the [User Setup](../user-setup/user_setup.md) or [Development Setup](../development-setup/development_setup.md) workflows.
- Domain name and DNS access for configuring TLS certificates.

---

## Configure Your App for Deployment

Not much needs to be changed within the application itself; however, if you have been working on your app from the `example/` directory, it is recommended that you restructure your project to include only the files that your application needs and remove the `example_` prefix from any remaining files. If you follow this recommendation, keep in mind that `config_example.py` looks for these specific paths:
```python
    config_paths = [
        'config_example.yaml',
        './config_example.yaml',
        'example/config_example.yaml'
    ]
```
These paths should be updated to match the path and name of your app's `config.yaml` file.

Additionally, if you have created your Maeser project using the [Development Setup Guide](../development-setup/development_setup.md), the Maeser package is located in the `maeser/` directory by default. Rather than having this package copied within your project, you should instead consider using the official Maeser PyPI package. Making this change is simple:
1. In your project's virtual environment, execute the following command:  
```bash
pip install maeser
```
2. Once the package is installed successfully, remove the `maeser/` directory from your project.
3. All done! Your project should be referencing Maeser functions from the PyPI package instead of `maeser/`.

---

## Using Gunicorn as WSGI Server

Gunicorn provides a robust, multi‑worker Python WSGI server for Flask apps.
<!-- Consider explaining what WSGI is -->
<!-- Let the user know that they need to reconfigure their github app both online and in config_example.yaml -->

1. **Start Gunicorn** with multiple workers:
   ```bash
   gunicorn \
     --workers 4 \
     --bind 0.0.0.0:8000 \
     --timeout 120 \
     example.flask_example_user_mangement:app
   ```
2. **Background Process**: Use a process manager (systemd, Supervisor) to keep Gunicorn running.

### systemd Service Example

<!-- Explain what a service file is and what this configuration does -->
<!-- Explain what a .sock is and why we're using it here instead of 0.0.0.0:8000 -->

Create `/etc/systemd/system/maeser.service`:
```ini
[Unit]
Description=Maeser Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Maeser
ExecStart=/path/to/Maeser/.venv/bin/gunicorn --workers 4 --bind unix:/path/to/Maeser/maeser.sock example.flask_example_user_mangement:app
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

## Reverse Proxy with NGINX & TLS

<!-- Explain what these things are -->
<!-- Note: I ran into a plethora of issues trying to get this to work with nginx using a web socket. This section needs to be looked at in further detail.-->

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

## Containerization with Docker & Docker Compose

<!-- Explain the purpose of Docker briefly -->

### Dockerfile Example

```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -e . && pip install gunicorn
EXPOSE 8000
env OPENAI_API_KEY=<your-key>
CMD ["gunicorn", "example.flask_example_user_mangement:app", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml Example

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

## Scaling & High Availability

- **Horizontal Scaling**: Deploy multiple Gunicorn containers behind a load balancer (e.g., AWS ELB, NGINX upstream).  
- **Session Storage**: Use centralized memory store (Redis) or persistent DB for session state and chat logs.  
- **Container Orchestration**: Use Kubernetes, Docker Swarm, or ECS/EKS to manage replicas, auto‑scaling, and rolling updates.

---

## Monitoring & Logging

- **Application Logs**: Configure Gunicorn `--access-logfile` and `--error-logfile` options.  
- **Chat Logs**: Ensure `ChatLogsManager` is writing to a persistent volume or external storage.  
- **Monitoring Tools**: Integrate Prometheus/Grafana for metrics (CPU, memory, request latency).  
- **Alerts**: Set up alerts for high error rates or API quota exhaustion.

---

## Backup & Maintenance

- **Database Backups**: Schedule regular dumps of `USERS_DB_PATH` and chat logs.  
- **Vectorstore Snapshots**: Archive FAISS indexes after embedding runs to prevent data loss.  
- **Certificate Renewal**: Automate Let’s Encrypt renewals with `certbot renew --quiet` in a cron job.



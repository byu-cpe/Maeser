<!-- Ayden here - I have left some comments here on areas where this documentation page can be improved. -->

# Deployment Guide

While Flask makes it easy to test your Maeser project locally, deploying your Flask app publicly is a layered process. Flask handles the functionality of your application, but it is not a server in of itself. For full functionality, a [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) server program is need to serve your application. A typical Flask-based server connects a flask app to a WSGI server, which communicates with an HTTP server by a "reverse proxy" protocol. See [Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/) from Flask's official documentation for more information.

**By following this guide, you will:**

1. [**Configure your app for deployment**](#configure-your-app-for-deployment)
2. [**Configure a WSGI server to run your app**](#configure-a-wsgi-server-to-run-your-app)
3. [**Use reverse-proxy to host your server with HTTP**](#use-reverse-proxy-to-host-your-server-with-http)
4. [**Run your web server as a Linux service (optional)**](#run-your-web-server-as-a-linux-service-optional)
5. [**Deploy your server publicly with a domain name**](#deploy-your-server-publicly-with-a-domain-name)

Because there are several ways to accomplish these steps, this guide will not explicitly explain how to get everything set up but will instead provide resources that explain how to set things up for your preferences. The Maeser app has been tested to work with [Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/) for WSGI server creation and [nginx](https://flask.palletsprojects.com/en/stable/deploying/nginx/) for reverse proxy, but feel free to choose any of Flask's [reccomended programs for deployment](https://flask.palletsprojects.com/en/stable/deploying/#self-hosted-options) if they work better for your needs.

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
3. All done! Your project should now reference Maeser functions from the PyPI package instead of from `maeser/`. Run your project locally to make sure these changes were successful.

---

## Configure a WSGI Server to Run Your App

> "Flask is a WSGI application. A WSGI server is used to run the application, converting incoming HTTP requests to the standard WSGI environ, and converting outgoing WSGI responses to HTTP responses."  
> —[Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/), Flask Documentation

While Flask does have a development server that allows the app to be run locally, a separate program is required to run the application as a production WSGI server.

Consult the list of [Self-Hosted Options](https://flask.palletsprojects.com/en/stable/deploying/#self-hosted-options) from Flask's deployment guide to start setting up your own WSGI server. Each of these options link to a guide on how to set them up and test them locally. Maeser has been tested to work with [Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/), but any of the listed options should work.

Keep in mind that if you are using Github authentication, you will need to update the `Homepage URL` and `Authorization callback URL` within the settings of your OAuth app. As a reminder, this is accessible via the [Developer Settings page](https://github.com/settings/developers) on GitHub. Be sure to also update `github_callback_uri` in your project's `config.yaml`. If you are using other authentication methods, they will likely need to be updated as well. These settings will need to be updated again after you [set up a reverse proxy](#use-reverse-proxy-to-host-your-server-with-http) for your WSGI server.

## Use Reverse-Proxy to Host Your Server with HTTP

> "WSGI servers have HTTP servers built-in. However, a dedicated HTTP server may be safer, more efficient, or more capable. Putting an HTTP server in front of the WSGI server is called a 'reverse proxy.'"  
> —[Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/), Flask Documentation

Running your WSGI server with a reverse proxy is standard for Flask apps and is relatively straightforward. [nginx](https://flask.palletsprojects.com/en/stable/deploying/nginx/) is one of the most commonly used HTTP servers and has been tested to work with Maeser. The official flask guide recommends using either [nginx](https://flask.palletsprojects.com/en/stable/deploying/nginx/) or [Apache httpd](https://flask.palletsprojects.com/en/stable/deploying/apache-httpd/) for setting up the reverse proxy, so follow the guide for either service and you should have a functioning HTTP server in no time.

Once your http server is configured, follow the guide to [Tell Flask it is Behind a Proxy](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/). This will involve making a slight modification to your project's main python script. Be sure to update your OAuth settings (as described [above](#configure-a-wsgi-server-to-run-your-app)) since the web server is now accessed through the HTTP server. Your Flask app should now be fully functional and accessible via reverse-proxy.

---

## Run Your Web Server as a Linux Service (Optional)

A **Linux systemctl service** is a service that runs in the background (also known as a **daemon**). By creating a service to run your web server, you can more easily control when the server should start, stop, and restart, without needing to control the service manually in a terminal session.

To create a Linux service for your web server, navigate to `/etc/systemd/system/` and create a file `my-Maeser-app.service`, replacing `my-maeser-app` with whatever you would like the service to be called. This file is where the configuration for your service will be stored. There are many ways to configure a Linux service, but the following configuration has proven to work well with a Maeser application:

```ini
[Unit]
Description=My Maeser WSGI Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/maeser/app
ExecStart=/path/to/maeser/app/.venv/bin/gunicorn -w 16 --access-logfile=- 'gmtk_flask:app'
Restart=always

[Install]
WantedBy=multi-user.target
```

Save this to your `my-maeser-app.service` file, and run `sudo systemctl daemon-reload`. This will reload the configurations for all daemons on your machine, which will allow systemctl to recognize the new maeser service.

> **Note:** If you make changes to your service file in the future, always be sure to run `sudo systemctl daemon-reload` afterward.

To start your service, run `sudo systemctl start my-maeser-app.service`, or equivalently, `sudo systemctl start my-maeser-app`. To confirm that it started successfully and is running, run `sudo systemctl status my-maeser-app.service`. If all is well, you should see something similar to the following:
```
● my-maeser-app.service - My Maeser WSGI Server
     Loaded: loaded (/etc/systemd/system/my-maeser-app.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-07-08 16:59:05 MDT; 18h ago
     ...
```

If your service is "**active (running)**", then you are all set! You should be able to access your server in a web browser just as before.

> **Note:** To see a live feed of your service's logs, you can use `journalctl`. Run the following command in its own terminal session:
> ```bash
> sudo journalctl -fu my-maeser-app.service
> ```
> The terminal window will now show the live output of your webserver.

---

## Deploy your server publicly with a domain name

<!--TODO-->

<!-- Old Docker Section
## Containerization with Docker & Docker Compose

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
-->
<!-- Other Old Sections
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
-->

<!-- Additional sections worth adding:
- Creating a service file to run the wsgi app
- using a unix socket for reverse proxy instead of a port
 -->

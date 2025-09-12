# SysAdmin Troubleshooting Guide

This guide serves as a quick reference for resolving issues in Maeser production deployments.

Since there are many different deployment setups, this guide is generalized and does not provide a comprehensive list of problems and solutions; for more detailed troubleshooting, refer to the documentation for your WSGI and HTTP server programs.

---

## WSGI Server Issues

### Failing to Start

- **Symptoms:** `ModuleNotFoundError` or `AttributeError` referencing your app.
- **Solutions:**
  1. **Module path:** Ensure you launch your WSGI server with the correct module notation (e.g., `example.flask_example_user_management:app`).
  2. **Virtual environment:** Make sure the path to your WSGI program is in your project's virtual environment (e.g., `.venv/bin/...`).

### Port Binding Conflicts

- **Symptoms:** `OSError: [Errno 98] Address already in use`.
- **Solutions:**
  - **Free port:** Stop the conflicting service or choose a different port.

---

## HTTP/Reverse Proxy Issues

### 502 Bad Gateway

- **Symptoms:** HTTP server returns a 502 error when proxying.
- **Solutions:**
  - **Backend status:** Confirm your WSGI program is running and listening on the expected port or socket.
  - **Proxy settings:** Make sure that the proxy pass URL in the HTTP server (named `proxy_pass` in nginx) is assigned to the same port that the WSGI server is bound to (usually `http://127.0.0.1:8000/` by default).
  - **Socket permissions:** If you are using a Unix socket to connect your WSGI and HTTP server, make sure that `www-data` is configured with proper permissions by executing the following: `chown www-data:www-data maeser.sock && chmod 660 maeser.sock`

### SSL/TLS Certificate Errors

- **Symptoms:** Browser warnings about invalid or expired certificate.
- **Solutions:**
  - **Renew Certificates:** Verify the status of your certificates and renew them if necessary.
  - **Verify paths:** Ensure HTTP server's config is up-to-date with correct paths to the `ssl_certificate` and `ssl_certificate_key`.
  - **Reload NGINX:** After renewal, run `sudo systemctl reload nginx`.

### Static Assets Not Loading

- **Symptoms:** CSS/JS requests return 404.
- **Solutions:**
  - **File permissions:** Ensure the HTTP user (`www-data`) can read static files (`chmod -R u+r /path/to/static`).

---

## Database & Persistence

### Vector Store/FAISS Index Errors

- **Symptoms:** FAISS load failures on network-mounted volumes.
- **Solutions:**
  - **Local storage:** Place vector stores on local SSD for performance and reliability.
  - **Avoid NFS:** Network filesystems can cause locking and latency issues.

---

If you encounter other issues, review the steps and resources in the [**Deployment Guide**](./deployment.md), or consider [**submitting an issue on GitHub**](https://github.com/byu-cpe/Maeser/issues).

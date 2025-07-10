<!-- Ayden here - I have left some comments here on areas where this documentation page can be improved. -->

# Deployment Guide

While Flask makes it easy to test your Maeser project locally, deploying your Flask app publicly is a layered process. Flask handles the functionality of your application, but it is not a server in and of itself. For full functionality, a [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) server program is needed to serve your application. A typical Flask-based server connects a Flask app to a WSGI server, which communicates with an HTTP server by a "reverse proxy" protocol. See [Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/) from Flask's official documentation for more information.

**By following this guide, you will:**

1. [**Configure your app for deployment**](#configure-your-app-for-deployment)
2. [**Configure a WSGI server to run your app**](#configure-a-wsgi-server-to-run-your-app)
3. [**Use reverse proxy to host your server with HTTP**](#use-reverse-proxy-to-host-your-server-with-http)
4. [**Run your web server as a Linux service (optional)**](#run-your-web-server-as-a-linux-service-optional)
5. [**Deploy your server publicly with a domain name**](#deploy-your-server-publicly-with-a-domain-name)

Because there are several ways to accomplish these steps, this guide will not explicitly explain how to get everything set up, but will instead provide resources that explain how to set things up for your preferences. The Maeser app has been tested to work with [**Gunicorn**](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/) for WSGI server creation and [**nginx**](https://flask.palletsprojects.com/en/stable/deploying/nginx/) for reverse proxy, but feel free to choose any of Flask's [recommended programs for deployment](https://flask.palletsprojects.com/en/stable/deploying/#self-hosted-options) if they work better for your needs.

---

## Prerequisites

- A Maeser application that is set up and working locally. See either the [**User Setup**](../user-setup/user_setup.md) or [**Development Setup**](../development-setup/development_setup.md) workflows.
- A domain name and SSL/TLS certificate (explained in [**Deploy Your Server Publicly With a Domain Name**](#deploy-your-server-publicly-with-a-domain-name)).

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

Additionally, if you have created your Maeser project using the [**Development Setup Guide**](../development-setup/development_setup.md), the Maeser package is located in the `maeser/` directory by default. Rather than having this package copied within your project, you should instead consider using the official Maeser PyPI package. Making this change is simple:
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

While Flask does have a development server that allows the app to be run locally, a separate program is required to run the application as a **production WSGI server**.

Consult the list of [Self-Hosted Options](https://flask.palletsprojects.com/en/stable/deploying/#self-hosted-options) from Flask's deployment guide to start setting up your own WSGI server. Each of these options links to a guide on how to set them up and test them locally. Maeser has been tested to work with [**Gunicorn**](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/), but any of the listed options should work.

Keep in mind that if you are using GitHub authentication, you will need to update the **Homepage URL** and **Authorization callback URL** within the settings of your OAuth app. As a reminder, this is accessible via the [Developer Settings page](https://github.com/settings/developers) on GitHub. Be sure to also update `github_callback_uri` in your project's `config.yaml`. If you are using other authentication methods, they will likely need to be updated as well. These settings will need to be updated again after you [**set up a reverse proxy**](#use-reverse-proxy-to-host-your-server-with-http) for your WSGI server.

## Use Reverse Proxy to Host Your Server with HTTP

> "WSGI servers have HTTP servers built-in. However, a dedicated HTTP server may be safer, more efficient, or more capable. Putting an HTTP server in front of the WSGI server is called a 'reverse proxy.'"  
> —[Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/), Flask Documentation

Running your WSGI server with a **reverse proxy** is standard for Flask apps and is relatively straightforward. [**nginx**](https://flask.palletsprojects.com/en/stable/deploying/nginx/) is one of the most commonly used HTTP servers and has been tested to work with Maeser. The official Flask guide recommends using either [**nginx**](https://flask.palletsprojects.com/en/stable/deploying/nginx/) or [**Apache httpd**](https://flask.palletsprojects.com/en/stable/deploying/apache-httpd/) for setting up the reverse proxy, so follow the guide for either service and you should have a functioning HTTP server in no time.

Once your HTTP server is configured, follow the guide to [**Tell Flask it is Behind a Proxy**](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/). This will involve making a slight modification to your project's main Python script. Be sure to update your OAuth settings (as described [above](#configure-a-wsgi-server-to-run-your-app)) since the web server is now accessed through the HTTP server. Your Flask app should now be fully functional and accessible via reverse proxy.

---

## Run Your Web Server as a Linux Service (Optional)

A **Linux systemctl service** is a service that runs in the background (also known as a **daemon**). By creating a service to run your web server, you can more easily control when the server should start, stop, and restart, without needing to control the service manually in a terminal session.

To create a Linux service for your web server, navigate to `/etc/systemd/system/` and create a new file named `my-maeser-app.service`, replacing `my-maeser-app` with whatever you would like the service to be called. This **service file** is where the configuration for your service will be stored. There are many ways to configure a Linux service, but the following configuration has proven to work well with a Maeser application:

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

> **Note:** If you have configured your server with a different WSGI server program or with different arguments, update the `ExecStart=...` line accordingly, making sure that `/path/to/maeser/app/.venv/bin/gunicorn` is the path to your WSGI server program within your virtual environment's directory.

Save this to your `my-maeser-app.service` file, and run `sudo systemctl daemon-reload`. This will reload the configurations for all daemons on your machine, which will allow systemctl to recognize the new maeser service.

> **Note:** If you make changes to your service file in the future, always be sure to run `sudo systemctl daemon-reload` afterward.

Before starting the service, you will need to grant user `www-data` necessary file permissions for your Maeser app. If you wish to retain ownership of your app's directory, you can use `setfacl` to grant `www-data` read-write-execute access while also retaining your permissions. Run the following two commands:

```bash
sudo setfacl -R -m u:www-data:rwx /path/to/maeser/app
```

```bash
sudo setfacl -R -m -d u:www-data:rwx /path/to/maeser/app
```

The first command grants read-write-execute permissions for `www-data` for every file in your project directory. The second command sets these permissions as the default for files created in this directory in the future, so these commands only need to be run once.

> **Note:** You can use `getfacl` to check the permissions set for any file or directory.

To start your service, run `sudo systemctl start my-maeser-app.service`, or equivalently, `sudo systemctl start my-maeser-app`. To confirm that it started successfully and is running, run `sudo systemctl status my-maeser-app.service`. If all is well, you should see something similar to the following:
```
● my-maeser-app.service - My Maeser WSGI Server
     Loaded: loaded (/etc/systemd/system/my-maeser-app.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-07-08 16:59:05 MDT; 8s ago
     ...
```

If your service is "**active (running)**", then you are all set! You should be able to access your server in a web browser just as before. Your web server will now run in the background and will automatically start up when your machine starts up. You can manage your service in the following ways:
1. Start Service
  ```bash
  sudo systemctl start my-maeser-app.service
  ```

2. Stop Service
  ```bash
  sudo systemctl stop my-maeser-app.service
  ```

3. Restart Service
  ```bash
  sudo systemctl restart my-maeser-app.service
  ```

> **Note:** To see a live feed of your service's logs, you can use `journalctl`. Run the following command in its own terminal session:
> ```bash
> sudo journalctl -fu my-maeser-app.service
> ```
> The terminal window will now show the live output of your web server.

---

## Deploy Your Server Publicly With a Domain Name

There are three main things you will need to acquire to fully deploy your server:
1. **A domain name**
2. **An SSL/TLS certificate**
3. **A private key**

A **domain name** will need to be acquired from a [**domain name registrar**](https://en.wikipedia.org/wiki/Domain_name_registrar) — a company that registers domain names for a price (like [**Cloudflare**](https://www.cloudflare.com/products/registrar/), just as an example). Several registrars exist, so it is encouraged that you **do your own research** to find a domain name registrar that best fits your needs.

An **SSL/TLS certificate** and a **private key** are needed to upgrade your web server from HTTP to HTTPS, which encrypts messages between the user's web browser and the web server for added security. This certificate and key must be acquired from a **Certificate Authority (CA)**, such as [**Let's Encrypt**](https://letsencrypt.org/). There are many Certificate Authorities, and some offer certificates for free while others charge for them, so **do your own research** to find a Certificate Authority that best fits your needs.

> For more information on SSL/TLS Certificates, refer to [this article](https://aws.amazon.com/what-is/ssl-certificate/) by Amazon.

Once you have acquired your domain name, SSL certificate, and private key, you will need to configure your web server to work with them. For an nginx server, refer to its [documentation](https://nginx.org/en/docs/http/configuring_https_servers.html) on how to configure your HTTP server with SSL. Configuration will vary for other HTTP server applications.

Lastly, be sure to update your OAuth settings once more (as described [above](#configure-a-wsgi-server-to-run-your-app)) since the web server is now accessed through your site's domain name.

## Resources
- [**Deploying to Production**](https://flask.palletsprojects.com/en/stable/deploying/), Flask documentation
- The section on directives for a `.service file` from [**this DigitalOcean article**](https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files#the-service-section)
- Wikipedia article on [**Web Server Gateway Interface (WSGI)**](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
- Wikipedia article on [**Domain Name Registrars**](https://en.wikipedia.org/wiki/Domain_name_registrar)
- Amazon article on [**SSL/TLS Certificates**](https://aws.amazon.com/what-is/ssl-certificate/)

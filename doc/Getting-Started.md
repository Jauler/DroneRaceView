# Getting Started

This file is intended to help you get up and running with the website.
It does not although get into details on how to configure timer itself in order to get desired information being shown (I will write one, later if I am not lazy :P ).

## Prerequisites

### Direct network access

DroneRaceView requires direct network access to the timer in order to operate.
In case you are running the website on a machine which the timer is connected to - direct access should be available out-of-the-box.
Otherwise consider taking a look at [Establishing Wireguard Tunnel](doc/establishing-wireguard-tunnel.md)

### Docker and Docker compose

DroneRaceView is generally expected to be run in a dockerized environment, therefore one will require [Docker](https://www.docker.com/) and [Docker compose](https://docs.docker.com/compose/) to be correctly installed and configured.
Please seek respective installation guides to get it configured.
This getting-started guide will assume that CLI commands may be used for docker and docker compose.


### (Optional) Owning a domain

If you wish to setup the website publically - you may need to own a domain, but I will consider how to achieve that to be out-of-scope for this guide.


## Setup

### Step 1. Obtaining a clone of DroneRaceView

Wherever you are planning to run the website - acquire a clone of repository

```bash
git clone https://github.com/Jauler/DroneRaceView.git
```

Or you may download zip and extract it wherever convenient.

### Step 2. Configure DroneRaceView

A few configuration parameters are needed in order for drone race view to operate, therefore open up docker-compose.yml file in your favorite text editor and replace:
- `--url http://10.42.191:8000` with whatever the actual URL for accessing timer is. If setting up remote access - see [Establishing Wireguard Tunnel](doc/establishing-wireguard-tunnel.md)
- `--username <your username>` replace `<your username>` with the administrator's username for the RotorHazard timing system
- `--password <your password>` replace `<your password>` with the administrator's password for the RotorHazard timing system


### Step 3. Bringin the app up

Execute:
```bash
docker compose up -d --build
```

in order to bring the app up.

Once the app is up and running, you may obtain logs via `docker compose logs`, or access the website via `http://localhost:5000` on the machine which is running the website.

### Step 4. (Optional) setup reverse proxy with TLS

If website is publically accessible it is considered best practice to configure reverse proxy (like NGINX) which servers the publically accessible port and terminates the TLS encryption.

__Step 4.1: install required dependencies (assuming Debian/Ubuntu server)__

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

__Step 4.2: create nginx configuration file__

For example, if you are setting up to work on a domain "results.jauler.eu":
```bash
sudo nano /etc/nginx/sites-available/results.jauler.eu
```

And populate the file with the following contents:
```bash
server {
    listen 80;
    server_name results.jauler.eu;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Obviously do not forget to replace "results.jauler.eu" with your own domain.

__Step 4.3: Enable site on nginx__

```bash
sudo ln -s /etc/nginx/sites-available/results.jauler.eu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
Again, do not forget to replace results.jauler.eu with your own domain.

__Step 4.4: Obtain TLS keys from Lets-Encrypt initiative__

At this time the your domain must be configured to and pointing to the machine running the DroneRaceView
```bash
sudo certbot --nginx -d results.jauler.eu
```
Again, do not forget to replace results.jauler.eu with your own domain.

---

By now you should have your DroneRaceView website up and running.
You should be able to setup some classes and heats and see them visualized in `/heats` view.





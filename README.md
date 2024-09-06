![HONEYPOT-Logo](/assets/images/honeypot-logo-black-text.png)

A flexible, visually-oriented honeypot designed to monitor and log IP addresses, usernames, passwords, and commands from various protocols, with current support for SSH and HTTP. Built using Python.

# Install

**1) Clone the repository.**
`git clone https://github.com/AslamMahi/HoneyLogix_HoneyPot.git`

**2) Permissions.**
Navigate to the `HoneyLogix_HoneyPot` directory.

Ensure `main.py` has the correct permissions. (`chmod 755 main.py`)

**3) Key Generation.**

Create a new folder `static`. 

`mkdir static`

Navigate into this directory.

`cd static`

Generate an RSA key for the SSH server host key. Ensure the key is named `server.key` and is located in the same directory as the main program.

`ssh-keygen -t rsa -b 2048 -f server.key`

# Usage

To start a new instance of HoneyLogix, use the `honeypot.py` file. This is the main file to interface with for HoneyLogix.

HoneyLogix requires a bind IP address (`-a`) and network port to listen on (`-p`). Use `0.0.0.0` to listen on all network interfaces. Also, specify the protocol type.

```
-a / --address: Bind address.
-p / --port: Port.
-s / --ssh OR -wh / --http: Declare honeypot type.
```

Example: `python3 honeypot.py -a 0.0.0.0 -p 22 --ssh`

💡 If HoneyLogix is set to listen on a privileged port (22), run the program with `sudo` or root privileges. Ensure no other services are using the specified port.

If port 22 is used for listening, change the default SSH port. Refer to Hostinger's "[How to Change the SSH Port](https://www.hostinger.com/tutorials/how-to-change-ssh-port-vps)" guide.

**Optional Arguments**

Specify a username (`-u`) and password (`-w`) for SSH server authentication. By default, the configuration accepts all usernames and passwords.


```
-u / --username: Username.
-w / --password: Password.
-t / --tarpit: For SSH-based honeypots, -t can be used to trap sessions inside the shell, by sending a 'endless' SSH banner.
```

Example: `python3 honeypot.py -a 0.0.0.0 -p 22 --ssh -u admin -w admin --tarpit`

# Logging Files

HoneyLogix has three loggers configured. Logs will be routed to `cmd_audits.log`, `creds_audits.log` (for SSH), and `http_audit.log` (for HTTP) for capturing information.

`cmd_audits.log`: Captures IP address, username, password, and all commands supplied.

`creds_audits.log`: Captures IP address, username, and password, comma-separated. Used to track how many hosts attempt to connect to HoneyLogix.

`http_audit.log`: Captures IP address, username, and password.

# Honeypot Types

HoneyLogix was designed with modularity in mind to support various honeypot types (Telnet, HTTPS, SMTP, etc). Currently, two honeypot types are supported.

## SSH
HoneyLogix initially supports SSH. Follow the instructions above to set up an SSH-based honeypot that emulates a basic shell.

💡 `-t / --tarpit`: A tarpit slows down or delays attackers trying to brute-force login credentials. Using Python's time module, a long SSH banner is sent to the connecting shell session. The only way out is to close the terminal.

## HTTP
HoneyLogix uses Python Flask to create a simple web service, impersonating a default WordPress `wp-admin` login page. Username/password pairs are collected.

Default credentials `admin` and `deeboodah` will trigger a Rick Roll gif. Username and password can be changed using the `-u / --username` and `-w / --password` arguments.

The web-based honeypot runs on port 5000 by default. This can be adjusted with the `-p / --port` flag.

💡 Currently, there is no dashboard for HTTP-based results. This will be a future addition.

# Dashboard

HoneyLogix includes a `web_app.py` file. Run this in a separate terminal session on localhost to view statistics such as top 10 IP addresses, usernames, passwords, commands, and all data in tabular format. Note that dashboards do not dynamically update; they need to be rerun to reflect the most current information.

Run `python3 web_app.py` on localhost. The default port for Python Dash is `8050`. Access the dashboard at `http://127.0.0.1:8050`.

💡 The dashboard includes a country code lookup using the IP address. The [ipinfo() CleanTalk API](https://cleantalk.org/help/api-ip-info-country-code) is used for this. Due to rate limiting, only 1000 IP addresses can be looked up per 60 seconds. By default, country code lookup is set to `False` to avoid impacting performance. Set the `COUNTRY` environment variable to `True` for country code lookup.

HoneyLogix uses Python Dash for charts, Dash Bootstrap Components for dark-theme styling, and Pandas for data parsing.

<img src="/assets/images/Dashboard.PNG" alt="Dashboard" width="600"/>

# VPS Hosting (General Tips)

To host on a VPS, follow these general tips.

Using a Virtual Private Server (VPS) is recommended for gathering logging information. VPSes are cloud-based hosts with Internet access, providing a secure, isolated way to collect real-time data.

Ensure to open the following ports for HoneyLogix:
- `Port 80`, `Port 5000`, `Port 2223` (or your configured SSH port), `Port 8050`. 

For Linux-based distributions, also open the ports with IP Tables or Unfiltered Firewall (UFW). 
- `ufw enable`
- `ufw allow [port]`

# Running in Background With Systemd

To run HoneyLogix in the background, you can use Systemd on popular Linux distributions.

A template is included in the `systemd` folder of this repository.

Supply the required arguments after `honeypot.py` in the configuration. Edit the configuration file as needed.
- `ExecStart=/usr/bin/python3 /honeypot.py -a 127.0.0.1 -p 22 --ssh`

Copy the `honeypot.service` template file to `/etc/systemd/system`. `cp honeypot.service /etc/systemd/system`.

Reload systemd with the new configuration using `systemctl daemon-reload`.

Enable the `honeypot.service` file with `systemctl enable honeypot.service`.

Start the `honeypot.service` file with `systemctl start honeypot.service`.

# Future Features

- Additional protocol support:
  - Telnet
  - HTTP ✅
  - HTTPS
  - SMTP
  - RDP
  - DNS
- Custom DNS support.
- Docker support for host-based isolation and deployment.
- Systemd support for running scripts in the background. ✅
- Create a basic overview Dashboard. ✅
- Dynamic Dashboard Updates.
- Dashboard hosted on a separate host for independent results.
- Add SSH Banner Tarpit to trap SSH sessions ✅ (`-t, --tarpit`)

# Helpful Resources

Resources and guides used during the development of this project.

- [Building an SSH Honeypot in Python and Docker](https://securehoney.net/blog/how-to-build-an-ssh-honeypot-in-python-and-docker-part-1.html) 
- [Building a Python Honeypot to Thwart Cyber Attackers](https://medium.com/@abdulsamie488/deceptive-defense-building-a-python-honeypot-to-thwart-cyber-attackers-2a9d2ced2760)
- [SSH Honeypot Script](https://gist.github.com/cschwede/3e2c025408ab4af531651098331cce45)
- [How to Change SSH Port on VPS](https://www.hostinger.com/tutorials/how-to-change-ssh-port-vps)

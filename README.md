<p align="center">
  <img src="/assets/images/honeypot4.png" alt="HONEYPOT-Logo" style="opacity:0.5; width: auto; height: auto;">
</p>

A flexible, visually-oriented honeypot designed to monitor and log IP addresses, usernames, passwords, and commands from various protocols, with current support for SSH and HTTP. Built using Python.

# HoneyLogix Setup Instructions

## 1. Clone the Repository

```bash
git clone https://github.com/AslamMahi/HoneyLogix_HoneyPot.git

```

## 2. Set Permissions

Ensure `honeypy.py` has the appropriate permissions:

```bash
cd HoneyLogix_HoneyPot
chmod 755 honeypy.py
```

## 3. Generate SSH Key

Create a new directory named `static`:

```bash
mkdir static
```

Move into this directory:

```bash
cd static
```

Generate an RSA key for the SSH server host key. Make sure the key is named server.key and is located in the static directory:

```bash
ssh-keygen -t rsa -b 2048 -f server.key
```

# Running HoneyLogix

To launch HoneyLogix, execute the honeypot.py file, which is the primary interface for managing the honeypot.
Basic Usage

HoneyLogix needs the following parameters to start:

Bind Address (-a): The IP address to bind the honeypot to. Use 0.0.0.0 to listen on all network interfaces.
Port (-p): The network port the honeypot will listen on.
Honeypot Type (-s or -wh): Specify the type of honeypot, such as SSH or HTTP.

Example command:

```bash
python3 honeypy.py -a 0.0.0.0 -p 22 --ssh
```

Note: If you choose to listen on a privileged port (like 22), you may need to run the script with sudo or as the root user. Ensure that no other services are using the same port.

For changing the default SSH port, consult Hostinger's How to Change the SSH Port guide.

## Additional Configuration Options

HoneyLogix allows for further customization with the following optional parameters:

Username (-u): Specifies a particular username for SSH authentication. If not provided, the honeypot will accept any username.

Example:

```
-u admin
```
Password (-w): Defines a specific password for SSH authentication. By default, the honeypot accepts any password.

Example:

```bash
-w password123
```
Tarpit (-t): Used with SSH honeypots to trap sessions within the shell. This option sends an 'endless' SSH banner, effectively keeping the connection open and preventing the session from completing.

Example:

```bash
-t
```

Example Usage

Combining these options, you can configure HoneyLogix to listen on a specific port with designated credentials and session handling:

```bash
python3 honeypot.py -a 0.0.0.0 -p 22 --ssh -u admin -w password123 -t
```

In this example:

    The honeypot listens on all network interfaces (0.0.0.0) on port 22.
    It uses SSH as the honeypot type.
    It requires the username admin and password password123.
    It traps sessions using the -t option.

# Log Management

HoneyLogix generates three types of log files to capture different aspects of interactions:

cmd_audits.log: This file records detailed information about SSH interactions, including the IP address, username, password, and all commands executed. It provides a comprehensive view of the commands attempted by attackers.

creds_audits.log: This log file captures connection attempts and authentication details, including IP address, username, and password, in a comma-separated format. It helps track the volume and details of connection attempts to HoneyLogix.

http_audit.log: Used for HTTP honeypots, this file logs IP address, username, and password. It provides insights into HTTP-based interactions and authentication attempts.

## Supported Honeypot Types

HoneyLogix is designed with modularity to accommodate different honeypot types. Currently, it supports the following types:

### SSH Honeypot

The SSH honeypot simulates an SSH service, providing a basic shell environment to interact with potential attackers.

- **Tarpit Mode (`-t`)**: When enabled, this mode introduces delays to hinder attackers attempting brute-force attacks. It uses Python's time module to send an extended SSH banner, trapping the connection until the attacker closes the terminal.

### HTTP Honeypot

The HTTP honeypot uses Python Flask to simulate a web service, specifically a default WordPress `wp-admin` login page, to capture login attempts.

- **Default Credentials**: The default username and password are `admin` and `deeboodah`, respectively. Logging in with these credentials will trigger a Rick Roll GIF.
- **Custom Credentials**: You can set your own username and password using the `-u / --username` and `-w / --password` options.

The HTTP honeypot listens on port 5000 by default, but this can be customized with the `-p / --port` flag.

# Dashboard

HoneyLogix includes a `web_app.py` file. Run this in a separate terminal session on localhost to view statistics such as top 10 IP addresses, usernames, passwords, commands, and all data in tabular format. Note that dashboards do not dynamically update; they need to be rerun to reflect the most current information.

Run `python3 web_app.py` on localhost. The default port for Python Dash is `8050`. Access the dashboard at `http://127.0.0.1:8050`.

💡 The dashboard includes a country code lookup using the IP address. The [ipinfo() CleanTalk API](https://cleantalk.org/help/api-ip-info-country-code) is used for this. Due to rate limiting, only 1000 IP addresses can be looked up per 60 seconds. By default, country code lookup is set to `False` to avoid impacting performance. Set the `COUNTRY` environment variable to `True` for country code lookup.

HoneyLogix uses Python Dash for charts, Dash Bootstrap Components for dark-theme styling, and Pandas for data parsing.

<img src="/assets/images/Dashboard1.png" alt="Dashboard" width="600"/>

# VPS Hosting (General Tips)

To host on a VPS, follow these general tips.

Using a Virtual Private Server (VPS) is recommended for gathering logging information. VPSes are cloud-based hosts with Internet access, providing a secure, isolated way to collect real-time data.

Ensure to open the following ports for HoneyLogix:
- `Port 80`, `Port 5000`, `Port 2223` (or your configured SSH port), `Port 8050`. 

For Linux-based distributions, also open the ports with IP Tables or Unfiltered Firewall (UFW). 
- `ufw enable`
- `ufw allow [port]`

# Running HoneyLogix as a Background Service with Systemd

To run HoneyLogix in the background using Systemd on popular Linux distributions, follow these steps:

1. **Locate the Systemd Service Template:**
   - A Systemd service template can be found in the `systemd` folder of this repository.

2. **Configure the Service:**
   - Update the `ExecStart` line in the template to match the location and arguments for `honeypot.py`. For example:
     ```bash
     ExecStart=/usr/bin/python3 /path/to/honeypot.py -a 127.0.0.1 -p 22 --ssh
     ```

3. **Install the Service File:**
   - Copy the `honeypot.service` template to the Systemd configuration directory:
     ```bash
     cp honeypot.service /etc/systemd/system/
     ```

4. **Apply the New Configuration:**
   - Reload Systemd to recognize the new service:
     ```bash
     systemctl daemon-reload
     ```

5. **Enable the Service:**
   - Set the service to start automatically on boot:
     ```bash
     systemctl enable honeypot.service
     ```

6. **Start the Service:**
   - Launch the HoneyLogix service:
     ```bash
     systemctl start honeypot.service
     ```

# Planned Features

- **Support for Additional Protocols:**
  - Telnet
  - HTTP ✔️
  - HTTPS
  - SMTP
  - RDP
  - DNS

- **Custom DNS Configuration**

- **Docker Integration:**
  - For host-based isolation and deployment.

- **Systemd Integration:**
  - For background script execution ✔️

- **Dashboard Enhancements:**
  - Basic Overview Dashboard ✔️
  - Dynamic Dashboard Updates
  - Separate host for independent Dashboard hosting

- **SSH Banner Tarpit:**
  - To trap SSH sessions (`-t, --tarpit`) ✔️




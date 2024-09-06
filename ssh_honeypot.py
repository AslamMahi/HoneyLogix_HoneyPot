# Import library dependencies.
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import threading
import socket
import time
from pathlib import Path

# Constants.
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"  # The banner string that the SSH server presents to clients.

# Get base directory of where user is running honeypy from.
base_dir = Path(__file__).parent.parent  # Determines the base directory for log and key files.
server_key = base_dir / 'ssh_honeypy' / 'static' / 'server.key'  # Path to the SSH server's private key.

# Log file paths.
creds_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'creds_audits.log'  # Log file for storing credentials attempts.
cmd_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'cmd_audits.log'  # Log file for storing commands executed.

# SSH Server Host Key.
host_key = paramiko.RSAKey(filename=server_key)  # Loads the server's private key for SSH.

# Logging Format.
logging_format = logging.Formatter('%(message)s')  # Defines the format for logging messages.

# Funnel (catch all) Logger.
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)  # Sets logging level to INFO.
funnel_handler = RotatingFileHandler(cmd_audits_log_local_file_path, maxBytes=2000, backupCount=5)  # Sets up rotating file logging.
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Credentials Logger. Captures IP Address, Username, Password.
creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)  # Sets logging level to INFO.
creds_handler = RotatingFileHandler(creds_audits_log_local_file_path, maxBytes=2000, backupCount=5)  # Sets up rotating file logging.
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# SSH Server Class. This establishes the options for the SSH server.
class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()  # Event object to signal channel readiness.
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED  # Allow session channel requests.

    def get_allowed_auths(self, username):
        return "password"  # Only password authentication is allowed.

    def check_auth_password(self, username, password):
        # Logs the attempted credentials and checks if they match expected values.
        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL  # If no credentials are specified, allow any.

    def check_channel_shell_request(self, channel):
        self.event.set()  # Signal that the channel is ready for interaction.
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True  # Allow pseudo-terminal requests.

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True  # Allow execution of commands.

def emulated_shell(channel, client_ip):
    # Simulates a shell environment for the client.
    channel.send(b"corporate-jumpbox2$ ")
    command = b""
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()
        command += char
        # Simulate responses to specific shell commands.
        if char == b"\r":
            if command.strip() == b'exit':
                response = b"\n Goodbye!\n"
                channel.close()
            elif command.strip() == b'pwd':
                response = b"\n" + b"\\usr\\local" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'ls':
                response = b"\n" + b"jumpbox1.conf" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b"\n" + b"Go to deeboodah.com" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()} executed by {client_ip}')
            else:
                response = b"\n" + bytes(command.strip()) + b"\r\n"
                funnel_logger.info(f'Command {command.strip()} executed by {client_ip}')
            channel.send(response)
            channel.send(b"corporate-jumpbox2$ ")
            command = b""

def client_handle(client, addr, username, password, tarpit=False):
    client_ip = addr[0]
    print(f"{client_ip} connected to server.")
    try:
        # Initializes a Transport object using the socket connection from client.
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER  # Set the SSH banner version.

        # Creates an instance of the SSH server, adds the host key, and starts the server.
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.add_server_key(host_key)
        transport.start_server(server=server)

        # Establishes a communication channel with the client.
        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")

        standard_banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"
        
        try:
            # Send a banner to the client.
            if tarpit:
                endless_banner = standard_banner * 100
                for char in endless_banner:
                    channel.send(char)
                    time.sleep(8)
            else:
                channel.send(standard_banner)
            # Redirect channel to emulated shell.
            emulated_shell(channel, client_ip=client_ip)

        except Exception as error:
            print(error)
    except Exception as error:
        print(error)
        print("!!! Exception !!!")
    
    finally:
        try:
            transport.close()  # Close the transport connection.
        except Exception:
            pass
        
        client.close()  # Close the client socket connection.

def honeypot(address, port, username, password, tarpit=False):
    # Set up a TCP socket and listen for incoming connections.
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    # Listen for up to 100 concurrent connections.
    socks.listen(100)
    print(f"SSH server is listening on port {port}.")

    while True: 
        try:
            client, addr = socks.accept()  # Accept an incoming client connection.
            # Handle the client connection in a new thread.
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password, tarpit))
            ssh_honeypot_thread.start()

        except Exception as error:
            print("!!! Exception - Could not open new client connection !!!")
            print(error)

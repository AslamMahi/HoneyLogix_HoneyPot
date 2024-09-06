# Import library dependencies.
from flask import Flask, render_template, request, redirect, url_for
import logging
from logging.handlers import RotatingFileHandler
from dashboard_data_parser import *  # Import custom dashboard data parser
from pathlib import Path

# Configure logging format.
logging_format = logging.Formatter('%(asctime)s %(message)s')

# Define the base directory and log file path.
base_dir = Path(__file__).parent.parent
http_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'http_audit.log'

# Set up HTTP logger.
funnel_logger = logging.getLogger('HTTPLogger')
funnel_logger.setLevel(logging.INFO)  # Set log level to INFO
funnel_handler = RotatingFileHandler(http_audits_log_local_file_path, maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Define the web honeypot application.
def baseline_web_honeypot(input_username="admin", input_password="deeboodah"):
    app = Flask(__name__)

    # Route for the home page.
    @app.route('/')
    def index():
        return render_template('wp-admin.html')  # Render the login page template

    # Route for handling login submissions.
    @app.route('/wp-admin-login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        ip_address = request.remote_addr

        # Log client information and credentials.
        funnel_logger.info(f'Client with IP Address: {ip_address} entered\n Username: {username}, Password: {password}')

        # Check credentials and return appropriate response.
        if username == input_username and password == input_password:
            return 'Please go to https://r.mtdv.me/gYVb1JYxGw'
        else:
            return "Invalid username or password, please try again."
        
    return app

# Function to run the Flask application.
def run_app(port=5000, input_username="admin", input_password="deeboodah"):
    app = baseline_web_honeypot(input_username, input_password)
    app.run(debug=True, port=port, host="0.0.0.0")  # Run the app on all IPs, on the specified port

    return app
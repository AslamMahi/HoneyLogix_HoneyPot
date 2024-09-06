# Import library dependencies.
import argparse  # Used for parsing command-line arguments.

# Import project python file dependencies. This is the main file to interface with the honeypot with.
from ssh_honeypot import *  # Contains functionality for running the SSH honeypot.
from web_honeypot import *  # Contains functionality for running the HTTP/web-based honeypot.
from dashboard_data_parser import *  # Handles parsing of data for the dashboard.
from web_app import *  # Manages running the web application (like HTTP honeypot, interface, or dashboard).

if __name__ == "__main__":
    # Create parser and add arguments.
    parser = argparse.ArgumentParser()  # Initialize the argument parser.
    
    # Define the required arguments for the script.
    parser.add_argument('-a','--address', type=str, required=True)  # IP address or hostname where the honeypot will run.
    parser.add_argument('-p','--port', type=int, required=True)  # Port number for the honeypot (e.g., SSH or HTTP).
    
    # Optional username and password for authentication.
    parser.add_argument('-u', '--username', type=str)  # Username for SSH or HTTP login, if applicable.
    parser.add_argument('-w', '--password', type=str)  # Password for SSH or HTTP login, if applicable.

    # Optional flags for the type of honeypot to run.
    parser.add_argument('-s', '--ssh', action="store_true")  # Flag to indicate running the SSH honeypot.
    parser.add_argument('-t', '--tarpit', action="store_true")  # Optional tarpit mode (slows down attackers).
    parser.add_argument('-wh', '--http', action="store_true")  # Flag to indicate running the HTTP/web honeypot.

    args = parser.parse_args()  # Parse the command-line arguments.

    # Parse the arguments based on user-supplied argument.
    try:
        # If the SSH honeypot is selected.
        if args.ssh:
            print("[-] Running SSH Honeypot...")
            # Call the honeypot function from ssh_honeypot module with the provided arguments.
            honeypot(args.address, args.port, args.username, args.password, args.tarpit)

        # If the HTTP honeypot is selected.
        elif args.http:
            print('[-] Running HTTP Wordpress Honeypot...')
            
            # Provide default username and password if none are supplied.
            if not args.username:
                args.username = "admin"  # Set default username to "admin" if not provided.
                print("[-] Running with default username of admin...")
            if not args.password:
                args.password = "deeboodah"  # Set default password if not provided.
                print("[-] Running with default password of deeboodah...")
            
            # Print the details of the HTTP honeypot.
            print(f"Port: {args.port} Username: {args.username} Password: {args.password}")
            # Call the function to run the web app honeypot on the specified port.
            run_app(args.port, args.username, args.password)
        
        # If neither SSH nor HTTP is selected, print an error message.
        else:
            print("[!] You can only choose SSH (-s) (-ssh) or HTTP (-h) (-http) when running script.")
    
    # Catch a keyboard interrupt (Ctrl+C) and exit gracefully.
    except KeyboardInterrupt:
        print("\nProgram exited.")
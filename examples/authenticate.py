"""
Example script demonstrating how to authenticate with the Veda API.
"""

import sys
import os

# Add the parent directory to sys.path to allow importing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from veda_client import VedaClient
from veda_client.utils import hash_password


def main():
    # Initialize the client
    client = VedaClient(base_url="http://example.com/api")
    
    # Get login credentials
    login = input("Enter your login: ")
    password = input("Enter your password: ")
    
    # Hash the password (if required by your Veda instance)
    hashed_password = hash_password(password)
    
    try:
        # Authenticate
        auth_response = client.authenticate(login=login, password=hashed_password)
        
        # Print the response
        print("\nAuthentication successful!")
        print(f"Ticket ID: {auth_response.get('id')}")
        print(f"User URI: {auth_response.get('user_uri')}")
        print(f"Session ends at: {auth_response.get('end_time')}")
        
        # Check if the ticket is valid
        is_valid = client.is_ticket_valid()
        print(f"\nTicket is valid: {is_valid}")
        
    except Exception as e:
        print(f"Authentication failed: {e}")


if __name__ == "__main__":
    main()

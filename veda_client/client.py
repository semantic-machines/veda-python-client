"""
Main client implementation for interacting with the Veda Platform API.
"""

import json
import requests
from typing import Dict, List, Optional, Union, Any

from .exceptions import (
    VedaError,
    VedaAuthError,
    VedaRequestError,
    VedaResponseError,
    VedaServerError
)
from .models import Individual


class VedaClient:
    """
    Client for interacting with the Veda Platform API.
    
    This class provides methods for all endpoints defined in the Veda Platform API.
    """
    
    def __init__(self, base_url: str = "http://example.com/api"):
        """
        Initialize a new client instance.
        
        Args:
            base_url: The base URL of the Veda API.
        """
        self.base_url = base_url
        self.ticket = None
        self.user_uri = None
    
    def _handle_response(self, response: requests.Response) -> dict:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: The requests Response object.
            
        Returns:
            The response content parsed as JSON.
            
        Raises:
            VedaAuthError: If authentication fails.
            VedaResponseError: If the API returns a client error.
            VedaServerError: If the API returns a server error.
        """
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                # If response is not JSON, return text content
                return {"content": response.text}
        
        # Map status codes to exceptions
        if response.status_code == 472:
            raise VedaAuthError("Authentication failed")
        elif response.status_code == 473:
            raise VedaResponseError("Request was invalid or operation failed")
        elif response.status_code == 400:
            raise VedaRequestError("Bad request")
        elif response.status_code >= 500:
            raise VedaServerError(f"Server error: {response.status_code}")
        else:
            raise VedaError(f"Unexpected status code: {response.status_code}")
    
    def authenticate(self, login: str, password: str, secret: Optional[str] = None) -> dict:
        """
        Authenticate a user with login and password.
        
        Args:
            login: The user's login name.
            password: The user's password (hashed format).
            secret: Optional secret key for additional security.
            
        Returns:
            Authentication response containing ticket and user info.
        """
        params = {
            "login": login,
            "password": password
        }
        
        if secret:
            params["secret"] = secret
        
        url = f"{self.base_url}/authenticate"
        response = requests.get(url, params=params)
        result = self._handle_response(response)
        
        # Store ticket for subsequent requests
        if "id" in result:
            self.ticket = result["id"]
            self.user_uri = result.get("user_uri")
        
        return result
    
    def is_ticket_valid(self, ticket: Optional[str] = None) -> bool:
        """
        Check if the provided ticket is valid.
        
        Args:
            ticket: The ticket to validate. If not provided, uses the client's stored ticket.
            
        Returns:
            True if the ticket is valid, False otherwise.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/is_ticket_valid"
        response = requests.get(url, params={"ticket": ticket})
        
        if response.status_code == 200:
            return response.json()
        
        return False
    
    def get_ticket_trusted(self, login: str, ticket: Optional[str] = None) -> dict:
        """
        Get a ticket trusted for use by another user.
        
        Args:
            login: The login of the user for whom the ticket is being requested.
            ticket: The requesting user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Ticket information for the specified user.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_ticket_trusted"
        params = {
            "ticket": ticket,
            "login": login
        }
        
        response = requests.get(url, params=params)
        return self._handle_response(response)
    
    def query(
        self,
        query: str,
        sort: Optional[str] = None,
        databases: Optional[str] = None,
        reopen: Optional[bool] = None,
        from_: Optional[int] = None,
        top: Optional[int] = None,
        limit: Optional[int] = None,
        trace: Optional[bool] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Execute a full text query against the stored data.
        
        Args:
            query: The full text query string.
            sort: Optional parameter to specify sorting.
            databases: Optional parameter to specify databases.
            reopen: Optional flag to reopen the query.
            from_: Optional parameter to specify the starting point.
            top: Optional parameter to specify the top limit.
            limit: Optional parameter to specify the limit on results.
            trace: Optional flag to enable tracing.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Query results.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/query"
        
        data = {
            "ticket": ticket,
            "query": query
        }
        
        if sort:
            data["sort"] = sort
        if databases:
            data["databases"] = databases
        if reopen is not None:
            data["reopen"] = reopen
        if from_ is not None:
            data["from"] = from_
        if top is not None:
            data["top"] = top
        if limit is not None:
            data["limit"] = limit
        if trace is not None:
            data["trace"] = trace
        
        response = requests.post(url, json=data)
        return self._handle_response(response)
    
    def get_individual(self, uri: str, reopen: Optional[bool] = None, ticket: Optional[str] = None) -> Individual:
        """
        Retrieve information about a specific individual.
        
        Args:
            uri: The unique identifier (URI) of the individual.
            reopen: Optional flag to reopen the query.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Individual object.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_individual"
        
        params = {
            "ticket": ticket,
            "uri": uri
        }
        
        if reopen is not None:
            params["reopen"] = reopen
        
        response = requests.get(url, params=params)
        data = self._handle_response(response)
        
        return Individual.from_dict(data)
    
    def get_individuals(self, uris: List[str], reopen: Optional[bool] = None, ticket: Optional[str] = None) -> List[Individual]:
        """
        Retrieve information about multiple individuals.
        
        Args:
            uris: List of unique identifiers (URIs) of the individuals.
            reopen: Optional flag to reopen the query.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            List of Individual objects.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_individuals"
        
        data = {
            "ticket": ticket,
            "uris": uris
        }
        
        if reopen is not None:
            data["reopen"] = reopen
        
        response = requests.post(url, json=data)
        result = self._handle_response(response)
        
        # Convert the list of dictionaries to a list of Individual objects
        return [Individual.from_dict(item) for item in result]
    
    def put_individual(
        self,
        individual: Union[Individual, Dict],
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Update or insert information about an individual.
        
        Args:
            individual: The individual object to be updated or inserted.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/put_individual"
        
        # Convert Individual object to dict if needed
        if isinstance(individual, Individual):
            individual_dict = individual.to_dict()
        else:
            individual_dict = individual
        
        data = {
            "ticket": ticket,
            "individual": individual_dict
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def put_individuals(
        self,
        individuals: Union[List[Individual], List[Dict]],
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Update or insert information about multiple individuals.
        
        Args:
            individuals: List of individual objects to be updated or inserted.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/put_individuals"
        
        # Convert Individual objects to dicts if needed
        individuals_dict = []
        for individual in individuals:
            if isinstance(individual, Individual):
                individuals_dict.append(individual.to_dict())
            else:
                individuals_dict.append(individual)
        
        data = {
            "ticket": ticket,
            "individuals": individuals_dict
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def remove_individual(
        self,
        uri: str,
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Remove information about a specific individual.
        
        Args:
            uri: The unique identifier (URI) of the individual to be removed.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the removal operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/remove_individual"
        
        data = {
            "ticket": ticket,
            "uri": uri
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def remove_from_individual(
        self,
        uri: str,
        individual: Union[Individual, Dict],
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Remove a specific field from the information of an individual.
        
        Args:
            uri: The unique identifier (URI) of the individual.
            individual: An object representing the individual with the field to be removed.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the removal operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/remove_from_individual"
        
        # Convert Individual object to dict if needed
        if isinstance(individual, Individual):
            individual_dict = individual.to_dict()
        else:
            individual_dict = individual
        
        data = {
            "ticket": ticket,
            "uri": uri,
            "individual": individual_dict
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def set_in_individual(
        self,
        uri: str,
        individual: Union[Individual, Dict],
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Set or update a specific field in the information of an individual.
        
        Args:
            uri: The unique identifier (URI) of the individual.
            individual: An object representing the individual with the field to be set or updated.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the set/update operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/set_in_individual"
        
        # Convert Individual object to dict if needed
        if isinstance(individual, Individual):
            individual_dict = individual.to_dict()
        else:
            individual_dict = individual
        
        data = {
            "ticket": ticket,
            "uri": uri,
            "individual": individual_dict
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def add_to_individual(
        self,
        uri: str,
        individual: Union[Individual, Dict],
        prepare_events: Optional[bool] = None,
        assigned_subsystems: Optional[int] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        ticket: Optional[str] = None
    ) -> dict:
        """
        Add a specific field to the information of an individual.
        
        Args:
            uri: The unique identifier (URI) of the individual.
            individual: An object representing the individual with the field to be added.
            prepare_events: Optional flag to prepare events.
            assigned_subsystems: Optional byte value for assigned subsystems.
            event_id: Optional event identifier.
            transaction_id: Optional transaction identifier.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Result of the addition operation.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/add_to_individual"
        
        # Convert Individual object to dict if needed
        if isinstance(individual, Individual):
            individual_dict = individual.to_dict()
        else:
            individual_dict = individual
        
        data = {
            "ticket": ticket,
            "uri": uri,
            "individual": individual_dict
        }
        
        if prepare_events is not None:
            data["prepare_events"] = prepare_events
        if assigned_subsystems is not None:
            data["assigned_subsystems"] = assigned_subsystems
        if event_id:
            data["event_id"] = event_id
        if transaction_id:
            data["transaction_id"] = transaction_id
        
        response = requests.put(url, json=data)
        return self._handle_response(response)
    
    def get_rights(self, uri: str, ticket: Optional[str] = None) -> dict:
        """
        Retrieve the access rights for a specific URI.
        
        Args:
            uri: The unique identifier (URI) for which the rights are being queried.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Access rights of the specified URI.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_rights"
        
        params = {
            "ticket": ticket,
            "uri": uri
        }
        
        response = requests.get(url, params=params)
        return self._handle_response(response)
    
    def get_rights_origin(self, uri: str, ticket: Optional[str] = None) -> List[dict]:
        """
        Retrieve information about the origin of access rights for a specific URI.
        
        Args:
            uri: The unique identifier (URI) for which the rights origins are being queried.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Origins of the access rights of the specified URI.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_rights_origin"
        
        params = {
            "ticket": ticket,
            "uri": uri
        }
        
        response = requests.get(url, params=params)
        return self._handle_response(response)
    
    def get_membership(self, uri: str, ticket: Optional[str] = None) -> dict:
        """
        Retrieve membership information of a specific URI.
        
        Args:
            uri: The unique identifier (URI) for which the membership details are being queried.
            ticket: The user's ticket. If not provided, uses the client's stored ticket.
            
        Returns:
            Membership details of the specified URI.
        """
        if ticket is None:
            ticket = self.ticket
            
        if not ticket:
            raise VedaAuthError("No ticket provided and no ticket stored in the client")
        
        url = f"{self.base_url}/get_membership"
        
        params = {
            "ticket": ticket,
            "uri": uri
        }
        
        response = requests.get(url, params=params)
        return self._handle_response(response)
    
    def get_operation_state(self, module_id: int, wait_op_id: int) -> int:
        """
        Retrieve the state of a specified operation.
        
        Args:
            module_id: The module ID associated with the operation.
            wait_op_id: The operation ID for which the state is being queried.
            
        Returns:
            State of the specified operation.
        """
        url = f"{self.base_url}/get_operation_state"
        
        params = {
            "module_id": module_id,
            "wait_op_id": wait_op_id
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            try:
                return int(response.text)
            except ValueError:
                raise VedaResponseError("Invalid response format for operation state")
        
        self._handle_response(response)  # This will raise an appropriate exception

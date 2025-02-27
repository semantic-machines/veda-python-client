# Veda Platform Python Client

A client library for interacting with the Veda Platform HTTP API.

## Installation

```bash
pip install veda-platform-client
```

## Requirements

- Python 3.6+
- requests

## Basic Usage

### Initialization

```python
from veda_client import VedaClient

# Initialize the client with your API URL
client = VedaClient(base_url="http://your-veda-instance.com/api")
```

### Authentication

```python
# Authenticate with username and password
auth_result = client.authenticate("username", "password")

# After successful authentication, the client stores the ticket
# for subsequent requests
print(f"Authenticated as: {client.user_uri}")

# Check if a ticket is valid
is_valid = client.is_ticket_valid()

# Logout (invalidate ticket)
client.logout()
```

### Basic Data Operations

```python
from veda_client.models import Individual, ValueItem

# Get a single individual
individual = client.get_individual("document:123")

# Get multiple individuals
individuals = client.get_individuals(["document:123", "document:456"])

# Create a new individual
new_individual = Individual(uri="document:123")

# Add values to the individual
new_individual.add_value("rdf:type", "v-s:Document", "uri")
new_individual.add_value("v-s:title", "Test Document", "string", "en")

# Save the individual
result = client.put_individual(new_individual)

# Update a field
update_individual = Individual(uri="document:123")
update_individual.add_value("v-s:description", "Updated description", "string", "en")

# Apply the update
result = client.set_in_individual("document:123", update_individual)

# Add a field
add_individual = Individual(uri="document:123")
add_individual.add_value("v-s:tag", "important", "string")

# Apply the addition
result = client.add_to_individual("document:123", add_individual)

# Remove a field
remove_individual = Individual(uri="document:123")
remove_individual.add_value("v-s:tag", "important", "string")

# Apply the removal
result = client.remove_from_individual("document:123", remove_individual)

# Delete an individual
result = client.remove_individual("document:123")
```

### Querying

```python
# Execute a basic query
result = client.query("'rdf:type' == 'v-s:Document'")

# Query with sorting and limit
result = client.query(
    query="'rdf:type' == 'v-s:Document'",
    sort="v-s:created",
    limit=10
)

# Execute a stored query with parameters
params = {
    "type": "v-s:Document",
    "limit": 10
}
result = client.stored_query("stored-query:DocumentSearch", params)
```

### File Operations

```python
# Upload a file
file_id = client.upload_file("path/to/document.pdf")

# Download a file
success = client.download_file(file_id, "path/to/download/document.pdf")
```

### Authorization

```python
# Get rights for a URI
rights = client.get_rights("document:123")

# Get rights origin
rights_origin = client.get_rights_origin("document:123")

# Get membership
membership = client.get_membership("document:123")
```

### Session Management

```python
# Get a ticket for another user (admin operation)
trusted_ticket = client.get_ticket_trusted("another_username")
```

## API Reference

### Authentication and Session Management

#### `authenticate(login, password, secret=None)`
Authenticate a user with login and password.

#### `is_ticket_valid(ticket=None)`
Check if the provided ticket is valid.

#### `get_ticket_trusted(login, ticket=None)`
Get a ticket trusted for use by another user.

#### `logout(ticket=None)`
Logout a user and invalidate their ticket.

### Individual Operations

#### `get_individual(uri, reopen=None, ticket=None)`
Retrieve information about a specific individual.

#### `get_individuals(uris, reopen=None, ticket=None)`
Retrieve information about multiple individuals.

#### `put_individual(individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Update or insert information about an individual.

#### `put_individuals(individuals, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Update or insert information about multiple individuals.

#### `remove_individual(uri, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Remove information about a specific individual.

#### `remove_from_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Remove a specific field from the information of an individual.

#### `set_in_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Set or update a specific field in the information of an individual.

#### `add_to_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)`
Add a specific field to the information of an individual.

### Query Operations

#### `query(query, sort=None, databases=None, reopen=None, from_=None, top=None, limit=None, trace=None, ticket=None)`
Execute a full text query against the stored data.

#### `stored_query(stored_query_id, params, ticket=None)`
Execute a stored query with parameters.

### Authorization Operations

#### `get_rights(uri, ticket=None)`
Retrieve the access rights for a specific URI.

#### `get_rights_origin(uri, ticket=None)`
Retrieve information about the origin of access rights for a specific URI.

#### `get_membership(uri, ticket=None)`
Retrieve membership information of a specific URI.

### File Operations

#### `upload_file(file_path, ticket=None)`
Upload a file to the server.

#### `download_file(file_id, output_path, ticket=None)`
Download a file from the server.

### Operation Monitoring

#### `get_operation_state(module_id, wait_op_id)`
Retrieve the state of a specified operation.

## Data Models

### Individual

The `Individual` class represents an entity in the Veda Platform data model.

```python
from veda_client.models import Individual, ValueItem

# Create a new individual
individual = Individual(uri="document:123")

# Add values to the individual
individual.add_value("rdf:type", "v-s:Document", "uri")
individual.add_value("v-s:title", "Test Document", "string", "en")
individual.add_value("v-s:created", "2023-01-01T12:00:00Z", "dateTime")

# Get values from the individual
title_values = individual.get_property("v-s:title")
first_title = individual.get_first_value("v-s:title")

# Convert to/from dictionary
individual_dict = individual.to_dict()
from_dict_individual = Individual.from_dict(individual_dict)
```

## Error Handling

The client defines several exception types for different error scenarios:

- `VedaError`: Base exception for all Veda client errors
- `VedaAuthError`: Authentication errors
- `VedaRequestError`: Invalid request errors
- `VedaResponseError`: Errors in API responses
- `VedaServerError`: Server errors

```python
from veda_client import VedaClient
from veda_client.exceptions import VedaAuthError, VedaServerError

client = VedaClient("http://your-veda-instance.com/api")

try:
    client.authenticate("username", "wrong_password")
except VedaAuthError as e:
    print(f"Authentication failed: {e}")

try:
    client.get_individual("non-existent-uri")
except VedaServerError as e:
    print(f"Server error: {e}")
```

## License

MIT License

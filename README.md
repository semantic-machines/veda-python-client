# Veda Platform Python Client

A Python client for interacting with the Veda Platform HTTP API.

## Installation

You can install the package directly from PyPI:

```bash
pip install veda-client
```

Or from source:

```bash
pip install git+https://github.com/yourusername/veda-python-client.git
```

## Requirements

- Python 3.6+
- requests library

## Quick Start

```python
from veda_client import VedaClient

# Initialize client
client = VedaClient(base_url="http://example.com/api")

# Authenticate
auth_response = client.authenticate(
    login="your_username",
    password="your_password_hash"
)

# Make a query
results = client.query("( 'rdf:type'=='v-s:UserThing' )")

# Get an individual
individual = client.get_individual("v-ui:DefaultLanguage")
print(individual.uri)  # Prints the URI
print(individual.get_first_value("rdfs:label"))  # Prints the first label

# Create and save a new individual
from veda_client.models import Individual
from veda_client.utils import create_value_item

new_individual = Individual(uri="v-s:MyNewIndividual")
new_individual.add_value("rdf:type", "v-s:Document", "Uri")
new_individual.add_value("rdfs:label", "My New Document", "String", "EN")
new_individual.add_value("rdfs:label", "Мой новый документ", "String", "RU")

client.put_individual(new_individual)
```

## API Documentation

### Authentication

```python
client.authenticate(login, password, secret=None)
```

Authenticates a user with login and password, and optionally a secret.

### Query

```python
client.query(query, sort=None, databases=None, reopen=None, from_=None, top=None, limit=None, trace=None, ticket=None)
```

Execute a full text query against the stored data.

### Individuals

#### Get

```python
client.get_individual(uri, reopen=None, ticket=None)
```

Retrieve information about a specific individual.

```python
client.get_individuals(uris, reopen=None, ticket=None)
```

Retrieve information about multiple individuals.

#### Put

```python
client.put_individual(individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Update or insert information about an individual.

```python
client.put_individuals(individuals, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Update or insert information about multiple individuals.

#### Remove

```python
client.remove_individual(uri, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Remove information about a specific individual.

```python
client.remove_from_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Remove a specific field from the information of an individual.

#### Modify

```python
client.set_in_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Set or update a specific field in the information of an individual.

```python
client.add_to_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, ticket=None)
```

Add a specific field to the information of an individual.

### Access Rights

```python
client.get_rights(uri, ticket=None)
```

Retrieve the access rights for a specific URI.

```python
client.get_rights_origin(uri, ticket=None)
```

Retrieve information about the origin of access rights for a specific URI.

```python
client.get_membership(uri, ticket=None)
```

Retrieve membership information of a specific URI.

### Other

```python
client.is_ticket_valid(ticket=None)
```

Check if the provided ticket is valid.

```python
client.get_ticket_trusted(login, ticket=None)
```

Get a ticket trusted for use by another user.

```python
client.get_operation_state(module_id, wait_op_id)
```

Retrieve the state of a specified operation.

## Models

### Individual

Represents an individual in the Veda data model.

```python
from veda_client.models import Individual

# Create a new individual
individual = Individual(uri="v-s:MyIndividual")

# Add a property value
individual.add_value("rdfs:label", "My Label", "String", "EN")

# Get a property
labels = individual.get_property("rdfs:label")

# Get the first value of a property
first_label = individual.get_first_value("rdfs:label")

# Set a property with multiple values
individual.set_property("rdfs:label", [
    {"data": "My Label", "type": "String", "lang": "EN"},
    {"data": "Моя метка", "type": "String", "lang": "RU"}
])

# Remove a property
individual.remove_property("rdfs:comment")
```

### ValueItem

Represents a value item in the Veda data model.

```python
from veda_client.models import ValueItem

# Create a new value item
value = ValueItem(data="My Value", type_="String", lang="EN")

# Convert to dictionary
value_dict = value.to_dict()
```

## Utility Functions

```python
from veda_client.utils import hash_password, build_query_string, create_individual, create_value_item, extract_values

# Hash a password
hash_password("my_password")

# Build a query string from conditions
build_query_string({"rdf:type": "v-s:Document", "v-s:created": "2023-01-01"})

# Create an individual from a dictionary
create_individual("v-s:MyIndividual", {
    "rdf:type": [{"data": "v-s:Document", "type": "Uri"}],
    "rdfs:label": [{"data": "My Document", "type": "String", "lang": "EN"}]
})

# Create a value item
create_value_item("My Value", "String", "EN")

# Extract all values for a property
extract_values(individual, "rdfs:label")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

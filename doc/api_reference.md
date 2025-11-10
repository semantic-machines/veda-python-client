# API Reference

Complete reference for all VedaClient methods.

## VedaClient Class

### Constructor

#### `VedaClient(base_url)`

Initialize a new client instance.

**Parameters:**
- `base_url` (str): The base URL of the Veda API

**Example:**
```python
client = VedaClient(base_url="http://example.com/api")
```

---

## Authentication Methods

### `authenticate(login, password, secret=None)`

Authenticate a user with login and password.

**Parameters:**
- `login` (str): User login name
- `password` (str): User password (hashed format)
- `secret` (str, optional): Additional security key

**Returns:**
- dict: Authentication response containing ticket and user info

**Example:**
```python
result = client.authenticate("admin", "hashed_password")
print(result["id"])  # ticket
print(result["user_uri"])  # user URI
```

### `is_ticket_valid(ticket=None)`

Check if a ticket is valid.

**Parameters:**
- `ticket` (str, optional): Ticket to validate. Uses stored ticket if not provided

**Returns:**
- bool: True if valid, False otherwise

**Example:**
```python
is_valid = client.is_ticket_valid()
```

### `get_ticket_trusted(login, ticket=None)`

Get a trusted ticket for another user (admin operation).

**Parameters:**
- `login` (str): Login of the user to get ticket for
- `ticket` (str, optional): Requesting user's ticket

**Returns:**
- dict: Ticket information

**Example:**
```python
trusted = client.get_ticket_trusted("other_user")
```

### `logout(ticket=None)`

Logout and invalidate a ticket.

**Parameters:**
- `ticket` (str, optional): Ticket to invalidate

**Returns:**
- bool: True if successful

**Example:**
```python
client.logout()
```

---

## Individual Operations

### `get_individual(uri, reopen=None, ticket=None)`

Retrieve a single individual.

**Parameters:**
- `uri` (str): Individual's unique identifier
- `reopen` (bool, optional): Reopen flag
- `ticket` (str, optional): User ticket

**Returns:**
- Individual: Individual object

**Example:**
```python
person = client.get_individual("person:123")
```

### `get_individuals(uris, reopen=None, ticket=None)`

Retrieve multiple individuals.

**Parameters:**
- `uris` (list of str): List of URIs
- `reopen` (bool, optional): Reopen flag
- `ticket` (str, optional): User ticket

**Returns:**
- list of Individual: List of Individual objects

**Example:**
```python
persons = client.get_individuals(["person:123", "person:456"])
```

### `put_individual(individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Create or update an individual.

**Parameters:**
- `individual` (Individual or dict): Individual to save
- `prepare_events` (bool, optional): Prepare events flag
- `assigned_subsystems` (int, optional): Assigned subsystems byte value
- `event_id` (str, optional): Event identifier
- `transaction_id` (str, optional): Transaction identifier
- `src` (str, optional): Source identifier
- `ticket` (str, optional): User ticket

**Returns:**
- dict: Operation result

**Example:**
```python
person = Individual(uri="person:123")
person.add_value("v-s:name", "John", "string")
result = client.put_individual(person, src="my-app")
```

### `put_individuals(individuals, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Create or update multiple individuals.

**Parameters:**
- `individuals` (list of Individual or dict): Individuals to save
- Other parameters same as `put_individual`

**Returns:**
- dict: Operation result

**Example:**
```python
persons = [person1, person2, person3]
result = client.put_individuals(persons)
```

### `remove_individual(uri, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Remove an individual.

**Parameters:**
- `uri` (str): Individual's URI to remove
- Other parameters same as `put_individual`

**Returns:**
- dict: Operation result

**Example:**
```python
result = client.remove_individual("person:123")
```

### `add_to_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Add properties to an individual.

**Parameters:**
- `uri` (str): Target individual's URI
- `individual` (Individual or dict): Properties to add
- Other parameters same as `put_individual`

**Returns:**
- dict: Operation result

**Example:**
```python
addition = Individual(uri="person:123")
addition.add_value("v-s:email", "new@example.com", "string")
result = client.add_to_individual("person:123", addition)
```

### `set_in_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Set (replace) properties in an individual.

**Parameters:**
- `uri` (str): Target individual's URI
- `individual` (Individual or dict): Properties to set
- Other parameters same as `put_individual`

**Returns:**
- dict: Operation result

**Example:**
```python
update = Individual(uri="person:123")
update.add_value("v-s:email", "updated@example.com", "string")
result = client.set_in_individual("person:123", update)
```

### `remove_from_individual(uri, individual, prepare_events=None, assigned_subsystems=None, event_id=None, transaction_id=None, src=None, ticket=None)`

Remove properties from an individual.

**Parameters:**
- `uri` (str): Target individual's URI
- `individual` (Individual or dict): Properties to remove
- Other parameters same as `put_individual`

**Returns:**
- dict: Operation result

**Example:**
```python
removal = Individual(uri="person:123")
removal.add_value("v-s:oldEmail", "old@example.com", "string")
result = client.remove_from_individual("person:123", removal)
```

---

## Query Operations

### `query(query, sort=None, databases=None, reopen=None, from_=None, top=None, limit=None, trace=None, ticket=None)`

Execute a full-text query.

**Parameters:**
- `query` (str): Query string
- `sort` (str, optional): Sort specification
- `databases` (str, optional): Database specification
- `reopen` (bool, optional): Reopen flag
- `from_` (int, optional): Starting position
- `top` (int, optional): Top limit
- `limit` (int, optional): Result limit
- `trace` (bool, optional): Enable tracing
- `ticket` (str, optional): User ticket

**Returns:**
- dict: Query results

**Example:**
```python
result = client.query(
    query="'rdf:type' == 'v-s:Person'",
    sort="v-s:created",
    limit=10
)
```

### `stored_query(stored_query_id, params, ticket=None)`

Execute a stored query.

**Parameters:**
- `stored_query_id` (str): Stored query ID
- `params` (dict): Query parameters
- `ticket` (str, optional): User ticket

**Returns:**
- dict: Query results

**Example:**
```python
result = client.stored_query(
    "query:FindPersons",
    {"type": "v-s:Person", "limit": 10}
)
```

---

## Authorization Operations

### `get_rights(uri, ticket=None)`

Get access rights for a URI.

**Parameters:**
- `uri` (str): URI to check rights for
- `ticket` (str, optional): User ticket

**Returns:**
- dict: Access rights information

**Example:**
```python
rights = client.get_rights("person:123")
```

### `get_rights_origin(uri, ticket=None)`

Get the origin of access rights for a URI.

**Parameters:**
- `uri` (str): URI to check
- `ticket` (str, optional): User ticket

**Returns:**
- list of dict: Rights origin information

**Example:**
```python
origins = client.get_rights_origin("person:123")
```

### `get_membership(uri, ticket=None)`

Get membership information for a URI.

**Parameters:**
- `uri` (str): URI to check
- `ticket` (str, optional): User ticket

**Returns:**
- dict: Membership information

**Example:**
```python
membership = client.get_membership("person:123")
```

---

## File Operations

### `upload_file(file_path, ticket=None)`

Upload a file to the server.

**Parameters:**
- `file_path` (str): Path to file to upload
- `ticket` (str, optional): User ticket

**Returns:**
- str: File ID on server

**Example:**
```python
file_id = client.upload_file("/path/to/document.pdf")
```

### `download_file(file_id, output_path, ticket=None)`

Download a file from the server.

**Parameters:**
- `file_id` (str): File ID to download
- `output_path` (str): Path to save file
- `ticket` (str, optional): User ticket

**Returns:**
- bool: True if successful

**Example:**
```python
success = client.download_file("file-123", "/path/to/save/document.pdf")
```

---

## Operation Monitoring

### `get_operation_state(module_id, wait_op_id)`

Get the state of an operation.

**Parameters:**
- `module_id` (int): Module ID
- `wait_op_id` (int): Operation ID

**Returns:**
- int: Operation state

**Example:**
```python
state = client.get_operation_state(1, 12345)
```


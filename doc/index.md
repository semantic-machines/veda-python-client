# Veda Python Client Documentation

Welcome to the Veda Python Client documentation. This library provides a Python interface for interacting with the Veda Platform HTTP API.

## Table of Contents

1. [Installation](installation.md)
2. [Getting Started](getting_started.md)
3. [API Reference](api_reference.md)
4. [Data Models](data_models.md)
5. [Examples](examples.md)
6. [Advanced Usage](advanced_usage.md)
7. [Error Handling](error_handling.md)

## Overview

The Veda Python Client is a library that allows you to interact with the Veda Platform API using Python. It provides:

- **Authentication and Session Management**: Authenticate users, validate tickets, and manage sessions
- **Individual Operations**: Create, read, update, and delete individuals (entities) in the Veda Platform
- **Query Operations**: Execute full-text queries and stored queries
- **File Operations**: Upload and download files
- **Authorization**: Check access rights and permissions

## Quick Example

```python
from veda_client import VedaClient
from veda_client.models import Individual

# Initialize the client
client = VedaClient(base_url="http://your-veda-instance.com/api")

# Authenticate
client.authenticate("username", "password")

# Create a new individual
person = Individual(uri="person:john-doe")
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "John", "string", "en")
person.add_value("v-s:lastName", "Doe", "string", "en")

# Save to the platform
client.put_individual(person)

# Retrieve the individual
retrieved = client.get_individual("person:john-doe")
print(retrieved.get_first_value("v-s:firstName"))  # Output: John
```

## Requirements

- Python 3.6 or higher
- requests library

## License

MIT License


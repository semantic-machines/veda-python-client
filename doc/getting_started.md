# Getting Started

This guide will help you start using the Veda Python Client.

## Basic Setup

### 1. Import the Library

```python
from veda_client import VedaClient
from veda_client.models import Individual
```

### 2. Initialize the Client

Create a client instance with your Veda Platform API URL:

```python
client = VedaClient(base_url="http://your-veda-instance.com/api")
```

### 3. Authenticate

Authenticate with your credentials:

```python
result = client.authenticate(login="username", password="hashed_password")
print(f"Authenticated as: {client.user_uri}")
```

The client stores the authentication ticket automatically. You don't need to pass it to subsequent requests.

## Basic Operations

### Creating an Individual

```python
# Create a new person
person = Individual(uri="person:john-doe")

# Add properties
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "John", "string", "en")
person.add_value("v-s:lastName", "Doe", "string", "en")
person.add_value("v-s:email", "john.doe@example.com", "string")

# Save to the platform
result = client.put_individual(person)
```

### Reading an Individual

```python
# Get a single individual
person = client.get_individual("person:john-doe")

# Access properties
first_name = person.get_first_value("v-s:firstName")
print(f"First name: {first_name}")

# Get all values for a property
emails = person.get_property("v-s:email")
for email_item in emails:
    print(f"Email: {email_item.data}")
```

### Updating an Individual

```python
# Method 1: Update the entire individual
person = client.get_individual("person:john-doe")
person.set_value("v-s:email", "new.email@example.com", "string")
client.put_individual(person)

# Method 2: Update specific fields
update = Individual(uri="person:john-doe")
update.add_value("v-s:phone", "+1234567890", "string")
client.set_in_individual("person:john-doe", update)
```

### Deleting an Individual

```python
# Remove an individual
result = client.remove_individual("person:john-doe")
```

### Querying Data

```python
# Execute a simple query
result = client.query("'rdf:type' == 'v-s:Person'")

# Query with limit
result = client.query(
    query="'rdf:type' == 'v-s:Person'",
    limit=10
)

# Access query results
if "result" in result:
    uris = result["result"]
    # Fetch the individuals
    persons = client.get_individuals(uris)
    for person in persons:
        print(person.get_first_value("v-s:firstName"))
```

## Working with Different Data Types

### String Values

```python
person.add_value("v-s:name", "John Doe", "string")
person.add_value("v-s:name", "Джон Доу", "string", "ru")  # with language
```

### URI References

```python
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:hasAccount", "account:123", "uri")
```

### Numeric Values

```python
person.add_value("v-s:age", 30, "integer")
person.add_value("v-s:salary", 50000.50, "decimal")
```

### Date and Time

```python
person.add_value("v-s:birthday", "1990-01-01", "date")
person.add_value("v-s:created", "2023-01-01T12:00:00Z", "dateTime")
```

### Boolean Values

```python
person.add_value("v-s:isActive", True, "boolean")
```

## Session Management

### Check Ticket Validity

```python
is_valid = client.is_ticket_valid()
print(f"Ticket valid: {is_valid}")
```

### Logout

```python
client.logout()
```

### Use a Different Ticket

```python
# Use a specific ticket instead of the stored one
individual = client.get_individual("person:123", ticket="custom-ticket")
```

## Next Steps

- Learn more about [API Reference](api_reference.md)
- Explore [Data Models](data_models.md) in detail
- Check out more [Examples](examples.md)
- Understand [Error Handling](error_handling.md)


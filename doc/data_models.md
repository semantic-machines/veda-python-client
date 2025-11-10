# Data Models

This document describes the data models used in the Veda Python Client.

## Individual

The `Individual` class represents an entity in the Veda Platform.

### Constructor

```python
Individual(uri, properties=None)
```

**Parameters:**
- `uri` (str): Unique identifier for the individual
- `properties` (dict, optional): Dictionary of properties

**Example:**
```python
person = Individual(uri="person:john-doe")
```

### Attributes

- `uri` (str): The individual's unique identifier
- `properties` (dict): Dictionary mapping property keys to lists of ValueItem objects

### Methods

#### `add_value(key, data, type_, lang=None)`

Add a value to a property.

**Parameters:**
- `key` (str): Property key
- `data` (any): Value data
- `type_` (str): Data type
- `lang` (str, optional): Language code

**Example:**
```python
person.add_value("v-s:firstName", "John", "string", "en")
person.add_value("v-s:age", 30, "integer")
```

#### `set_value(key, data, type_, lang=None)`

Set a single value for a property (removes existing values).

**Parameters:**
- Same as `add_value`

**Example:**
```python
person.set_value("v-s:email", "new@example.com", "string")
```

#### `get_property(key)`

Get all values for a property.

**Parameters:**
- `key` (str): Property key

**Returns:**
- list of ValueItem: List of values

**Example:**
```python
emails = person.get_property("v-s:email")
for email in emails:
    print(email.data)
```

#### `get_first_value(key)`

Get the data of the first value for a property.

**Parameters:**
- `key` (str): Property key

**Returns:**
- any: First value's data, or None if property doesn't exist

**Example:**
```python
name = person.get_first_value("v-s:firstName")
```

#### `set_property(key, values)`

Set a property with multiple values.

**Parameters:**
- `key` (str): Property key
- `values` (list): List of ValueItem objects or dicts

**Example:**
```python
person.set_property("v-s:email", [
    {"data": "email1@example.com", "type": "string"},
    {"data": "email2@example.com", "type": "string"}
])
```

#### `replace_value(key, old_data, new_data, type_, lang=None)`

Replace an existing value with a new one.

**Parameters:**
- `key` (str): Property key
- `old_data` (any): Old value to replace
- `new_data` (any): New value
- `type_` (str): Data type
- `lang` (str, optional): Language code

**Returns:**
- bool: True if replaced, False if old value not found

**Example:**
```python
person.replace_value("v-s:email", "old@example.com", "new@example.com", "string")
```

#### `remove_value(key, data)`

Remove a specific value from a property.

**Parameters:**
- `key` (str): Property key
- `data` (any): Value to remove

**Returns:**
- bool: True if removed, False if not found

**Example:**
```python
person.remove_value("v-s:email", "unwanted@example.com")
```

#### `remove_property(key)`

Remove an entire property.

**Parameters:**
- `key` (str): Property key

**Example:**
```python
person.remove_property("v-s:oldField")
```

#### `remove_predicate(predicate)`

Remove a predicate from the individual.

**Parameters:**
- `predicate` (str): Property key (predicate) to remove

**Returns:**
- bool: True if removed, False if property didn't exist

**Example:**
```python
success = person.remove_predicate("v-s:oldField")
if success:
    print("Predicate removed")
```

#### `to_dict()`

Convert the Individual to a dictionary.

**Returns:**
- dict: Dictionary representation

**Example:**
```python
data = person.to_dict()
# {'@': 'person:john-doe', 'v-s:firstName': [{'data': 'John', 'type': 'string', 'lang': 'en'}]}
```

#### `from_dict(data)` (class method)

Create an Individual from a dictionary.

**Parameters:**
- `data` (dict): Dictionary representation

**Returns:**
- Individual: New Individual instance

**Example:**
```python
data = {'@': 'person:john-doe', 'v-s:firstName': [{'data': 'John', 'type': 'string'}]}
person = Individual.from_dict(data)
```

---

## ValueItem

The `ValueItem` class represents a single value in the Veda data model.

### Constructor

```python
ValueItem(data, type_, lang=None)
```

**Parameters:**
- `data` (any): The value data
- `type_` (str): Data type
- `lang` (str, optional): Language code

**Example:**
```python
value = ValueItem(data="John", type_="string", lang="en")
```

### Attributes

- `data` (any): The value data
- `type` (str): The data type
- `lang` (str, optional): Language code

### Methods

#### `to_dict()`

Convert the ValueItem to a dictionary.

**Returns:**
- dict: Dictionary representation

**Example:**
```python
data = value.to_dict()
# {'data': 'John', 'type': 'string', 'lang': 'en'}
```

#### `from_dict(data)` (class method)

Create a ValueItem from a dictionary.

**Parameters:**
- `data` (dict): Dictionary representation

**Returns:**
- ValueItem: New ValueItem instance

**Example:**
```python
data = {'data': 'John', 'type': 'string', 'lang': 'en'}
value = ValueItem.from_dict(data)
```

---

## Data Types

The Veda Platform supports various data types:

### String

Text values.

```python
person.add_value("v-s:name", "John Doe", "string")
person.add_value("v-s:name", "Джон Доу", "string", "ru")  # with language
```

### URI

References to other individuals.

```python
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:hasAccount", "account:123", "uri")
```

### Integer

Whole numbers.

```python
person.add_value("v-s:age", 30, "integer")
person.add_value("v-s:count", 5, "integer")
```

### Decimal

Decimal numbers.

```python
person.add_value("v-s:salary", 50000.50, "decimal")
person.add_value("v-s:rate", 0.75, "decimal")
```

### Boolean

True/False values.

```python
person.add_value("v-s:isActive", True, "boolean")
person.add_value("v-s:isDeleted", False, "boolean")
```

### Date

Date values (format: YYYY-MM-DD).

```python
person.add_value("v-s:birthday", "1990-01-01", "date")
```

### DateTime

Date and time values (ISO 8601 format).

```python
person.add_value("v-s:created", "2023-01-01T12:00:00Z", "dateTime")
person.add_value("v-s:modified", "2023-06-15T14:30:00+03:00", "dateTime")
```

---

## Working with Properties

### Single-Value Properties

Use `set_value` to ensure a property has only one value:

```python
person.set_value("v-s:firstName", "John", "string")
# This replaces any existing values
```

### Multi-Value Properties

Use `add_value` to add multiple values:

```python
person.add_value("v-s:email", "john@example.com", "string")
person.add_value("v-s:email", "j.doe@example.com", "string")
# Person now has two email addresses
```

### Language-Specific Values

Store the same property in multiple languages:

```python
person.add_value("v-s:description", "Software Engineer", "string", "en")
person.add_value("v-s:description", "Инженер-программист", "string", "ru")
person.add_value("v-s:description", "Ingénieur logiciel", "string", "fr")
```

---

## Examples

### Complete Person Individual

```python
from veda_client.models import Individual

person = Individual(uri="person:john-doe")

# Basic info
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "John", "string", "en")
person.add_value("v-s:lastName", "Doe", "string", "en")
person.add_value("v-s:middleName", "Michael", "string", "en")

# Contact info
person.add_value("v-s:email", "john.doe@example.com", "string")
person.add_value("v-s:phone", "+1234567890", "string")

# Additional info
person.add_value("v-s:birthday", "1990-01-15", "date")
person.add_value("v-s:age", 33, "integer")
person.add_value("v-s:isActive", True, "boolean")

# References
person.add_value("v-s:hasAccount", "account:john-doe", "uri")
person.add_value("v-s:memberOf", "org:company-123", "uri")

# Timestamps
person.add_value("v-s:created", "2023-01-01T10:00:00Z", "dateTime")
person.add_value("v-s:modified", "2023-06-15T15:30:00Z", "dateTime")

# Convert to dict for inspection
print(person.to_dict())
```

### Working with Existing Individual

```python
from veda_client import VedaClient

client = VedaClient(base_url="http://example.com/api")
client.authenticate("user", "password")

# Retrieve individual
person = client.get_individual("person:john-doe")

# Read values
first_name = person.get_first_value("v-s:firstName")
all_emails = person.get_property("v-s:email")

# Modify values
person.set_value("v-s:age", 34, "integer")
person.add_value("v-s:email", "new.email@example.com", "string")
person.remove_value("v-s:email", "old.email@example.com")

# Save changes
client.put_individual(person)
```


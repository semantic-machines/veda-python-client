# Examples

This document provides practical examples of using the Veda Python Client.

## Authentication

### Basic Authentication

```python
from veda_client import VedaClient

client = VedaClient(base_url="http://example.com/api")

# Authenticate
result = client.authenticate(login="admin", password="hashed_password")
print(f"Ticket: {result['id']}")
print(f"User: {result['user_uri']}")
```

### Authentication with Password Hashing

```python
from veda_client import VedaClient
from veda_client.utils import hash_password

client = VedaClient(base_url="http://example.com/api")

# Hash password before authentication
plain_password = "my_password"
hashed = hash_password(plain_password)

client.authenticate(login="admin", password=hashed)
```

### Check Session Validity

```python
# After authentication
if client.is_ticket_valid():
    print("Session is active")
else:
    print("Session expired, need to re-authenticate")
    client.authenticate(login="admin", password="hashed_password")
```

---

## Creating Individuals

### Create a Person

```python
from veda_client import VedaClient
from veda_client.models import Individual

client = VedaClient(base_url="http://example.com/api")
client.authenticate("admin", "password")

# Create person
person = Individual(uri="person:alice-smith")
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "Alice", "string", "en")
person.add_value("v-s:lastName", "Smith", "string", "en")
person.add_value("v-s:email", "alice@example.com", "string")
person.add_value("v-s:birthday", "1985-05-20", "date")

# Save
result = client.put_individual(person)
print(f"Created: {person.uri}")
```

### Create a Document

```python
document = Individual(uri="doc:report-2023")
document.add_value("rdf:type", "v-s:Document", "uri")
document.add_value("v-s:title", "Annual Report 2023", "string", "en")
document.add_value("v-s:title", "Годовой отчет 2023", "string", "ru")
document.add_value("v-s:created", "2023-01-15T10:00:00Z", "dateTime")
document.add_value("v-s:author", "person:alice-smith", "uri")

client.put_individual(document)
```

### Create an Organization

```python
org = Individual(uri="org:tech-corp")
org.add_value("rdf:type", "v-s:Organization", "uri")
org.add_value("v-s:label", "Tech Corporation", "string", "en")
org.add_value("v-s:email", "info@techcorp.com", "string")
org.add_value("v-s:phone", "+1-800-TECH", "string")

client.put_individual(org)
```

---

## Reading Individuals

### Get Single Individual

```python
person = client.get_individual("person:alice-smith")

# Access properties
first_name = person.get_first_value("v-s:firstName")
last_name = person.get_first_value("v-s:lastName")
print(f"Name: {first_name} {last_name}")

# Get all emails
emails = person.get_property("v-s:email")
for email in emails:
    print(f"Email: {email.data}")
```

### Get Multiple Individuals

```python
uris = ["person:alice-smith", "person:bob-jones", "person:carol-white"]
persons = client.get_individuals(uris)

for person in persons:
    name = person.get_first_value("v-s:firstName")
    print(f"Person: {name} ({person.uri})")
```

### Get Individual with Error Handling

```python
from veda_client.exceptions import VedaError

try:
    person = client.get_individual("person:unknown")
except VedaError as e:
    print(f"Error retrieving individual: {e}")
```

---

## Updating Individuals

### Update Entire Individual

```python
# Get individual
person = client.get_individual("person:alice-smith")

# Modify properties
person.set_value("v-s:email", "alice.new@example.com", "string")
person.add_value("v-s:phone", "+1234567890", "string")

# Save changes
client.put_individual(person)
```

### Update Specific Fields

```python
# Create update object with only changed fields
update = Individual(uri="person:alice-smith")
update.add_value("v-s:jobTitle", "Senior Engineer", "string", "en")
update.add_value("v-s:department", "org:engineering", "uri")

# Apply update
client.set_in_individual("person:alice-smith", update)
```

### Add Values to Existing Properties

```python
# Add another email without removing existing ones
addition = Individual(uri="person:alice-smith")
addition.add_value("v-s:email", "alice.work@example.com", "string")

client.add_to_individual("person:alice-smith", addition)
```

### Remove Specific Values

```python
# Remove a specific email
removal = Individual(uri="person:alice-smith")
removal.add_value("v-s:email", "old@example.com", "string")

client.remove_from_individual("person:alice-smith", removal)
```

### Replace Values

```python
person = client.get_individual("person:alice-smith")

# Replace specific value
person.replace_value("v-s:phone", "+1111111111", "+2222222222", "string")

# Save
client.put_individual(person)
```

---

## Querying Data

### Simple Query

```python
# Find all persons
result = client.query("'rdf:type' == 'v-s:Person'")
print(f"Found {result.get('count', 0)} persons")

if "result" in result:
    for uri in result["result"]:
        print(f"- {uri}")
```

### Query with Limit and Sort

```python
result = client.query(
    query="'rdf:type' == 'v-s:Document'",
    sort="v-s:created",
    limit=10
)

# Get the documents
if "result" in result:
    documents = client.get_individuals(result["result"])
    for doc in documents:
        title = doc.get_first_value("v-s:title")
        print(f"Document: {title}")
```

### Complex Query

```python
# Find persons in a specific organization
query = "'rdf:type' == 'v-s:Person' && 'v-s:memberOf' == 'org:tech-corp'"
result = client.query(query, limit=20)
```

### Query with Parameters

```python
# Using query builder utility
from veda_client.utils import build_query_string

conditions = {
    "rdf:type": "v-s:Person",
    "v-s:department": "org:engineering"
}

query_string = build_query_string(conditions)
result = client.query(query_string)
```

### Stored Query

```python
params = {
    "type": "v-s:Person",
    "status": "active",
    "limit": 50
}

result = client.stored_query("query:FindActivePersons", params)
```

---

## Deleting Data

### Delete Individual

```python
result = client.remove_individual("person:old-account")
print("Individual removed")
```

### Delete with Source Tracking

```python
result = client.remove_individual(
    "person:old-account",
    src="cleanup-script"
)
```

### Delete Multiple Individuals

```python
uris_to_delete = ["person:temp1", "person:temp2", "person:temp3"]

for uri in uris_to_delete:
    try:
        client.remove_individual(uri)
        print(f"Deleted: {uri}")
    except Exception as e:
        print(f"Error deleting {uri}: {e}")
```

---

## File Operations

### Upload File

```python
# Upload a document
file_id = client.upload_file("/path/to/report.pdf")
print(f"File uploaded with ID: {file_id}")

# Create individual for the file
doc = Individual(uri=f"file:{file_id}")
doc.add_value("rdf:type", "v-s:File", "uri")
doc.add_value("v-s:fileName", "report.pdf", "string")
doc.add_value("v-s:fileUri", file_id, "string")

client.put_individual(doc)
```

### Download File

```python
file_id = "abc123-def456-ghi789"
output_path = "/path/to/save/document.pdf"

success = client.download_file(file_id, output_path)
if success:
    print(f"File downloaded to {output_path}")
else:
    print("Download failed")
```

---

## Authorization

### Check User Rights

```python
rights = client.get_rights("doc:confidential-report")
print(f"Rights: {rights}")
```

### Check Rights Origin

```python
origins = client.get_rights_origin("doc:confidential-report")
for origin in origins:
    print(f"Permission from: {origin}")
```

### Get Membership

```python
membership = client.get_membership("person:alice-smith")
print(f"Member of: {membership}")
```

---

## Batch Operations

### Create Multiple Individuals

```python
persons = []

for i in range(10):
    person = Individual(uri=f"person:user{i}")
    person.add_value("rdf:type", "v-s:Person", "uri")
    person.add_value("v-s:firstName", f"User{i}", "string")
    persons.append(person)

# Save all at once
result = client.put_individuals(persons)
print(f"Created {len(persons)} persons")
```

### Update Multiple Individuals

```python
# Get individuals
uris = ["person:user1", "person:user2", "person:user3"]
persons = client.get_individuals(uris)

# Modify all
for person in persons:
    person.add_value("v-s:department", "org:engineering", "uri")

# Save all
client.put_individuals(persons)
```

---

## Working with Transactions

### Use Transaction ID

```python
import uuid

transaction_id = str(uuid.uuid4())

# Create multiple individuals in the same transaction
person = Individual(uri="person:new-user")
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "New", "string")

account = Individual(uri="account:new-account")
account.add_value("rdf:type", "v-s:Account", "uri")
account.add_value("v-s:owner", "person:new-user", "uri")

# Save both with same transaction ID
client.put_individual(person, transaction_id=transaction_id)
client.put_individual(account, transaction_id=transaction_id)
```

---

## Source Tracking

### Track Modification Source

```python
# Different sources for different operations
client.put_individual(person, src="web-ui")
client.set_in_individual(person.uri, update, src="api-import")
client.remove_individual(person.uri, src="admin-panel")
```

---

## Error Handling

### Complete Error Handling Example

```python
from veda_client import VedaClient
from veda_client.exceptions import (
    VedaAuthError,
    VedaRequestError,
    VedaResponseError,
    VedaServerError,
    VedaError
)

client = VedaClient(base_url="http://example.com/api")

try:
    # Authenticate
    client.authenticate("admin", "password")
    
    # Get individual
    person = client.get_individual("person:alice")
    
    # Update
    person.set_value("v-s:email", "new@example.com", "string")
    client.put_individual(person)
    
    print("Success!")
    
except VedaAuthError as e:
    print(f"Authentication error: {e}")
except VedaRequestError as e:
    print(f"Invalid request: {e}")
except VedaResponseError as e:
    print(f"Operation failed: {e}")
except VedaServerError as e:
    print(f"Server error: {e}")
except VedaError as e:
    print(f"Veda error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Utility Functions

### Create Individual with Utility

```python
from veda_client.utils import create_individual

properties = {
    "rdf:type": [{"data": "v-s:Person", "type": "uri"}],
    "v-s:firstName": [{"data": "John", "type": "string", "lang": "en"}],
    "v-s:lastName": [{"data": "Doe", "type": "string", "lang": "en"}]
}

person = create_individual("person:john-doe", properties)
client.put_individual(person)
```

### Extract Values with Utility

```python
from veda_client.utils import extract_values

person = client.get_individual("person:alice-smith")

# Extract all email addresses
emails = extract_values(person, "v-s:email")
print(f"Emails: {emails}")
```

### Build Query String

```python
from veda_client.utils import build_query_string

conditions = {
    "rdf:type": "v-s:Person",
    "v-s:isActive": True,
    "v-s:department": "org:engineering"
}

query = build_query_string(conditions)
# Result: "('rdf:type'=='v-s:Person') && ('v-s:isActive'==True) && ('v-s:department'=='org:engineering')"

result = client.query(query)
```


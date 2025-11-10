# Advanced Usage

This document covers advanced features and patterns for using the Veda Python Client.

## Custom Client Configuration

### Custom Base URL and Endpoints

```python
from veda_client import VedaClient

# Initialize with custom URL
client = VedaClient(base_url="https://veda.example.com/custom/api")

# The client automatically appends endpoint paths
# e.g., https://veda.example.com/custom/api/authenticate
```

### Session Management Across Multiple Clients

```python
# Client 1 - authenticate
client1 = VedaClient(base_url="http://example.com/api")
result = client1.authenticate("admin", "password")
ticket = result["id"]

# Client 2 - reuse ticket
client2 = VedaClient(base_url="http://example.com/api")
client2.ticket = ticket
client2.user_uri = result["user_uri"]

# Now client2 can make authenticated requests
person = client2.get_individual("person:123")
```

---

## Batch Processing

### Process Large Collections

```python
def process_individuals_in_batches(client, uris, batch_size=100):
    """Process individuals in batches to avoid memory issues."""
    for i in range(0, len(uris), batch_size):
        batch = uris[i:i + batch_size]
        individuals = client.get_individuals(batch)
        
        # Process batch
        for individual in individuals:
            # Do something with each individual
            process_individual(individual)
        
        print(f"Processed {min(i + batch_size, len(uris))} of {len(uris)}")

# Usage
all_uris = ["person:1", "person:2", ..., "person:10000"]
process_individuals_in_batches(client, all_uris)
```

### Bulk Create with Error Handling

```python
from veda_client.models import Individual
from veda_client.exceptions import VedaError

def bulk_create_persons(client, persons_data):
    """
    Create multiple persons with error tracking.
    
    Args:
        persons_data: List of dicts with person information
        
    Returns:
        Tuple of (successful, failed)
    """
    successful = []
    failed = []
    
    for data in persons_data:
        try:
            person = Individual(uri=data["uri"])
            person.add_value("rdf:type", "v-s:Person", "uri")
            person.add_value("v-s:firstName", data["first_name"], "string")
            person.add_value("v-s:lastName", data["last_name"], "string")
            
            client.put_individual(person)
            successful.append(data["uri"])
        except VedaError as e:
            failed.append({"uri": data["uri"], "error": str(e)})
    
    return successful, failed

# Usage
persons = [
    {"uri": "person:1", "first_name": "John", "last_name": "Doe"},
    {"uri": "person:2", "first_name": "Jane", "last_name": "Smith"},
    # ... more persons
]

successful, failed = bulk_create_persons(client, persons)
print(f"Created: {len(successful)}, Failed: {len(failed)}")
```

---

## Advanced Querying

### Query with Pagination

```python
def get_all_results(client, query, page_size=100):
    """Get all results for a query using pagination."""
    all_results = []
    offset = 0
    
    while True:
        result = client.query(
            query=query,
            from_=offset,
            limit=page_size
        )
        
        if "result" not in result or len(result["result"]) == 0:
            break
        
        all_results.extend(result["result"])
        offset += page_size
        
        # Check if we got fewer results than requested (last page)
        if len(result["result"]) < page_size:
            break
    
    return all_results

# Usage
all_persons = get_all_results(
    client,
    "'rdf:type' == 'v-s:Person'",
    page_size=50
)
print(f"Total persons: {len(all_persons)}")
```

### Complex Query Building

```python
class QueryBuilder:
    """Helper class for building complex queries."""
    
    def __init__(self):
        self.conditions = []
    
    def add_type(self, type_uri):
        """Add type condition."""
        self.conditions.append(f"'rdf:type' == '{type_uri}'")
        return self
    
    def add_equals(self, field, value):
        """Add equality condition."""
        if isinstance(value, str):
            self.conditions.append(f"'{field}' == '{value}'")
        else:
            self.conditions.append(f"'{field}' == {value}")
        return self
    
    def add_contains(self, field, value):
        """Add contains condition."""
        self.conditions.append(f"'{field}' == '*{value}*'")
        return self
    
    def build(self):
        """Build final query string."""
        return " && ".join(self.conditions)

# Usage
query = (QueryBuilder()
    .add_type("v-s:Person")
    .add_equals("v-s:department", "org:engineering")
    .add_contains("v-s:firstName", "John")
    .build())

result = client.query(query)
```

---

## Transaction Management

### Coordinated Updates

```python
import uuid
from veda_client.models import Individual

def transfer_ownership(client, document_uri, from_person, to_person):
    """Transfer document ownership using a transaction."""
    transaction_id = str(uuid.uuid4())
    
    try:
        # Update document owner
        doc_update = Individual(uri=document_uri)
        doc_update.add_value("v-s:owner", to_person, "uri")
        client.set_in_individual(
            document_uri,
            doc_update,
            transaction_id=transaction_id,
            src="ownership-transfer"
        )
        
        # Add to new owner's documents
        person_update = Individual(uri=to_person)
        person_update.add_value("v-s:hasDocument", document_uri, "uri")
        client.add_to_individual(
            to_person,
            person_update,
            transaction_id=transaction_id,
            src="ownership-transfer"
        )
        
        # Remove from old owner's documents
        old_person_update = Individual(uri=from_person)
        old_person_update.add_value("v-s:hasDocument", document_uri, "uri")
        client.remove_from_individual(
            from_person,
            old_person_update,
            transaction_id=transaction_id,
            src="ownership-transfer"
        )
        
        return True
    except Exception as e:
        print(f"Transfer failed: {e}")
        return False

# Usage
success = transfer_ownership(
    client,
    "doc:report-2023",
    "person:alice",
    "person:bob"
)
```

---

## Custom Data Types and Helpers

### Create Helper Methods

```python
from veda_client.models import Individual
from datetime import datetime

class PersonIndividual(Individual):
    """Extended Individual class for persons."""
    
    def __init__(self, uri):
        super().__init__(uri)
        self.add_value("rdf:type", "v-s:Person", "uri")
    
    def set_name(self, first_name, last_name, lang="en"):
        """Set person's name."""
        self.set_value("v-s:firstName", first_name, "string", lang)
        self.set_value("v-s:lastName", last_name, "string", lang)
    
    def set_email(self, email):
        """Set person's email."""
        self.set_value("v-s:email", email, "string")
    
    def add_organization(self, org_uri):
        """Add organization membership."""
        self.add_value("v-s:memberOf", org_uri, "uri")
    
    def get_full_name(self):
        """Get full name."""
        first = self.get_first_value("v-s:firstName")
        last = self.get_first_value("v-s:lastName")
        return f"{first} {last}" if first and last else None

# Usage
person = PersonIndividual("person:john-doe")
person.set_name("John", "Doe", "en")
person.set_email("john@example.com")
person.add_organization("org:tech-corp")

client.put_individual(person)
```

### Date/Time Helpers

```python
from datetime import datetime

def set_timestamp(individual, field, dt=None):
    """Set a timestamp field to current or specified datetime."""
    if dt is None:
        dt = datetime.utcnow()
    
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    individual.set_value(field, timestamp, "dateTime")

# Usage
person = Individual("person:john")
set_timestamp(person, "v-s:created")
set_timestamp(person, "v-s:modified")
```

---

## Working with Files

### Upload Multiple Files

```python
import os

def upload_directory(client, directory_path, file_type_filter=None):
    """
    Upload all files from a directory.
    
    Args:
        directory_path: Path to directory
        file_type_filter: Optional list of extensions (e.g., ['.pdf', '.docx'])
        
    Returns:
        Dict mapping filenames to file IDs
    """
    uploaded = {}
    
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        if file_type_filter:
            ext = os.path.splitext(filename)[1]
            if ext not in file_type_filter:
                continue
        
        try:
            file_id = client.upload_file(filepath)
            uploaded[filename] = file_id
            print(f"Uploaded {filename} -> {file_id}")
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")
    
    return uploaded

# Usage
file_ids = upload_directory(
    client,
    "/path/to/documents",
    file_type_filter=['.pdf', '.doc', '.docx']
)
```

### Download with Progress

```python
import requests
from pathlib import Path

def download_file_with_progress(client, file_id, output_path):
    """Download file with progress indication."""
    url = f"{client.base_url}/files/{file_id}"
    params = {"ticket": client.ticket}
    
    response = requests.get(url, params=params, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    downloaded = 0
    chunk_size = 8192
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            downloaded += len(chunk)
            
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}%", end='')
    
    print("\nDownload complete")

# Usage
download_file_with_progress(client, "file-123", "/path/to/output.pdf")
```

---

## Caching and Performance

### Simple Cache Implementation

```python
from functools import lru_cache
from veda_client.models import Individual

class CachedVedaClient:
    """Veda client with caching."""
    
    def __init__(self, client):
        self.client = client
        self._cache = {}
    
    def get_individual_cached(self, uri, ttl=300):
        """Get individual with caching."""
        import time
        
        if uri in self._cache:
            cached_time, individual = self._cache[uri]
            if time.time() - cached_time < ttl:
                return individual
        
        # Not in cache or expired
        individual = self.client.get_individual(uri)
        self._cache[uri] = (time.time(), individual)
        return individual
    
    def invalidate_cache(self, uri=None):
        """Invalidate cache for specific URI or all."""
        if uri:
            self._cache.pop(uri, None)
        else:
            self._cache.clear()

# Usage
cached_client = CachedVedaClient(client)

# First call - fetches from server
person = cached_client.get_individual_cached("person:123")

# Second call - uses cache
person = cached_client.get_individual_cached("person:123")

# After update, invalidate cache
client.put_individual(person)
cached_client.invalidate_cache("person:123")
```

---

## Multi-threading

### Parallel Operations

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from veda_client import VedaClient

def process_uri(client_config, uri):
    """Process a single URI (in separate thread)."""
    # Create client instance for this thread
    client = VedaClient(base_url=client_config["base_url"])
    client.ticket = client_config["ticket"]
    
    try:
        individual = client.get_individual(uri)
        # Process individual
        return {"uri": uri, "success": True, "data": individual}
    except Exception as e:
        return {"uri": uri, "success": False, "error": str(e)}

def process_uris_parallel(client, uris, max_workers=5):
    """Process multiple URIs in parallel."""
    client_config = {
        "base_url": client.base_url,
        "ticket": client.ticket
    }
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_uri, client_config, uri): uri
            for uri in uris
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"Processed {result['uri']}: {result['success']}")
    
    return results

# Usage
uris = [f"person:{i}" for i in range(100)]
results = process_uris_parallel(client, uris, max_workers=10)

successful = [r for r in results if r["success"]]
print(f"Successfully processed: {len(successful)}/{len(uris)}")
```

---

## Custom Validators

### Validate Before Save

```python
class ValidationError(Exception):
    """Validation error."""
    pass

class PersonValidator:
    """Validator for person individuals."""
    
    @staticmethod
    def validate(individual):
        """Validate a person individual."""
        errors = []
        
        # Check type
        types = individual.get_property("rdf:type")
        if not any(t.data == "v-s:Person" for t in types):
            errors.append("Must have type v-s:Person")
        
        # Check required fields
        if not individual.get_first_value("v-s:firstName"):
            errors.append("First name is required")
        
        if not individual.get_first_value("v-s:lastName"):
            errors.append("Last name is required")
        
        # Check email format
        email = individual.get_first_value("v-s:email")
        if email and "@" not in email:
            errors.append("Invalid email format")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return True

# Usage
person = Individual("person:john")
person.add_value("rdf:type", "v-s:Person", "uri")
person.add_value("v-s:firstName", "John", "string")
person.add_value("v-s:lastName", "Doe", "string")

try:
    PersonValidator.validate(person)
    client.put_individual(person)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Monitoring and Logging

### Detailed Operation Logging

```python
import logging
import time
from functools import wraps

def log_operation(func):
    """Decorator to log operation execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"{func.__name__} completed in {duration:.2f}s"
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {duration:.2f}s: {e}"
            )
            raise
    
    return wrapper

# Usage
@log_operation
def create_person(client, uri, first_name, last_name):
    person = Individual(uri)
    person.add_value("rdf:type", "v-s:Person", "uri")
    person.add_value("v-s:firstName", first_name, "string")
    person.add_value("v-s:lastName", last_name, "string")
    return client.put_individual(person)

# This will log execution time
create_person(client, "person:john", "John", "Doe")
```


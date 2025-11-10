# Error Handling

This document explains how to handle errors when using the Veda Python Client.

## Exception Hierarchy

The library defines a hierarchy of exceptions:

```
VedaError (base exception)
├── VedaAuthError (authentication errors)
├── VedaRequestError (invalid request errors)
├── VedaResponseError (API response errors)
└── VedaServerError (server-side errors)
```

## Exception Classes

### VedaError

Base exception for all Veda client errors.

**When raised:**
- Unexpected status codes
- General errors not covered by specific exceptions

**Example:**
```python
from veda_client.exceptions import VedaError

try:
    client.get_individual("person:123")
except VedaError as e:
    print(f"Veda error: {e}")
```

### VedaAuthError

Exception for authentication-related errors.

**When raised:**
- Invalid credentials (status code 472)
- Missing or invalid ticket
- Session expired

**Example:**
```python
from veda_client.exceptions import VedaAuthError

try:
    client.authenticate("user", "wrong_password")
except VedaAuthError as e:
    print(f"Authentication failed: {e}")
```

### VedaRequestError

Exception for invalid request errors.

**When raised:**
- Malformed request (status code 400)
- Invalid parameters

**Example:**
```python
from veda_client.exceptions import VedaRequestError

try:
    client.query("")  # Empty query
except VedaRequestError as e:
    print(f"Invalid request: {e}")
```

### VedaResponseError

Exception for errors in API responses.

**When raised:**
- Operation failed (status code 473)
- Request was invalid

**Example:**
```python
from veda_client.exceptions import VedaResponseError

try:
    client.put_individual(invalid_individual)
except VedaResponseError as e:
    print(f"Operation failed: {e}")
```

### VedaServerError

Exception for server-side errors.

**When raised:**
- Server errors (status code 500+)
- Internal server problems

**Example:**
```python
from veda_client.exceptions import VedaServerError

try:
    client.get_individual("person:123")
except VedaServerError as e:
    print(f"Server error: {e}")
```

---

## Basic Error Handling

### Catch All Veda Errors

```python
from veda_client import VedaClient
from veda_client.exceptions import VedaError

client = VedaClient(base_url="http://example.com/api")

try:
    client.authenticate("user", "password")
    person = client.get_individual("person:123")
except VedaError as e:
    print(f"Error: {e}")
```

### Catch Specific Errors

```python
from veda_client.exceptions import VedaAuthError, VedaServerError

try:
    client.authenticate("user", "password")
except VedaAuthError:
    print("Invalid credentials")
except VedaServerError:
    print("Server is not responding")
```

---

## Common Error Scenarios

### Authentication Errors

```python
from veda_client import VedaClient
from veda_client.exceptions import VedaAuthError

client = VedaClient(base_url="http://example.com/api")

try:
    client.authenticate("admin", "wrong_password")
except VedaAuthError as e:
    print("Authentication failed. Check your credentials.")
    # Re-prompt for credentials or log the error
```

### Missing Ticket

```python
from veda_client.exceptions import VedaAuthError

client = VedaClient(base_url="http://example.com/api")

try:
    # Attempting operation without authentication
    person = client.get_individual("person:123")
except VedaAuthError as e:
    print("Not authenticated. Please login first.")
    client.authenticate("user", "password")
    person = client.get_individual("person:123")
```

### Invalid Individual URI

```python
from veda_client.exceptions import VedaResponseError

try:
    person = client.get_individual("invalid-uri-format")
except VedaResponseError as e:
    print(f"Individual not found or URI is invalid: {e}")
```

### Server Errors

```python
from veda_client.exceptions import VedaServerError
import time

max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        person = client.get_individual("person:123")
        break  # Success
    except VedaServerError as e:
        retry_count += 1
        if retry_count < max_retries:
            print(f"Server error, retrying ({retry_count}/{max_retries})...")
            time.sleep(2)
        else:
            print(f"Failed after {max_retries} attempts: {e}")
            raise
```

---

## Comprehensive Error Handling

### Full Try-Except Pattern

```python
from veda_client import VedaClient
from veda_client.exceptions import (
    VedaError,
    VedaAuthError,
    VedaRequestError,
    VedaResponseError,
    VedaServerError
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = VedaClient(base_url="http://example.com/api")

try:
    # Authenticate
    client.authenticate("admin", "password")
    
    # Perform operations
    person = client.get_individual("person:alice")
    person.set_value("v-s:email", "new@example.com", "string")
    client.put_individual(person)
    
    logger.info("Operation completed successfully")
    
except VedaAuthError as e:
    logger.error(f"Authentication failed: {e}")
    # Handle auth error - maybe re-authenticate or notify user
    
except VedaRequestError as e:
    logger.error(f"Invalid request: {e}")
    # Handle invalid request - check parameters
    
except VedaResponseError as e:
    logger.error(f"Operation failed: {e}")
    # Handle failed operation - maybe rollback or retry
    
except VedaServerError as e:
    logger.error(f"Server error: {e}")
    # Handle server error - retry or notify admin
    
except VedaError as e:
    logger.error(f"Unexpected Veda error: {e}")
    # Handle any other Veda errors
    
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle non-Veda errors
    raise
```

---

## Validation and Prevention

### Validate Before Operations

```python
from veda_client.models import Individual

def create_person_safely(client, uri, first_name, last_name, email):
    """Create a person with validation."""
    
    # Validate inputs
    if not uri or not uri.startswith("person:"):
        raise ValueError("Invalid person URI")
    
    if not first_name or not last_name:
        raise ValueError("First name and last name are required")
    
    if not email or "@" not in email:
        raise ValueError("Invalid email address")
    
    try:
        # Create individual
        person = Individual(uri=uri)
        person.add_value("rdf:type", "v-s:Person", "uri")
        person.add_value("v-s:firstName", first_name, "string")
        person.add_value("v-s:lastName", last_name, "string")
        person.add_value("v-s:email", email, "string")
        
        # Save
        result = client.put_individual(person)
        return True
        
    except VedaError as e:
        print(f"Failed to create person: {e}")
        return False

# Usage
success = create_person_safely(
    client,
    "person:john-doe",
    "John",
    "Doe",
    "john@example.com"
)
```

### Check Session Before Operations

```python
def ensure_authenticated(client, login, password):
    """Ensure client is authenticated."""
    try:
        if not client.is_ticket_valid():
            print("Session expired, re-authenticating...")
            client.authenticate(login, password)
    except VedaAuthError:
        print("Not authenticated, logging in...")
        client.authenticate(login, password)

# Usage
ensure_authenticated(client, "admin", "password")
person = client.get_individual("person:123")
```

---

## Retry Logic

### Simple Retry

```python
from veda_client.exceptions import VedaServerError
import time

def get_individual_with_retry(client, uri, max_retries=3):
    """Get individual with automatic retry on server errors."""
    for attempt in range(max_retries):
        try:
            return client.get_individual(uri)
        except VedaServerError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Server error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise  # Re-raise after all retries exhausted
    
# Usage
person = get_individual_with_retry(client, "person:123")
```

### Advanced Retry with Exponential Backoff

```python
from veda_client.exceptions import VedaError, VedaServerError
import time
import random

def retry_operation(func, max_retries=3, backoff_factor=2):
    """
    Retry an operation with exponential backoff.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        backoff_factor: Backoff multiplier
    """
    for attempt in range(max_retries):
        try:
            return func()
        except VedaServerError as e:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                wait_time = (backoff_factor ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"All {max_retries} attempts failed")
                raise
        except VedaError as e:
            # Don't retry on non-server errors
            print(f"Non-retryable error: {e}")
            raise

# Usage
person = retry_operation(lambda: client.get_individual("person:123"))
```

---

## Logging Errors

### Setup Logging

```python
import logging
from veda_client import VedaClient
from veda_client.exceptions import VedaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("veda_client.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("veda_client")

client = VedaClient(base_url="http://example.com/api")

try:
    client.authenticate("admin", "password")
    logger.info("Authentication successful")
except VedaError as e:
    logger.error(f"Authentication failed: {e}", exc_info=True)
```

---

## Best Practices

### 1. Always Handle Authentication Errors

```python
from veda_client.exceptions import VedaAuthError

try:
    client.authenticate("user", "password")
except VedaAuthError:
    # Don't continue if authentication fails
    print("Cannot proceed without authentication")
    exit(1)
```

### 2. Use Specific Exception Classes

```python
# Good - handle specific errors differently
try:
    person = client.get_individual("person:123")
except VedaAuthError:
    print("Not authenticated")
except VedaServerError:
    print("Server error")
except VedaResponseError:
    print("Operation failed")

# Bad - catches everything the same way
try:
    person = client.get_individual("person:123")
except Exception:
    print("Something went wrong")
```

### 3. Log Errors for Debugging

```python
import logging

try:
    client.put_individual(person)
except VedaError as e:
    logging.error(f"Failed to save person: {e}", exc_info=True)
    raise
```

### 4. Clean Up Resources

```python
try:
    client.authenticate("user", "password")
    # Perform operations
    person = client.get_individual("person:123")
except VedaError as e:
    print(f"Error: {e}")
finally:
    # Always logout when done
    try:
        client.logout()
    except:
        pass  # Ignore logout errors
```

### 5. Provide User-Friendly Messages

```python
from veda_client.exceptions import VedaAuthError, VedaResponseError

try:
    client.put_individual(person)
except VedaAuthError:
    print("Your session has expired. Please log in again.")
except VedaResponseError:
    print("Unable to save changes. Please check your data and try again.")
except Exception as e:
    print(f"An unexpected error occurred. Please contact support. Error: {e}")
```


# Installation

This guide explains how to install the Veda Python Client.

## Requirements

- Python 3.6 or higher
- pip package manager

## Installation Methods

### Method 1: Install from PyPI (when published)

```bash
pip install veda-client
```

### Method 2: Install from Source

1. Clone the repository:

```bash
git clone https://github.com/your-org/veda-python-client.git
cd veda-python-client
```

2. Install the package:

```bash
pip install .
```

### Method 3: Install in Development Mode

If you want to modify the code while using the library:

```bash
git clone https://github.com/your-org/veda-python-client.git
cd veda-python-client
pip install -e .
```

### Method 4: Install from Wheel

If you have a wheel file:

```bash
pip install veda_client-0.1.3-py3-none-any.whl
```

## Verify Installation

After installation, verify that the library is installed correctly:

```python
import veda_client
print(veda_client.__version__)
```

## Dependencies

The library automatically installs the following dependencies:

- **requests**: HTTP library for making API calls

## Upgrade

To upgrade to the latest version:

```bash
pip install --upgrade veda-client
```

## Uninstall

To remove the library:

```bash
pip uninstall veda-client
```


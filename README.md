# UltraDNS REST API Client for Python

This is a Python client for communicating with the UltraDNS REST API. It provides a simple and intuitive interface for interacting with the UltraDNS services.

Jump To:

* [Getting Started](#Getting-Started)
* [Usage](#Usage)
* [Functionality](#Functionality)
* [API Reference](#API-Reference)
* [Contributing](#Contributing)
* [License](#License)
* [Questions](#Questions)

## Getting Started

### Dependencies and Installation

This sample code depends on the requests library, which can be found at: http://docs.python-requests.org/en/latest/

If you have pip installed, you can add the client and requests to your environment with:

```
pip install ultra_rest_client
```

Once installed, you can use the `ultra_rest_client` module in your Python scripts:

```python
from ultra_rest_client import RestApiClient
client = RestApiClient(args)
```

## Usage

### Authentication

#### Authenticating using Username and Password

```python
from ultra_rest_client import RestApiClient

client = RestApiClient(your_username, your_password)

domain = "udns-python-rest-client-test.com."

# Get Zone Metadata
print(f"Get metadata for zone {domain}: {client.get_zone_metadata(domain)}")
```

#### Authenticating using Bearer Token and Refresh Token

```python
from ultra_rest_client import RestApiClient

client = RestApiClient(your_bearer_token, your_refresh_token, use_token=True)

domain = "udns-python-rest-client-test.com."

# Get Zone Metadata
print(f"Get metadata for zone {domain}: {client.get_zone_metadata(domain)}")
``` 

#### Authenticating using Bearer Token

```python
from ultra_rest_client import RestApiClient

client = RestApiClient(your_bearer_token, use_token=True)

domain = "udns-python-rest-client-test.com."

# Get Zone Metadata
print(f"Get metadata for zone {domain}: {client.get_zone_metadata(domain)}")
```

### Quick Examples
This example shows a complete working python file which will create a primary zone in UltraDNS. This example highlights how to get services using client and make requests.

```python
#!/usr/bin/env python3

from ultra_rest_client import RestApiClient
import sys

def create_zone(client, domain):
    """Create a zone in UltraDNS. This function will create a zone with the name specified in the domain argument.
    It uses the accounts API to get the account name. This is required to create a zone.

    Args:
    - client (RestApiClient): An instance of the RestApiClient class.
    - domain (str): The domain name to be created.

    Returns:
    - dict: The response body.
    """
    account_details = client.get_account_details()
    account_name = account_details['accounts'][0]['accountName']
    return client.create_primary_zone(account_name, domain)

def create_a_record(client, domain):
    """Create an A record in UltraDNS. This function will create an A record with the name specified in the domain

    Args:
    - client (RestApiClient): An instance of the RestApiClient class.
    - domain (str): The domain name.
    """
    return client.create_rrset(domain, "A", domain, 300, "192.0.2.1")


def create_cname_record(client, domain):
    """Create a CNAME record in UltraDNS. This function will create a CNAME record with the name specified in the domain

    Args:
    - client (RestApiClient): An instance of the RestApiClient class.
    - domain (str): The domain name.

    Returns:
    - dict: The response body.
    """
    return client.create_rrset(domain, "CNAME", f"www.{domain}", 300, [domain])

def delete_zone(client, domain):
    """Delete the zone from UltraDNS.

    Args:
    - client (RestApiClient): An instance of the RestApiClient class.
    - domain (str): The domain name.
    """
    client.delete_zone(domain)
    return "Zone deleted Successfully"

def main():
    """The main function. This is the entry point for the script. It parses the command line arguments and calls the
    create_zone, create_a_record, and create_cname_record functions."""

    username = sys.argv[1]
    password = sys.argv[2]
    domain = "ultra-rest-client-test.com."

    # Create an instance of your client
    client = RestApiClient(username, password)

    # Create the domain
    print(f"Creating zone {domain}: {create_zone(client, domain)}")

    # Create an A record for the domain
    print(f"Creating an A record pointing to 192.0.2.1: {create_a_record(client, domain)}")

    # Create a CNAME record for the domain
    print(f"Creating a 'www' CNAME pointing to {domain}: {create_cname_record(client, domain)}")

    # Delete the domain
    print(f"Deleting zone {domain}: {delete_zone(client, domain)}")

if __name__ == "__main__":
    main()
```

## Functionality

The sample code does not attempt to implement a client for all available UltraDNS REST API functionality.  It provides access to basic functionality. Adding additional functionality should be relatively straightforward, and any contributions from the UltraDNS community would be greatly appreciated. See [sample.py](sample.py) for an example of how to use this library in your own code.

## API Reference

For detailed API reference, please refer to the UltraDNS API documentation.

## Contributing

Contributions are always welcome! Please open a pull request with your changes, or open an issue if you encounter any problems or have suggestions.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Questions

Please contact UltraDNS support if you have any questions or encounter any issues with this code.


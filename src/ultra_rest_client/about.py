__version__ = "0.0.0"
PREFIX = "udns-python-rest-client-"

def get_client_user_agent():
    return f"{PREFIX}{__version__}"
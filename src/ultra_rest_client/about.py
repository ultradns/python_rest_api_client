__version__ = "2.2.4"
PREFIX = "udns-python-rest-client-"

def get_client_user_agent():
    return f"{PREFIX}{__version__}"
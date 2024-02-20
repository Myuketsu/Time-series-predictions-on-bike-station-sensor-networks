import os

def load_variables_env(file: str):
    """Load variables from a file into the environment."""
    with open(file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                name, value = line.strip().split('=', 1)
                os.environ[name] = value

path = 'variables.env'
load_variables_env(path)

api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
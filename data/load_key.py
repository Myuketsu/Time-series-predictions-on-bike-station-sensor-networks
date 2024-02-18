import os

def load_variables_env(file: str):
    """Load variables from a file into the environment."""
    with open(file, 'r') as f:
        for ligne in f:
            if ligne.strip() and not ligne.startswith('#'):
                nom, valeur = ligne.strip().split('=', 1)
                os.environ[nom] = valeur

chemin_fichier_env = 'variables.env'
load_variables_env(chemin_fichier_env)

api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
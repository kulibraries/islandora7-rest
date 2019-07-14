# This is a completely optional shortcut
# Priority is 1) real environment variable, 2) .env 3) defaults here

# Example:
# import islandora7_rest.config as config
# from islandora7_rest import IslandoraClient
# client = IslandoraClient(config.ISLANDORA_REST,
#                           user=ISLANDORA_USER,
#                           token=ISLANDORA_TOKEN)


import os, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(sys.path[0], '.env'))

ISLANDORA_REST = os.getenv("ISLANDORA_REST",
                           "http://localhost:8000/islandora/rest/")
ISLANDORA_USER = os.getenv("ISLANDORA_USER", "admin")
ISLANDORA_TOKEN = os.getenv("ISLANDORA_TOKEN", "password")
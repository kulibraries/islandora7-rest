from islandora7_rest import IslandoraClient
import islandora7_rest.config as islandora_config

islandora_client = IslandoraClient(islandora_config.ISLANDORA_REST,
                                   islandora_config.ISLANDORA_USER,
                                   islandora_config.ISLANDORA_TOKEN)

import os

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
""" ENV:BEARER_TOKEN: The Bearer Token used to authenticate to harvest with """

HARVEST_ACCOUNT = os.getenv("HARVEST_ACCOUNT_ID", "1121001")
""" ENV:HARVEST_ACCOUNT_ID:  Your harvest account ID """

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/clients.yaml")
""" ENV:CONFIG_PATH: The config path to load when looking for the Harvest Config """

BUCKET = os.getenv("BUCKET")
""" ENV:BUCKET: The GCP Storage Bucket to fetch config from """


class strings:
    """ Class to house string literals """

    bearer_token_help = "bearer token to use for the harvest-client"
    config_path_help = "path location to find the harvest-client config"
    account_id_help = "your harvest client id"


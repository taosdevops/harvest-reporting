import logging
import os
import sys

import google.cloud.logging as cloud_logging
import harvest
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud.logging.resource import Resource
from google.cloud import secretmanager
from harvest.harvest import Client, Clients, Harvest
from harvest.harvestdataclasses import PersonalAccessToken

from harvestapi.customer import HarvestCustomer, get_recipients_from_config
from reporting.config import ReporterConfig, EnvironmentConfiguration
from reporting.notifications import NotificationManager
from reporting.utils import load_yaml, load_yaml_file, read_cloud_storage

from typing import List
import sys

HARVEST_ENDPOINT = "https://api.harvestapp.com/api/v2"
LOGGER = logging.getLogger()
ENV_CONFIG = EnvironmentConfiguration()


def setup_logging():
    log_level = ENV_CONFIG.log_level
    stdout = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdout.setFormatter(formatter)
    LOGGER.addHandler(stdout)

    if log_level == "debug":
        LOGGER.setLevel(logging.DEBUG)
    elif log_level == "warning":
        LOGGER.setLevel(logging.WARNING)
    elif log_level == "error":
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)


def filter_customers(clients: Clients, customer_filter: list = None) -> List[Client]:
    if not customer_filter:
        return [customer for customer in clients.clients if customer.is_active]

    return [
        customer
        for customer in clients.clients
        if customer.is_active and customer.name in customer_filter
    ]


def main_method(
    bearer_token: str,
    harvest_account: str,
    global_config: ReporterConfig,
    from_email: str,
    exception_hooks: str = None,
):

    personal_access_token = PersonalAccessToken(harvest_account, bearer_token)
    client = harvest.Harvest(HARVEST_ENDPOINT, personal_access_token)

    customer_filter = global_config.customer_filter

    customers = client.clients()
    active_customers = filter_customers(customers, customer_filter=customer_filter)

    harvest_customers = []

    # Finds all active customers with a corresponding config in the config file.
    # If the config exists, create a new HarvestCustomer to tie the config and
    # Harvest API data together.
    for active_customer in active_customers:
        for customer in global_config.customers:
            if active_customer.name == customer.name:
                harvest_customers.append(
                    HarvestCustomer(
                        client,
                        customer,
                        get_recipients_from_config(customer, global_config),
                        active_customer,
                    )
                )

    notifications = NotificationManager(
        customers=harvest_customers,
        global_recipients=global_config.recipients,
        exception_config=global_config.exceptions,
        sendgrid_api_key=ENV_CONFIG.sendgrid_api_key,
        from_email=ENV_CONFIG.origin_email_address,
    )

    notifications.send()


def harvest_reports(*args):
    setup_logging()

    LOGGER.debug("Loading config")

    ENV_CONFIG = EnvironmentConfiguration()

    if not ENV_CONFIG.bucket:
        LOGGER.debug(f"Fetching config from file system: {ENV_CONFIG.config_path}")
        global_config = load_yaml_file(ENV_CONFIG.config_path)
    else:
        LOGGER.debug(
            f"Fetching config from GCS bucket: gs://{ENV_CONFIG.bucket}/{ENV_CONFIG.config_path}"
        )
        global_config = load_yaml(
            read_cloud_storage(ENV_CONFIG.bucket, ENV_CONFIG.config_path)
        )

    LOGGER.info(f"Effective config: {global_config}")

    return main_method(
        bearer_token=ENV_CONFIG.bearer_token,
        harvest_account=ENV_CONFIG.harvest_account,
        global_config=global_config,
        from_email=ENV_CONFIG.origin_email_address,
    )


if __name__ == "__main__":
    harvest_reports()

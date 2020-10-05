import logging
import os
import sys
from typing import List

import harvest
from google.cloud import secretmanager
from harvest.harvest import Harvest
from harvest.harvestdataclasses import Client, Clients, PersonalAccessToken

from harvestapi.customer import HarvestCustomer, get_recipients_from_config
import reporting.config
from reporting.notifications import NotificationManager

HARVEST_ENDPOINT = "https://api.harvestapp.com/api/v2"
LOGGER = logging.getLogger()


def setup_logging(log_level):
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


def harvest_reports(*args):
    ENV_CONFIG = reporting.config.EnvironmentConfiguration()
    setup_logging(ENV_CONFIG.log_level)


    LOGGER.debug("Loading config")

    global_config = reporting.config.load(ENV_CONFIG.config_path, bucket=ENV_CONFIG.bucket, project=ENV_CONFIG.project_id)

    LOGGER.info(f"Effective config: {global_config}")

    personal_access_token = PersonalAccessToken(ENV_CONFIG.harvest_account, ENV_CONFIG.bearer_token)
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

if __name__ == "__main__":
    harvest_reports()

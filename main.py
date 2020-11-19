import logging
import os
import sys
from typing import List

import harvest
from google.cloud import secretmanager
from harvest.harvest import Harvest
from harvest.harvestdataclasses import Client, Clients, PersonalAccessToken

import reporting.config
from harvestapi.customer import HarvestCustomer, get_recipients_from_config
from reporting.notifications import NotificationManager

LOGGER = logging.getLogger()


def get_harvest_client():
    personal_access_token = PersonalAccessToken(reporting.config.HARVEST_ACCOUNT_ID, reporting.config.BEARER_TOKEN)
    client = Harvest("https://api.harvestapp.com/api/v2", personal_access_token)
    return client


def setup_logging(log_level):
    stdout = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdout.setFormatter(formatter)
    LOGGER.addHandler(stdout)
    level = getattr(logging, log_level.upper())
    LOGGER.setLevel(level)


def filter_customers(clients: Clients, customer_filter: list = None) -> List[Client]:
    if not customer_filter:
        return [customer for customer in clients.clients if customer.is_active]

    return [
        customer
        for customer in clients.clients
        if customer.is_active and customer.name in customer_filter
    ]


def harvest_reports(*args):
    setup_logging(reporting.config.LOG_LEVEL)

    LOGGER.debug("Loading config")

    global_config = reporting.config.load(
        fname=reporting.config.CONFIG_PATH,
        bucket=reporting.config.BUCKET, 
        project=reporting.config.GCP_PROJECT
        )

    LOGGER.info(f"Effective config: {global_config}")

    client = get_harvest_client()

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
        sendgrid_api_key=reporting.config.SENDGRID_API_KEY,
        from_email=reporting.config.ORIGIN_EMAIL_ADDRESS,
    )

    notifications.send()

if __name__ == "__main__":
    harvest_reports()

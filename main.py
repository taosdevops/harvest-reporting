import logging
import os
import sys

from python_http_client.exceptions import BadRequestsError, UnauthorizedError
from taosdevopsutils.slack import Slack

from hreporting import config, utils
from hreporting.emails import SendGridSummaryEmail, SendGridTemplateEmail
from hreporting.harvest_client import HarvestClient
from hreporting.notifications import NotificationManager
from hreporting.utils import (load_yaml, load_yaml_file, print_verify,
                              read_cloud_storage, truncate)

logging.getLogger("harvest_reports")
logging.basicConfig(format="%(asctime)s %(message)s")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def client_is_filtered(client, filter_list=None):
    if not filter_list:
        return client["is_active"]
    else:
        return client["is_active"] and client["name"] in filter_list


def main_method(
    bearer_token, harvest_account, client_config, from_email, exception_hooks=None
):
    harvest_client = HarvestClient(bearer_token, harvest_account, client_config)
    client_filter = client_config.get("client_filter", [])

    notification = NotificationManager(
        from_email, client_config.get("emailTemplateId", None)
    )

    active_clients = [
        client

        for client in harvest_client.list_clients()

        if client_is_filtered(client, filter_list=client_filter)
    ]

    for client in active_clients:
        notification.send(harvest_client, client, exception_hooks)

    if client_config.get("sendVerificationHook"):
        notification.completion_notification(
            client_config.get("sendVerificationHook"), active_clients=active_clients
        )


def harvest_reports(*args):
    bearer_token = config.BEARER_TOKEN
    bucket = config.BUCKET
    config_path = config.CONFIG_PATH
    harvest_account = config.HARVEST_ACCOUNT
    from_email = config.ORIGIN_EMAIL_ADDRESS

    client_config = (
        load_yaml_file(config_path)

        if not bucket
        else load_yaml(read_cloud_storage(bucket, config_path))
    )

    return main_method(
        bearer_token=bearer_token,
        harvest_account=harvest_account,
        client_config=client_config,
        from_email=from_email,
        exception_hooks=client_config.get("exceptionHook"),
    )


if __name__ == "__main__":
    harvest_reports()

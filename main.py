import logging
import os
import sys

from python_http_client.exceptions import BadRequestsError, UnauthorizedError
from taosdevopsutils.slack import Slack

from hreporting.emails import SendGridSummaryEmail
from hreporting.harvest_client import HarvestClient
from hreporting.utils import (channel_post, exception_channel_post, load_yaml,
                              load_yaml_file, print_verify, read_cloud_storage,
                              truncate)

from hreporting import config
from hreporting import utils

logging.getLogger("harvest_reports")
logging.basicConfig(format="%(asctime)s %(message)s")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main_method(
        bearer_token, harvest_account, client_config, from_email,
        exception_hooks=None):
    harvest_client = HarvestClient(bearer_token, harvest_account, client_config)

    active_clients = [
        client for client in harvest_client.list_clients() if
        client["is_active"] and client["name"] in client_config.get("client_filter",[])
    ]

    for client in active_clients:
        _send_notifications(harvest_client, client, from_email, exception_hooks)


def _send_notifications(
        harvest_client, client, from_email,
        exception_hooks=None) -> None:

    clientId = client["id"]
    clientName = client["name"]

    hours_used = harvest_client.get_client_time_used(clientId)
    total_hours = harvest_client.get_client_time_allotment(clientName)
    hours_left = total_hours - hours_used

    used = truncate(hours_used, 2)
    left = truncate(hours_left, 2)

    percent = used / total_hours * 100

    print_verify(used, clientName, percent, left)

    client_hooks = harvest_client.get_client_hooks(clientName)

    for hook in client_hooks["hooks"]:
        try:
            channel_post(hook, used, clientName, percent, left)
        except Exception:
            if exception_hooks:
                for ehook in exception_hooks:
                    utils.exception_channel_post(
                        clientName, ehook,
                        f"Original Hook:{hook}\n"
                    )

def harvest_reports(*args):
    bearer_token    = config.BEARER_TOKEN
    bucket          = config.BUCKET
    config_path     = config.CONFIG_PATH
    harvest_account = config.HARVEST_ACCOUNT
    from_email      = config.ORIGIN_EMAIL_ADDRESS

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
        exception_hooks=client_config.get("exceptionHook")
    )

if __name__ == "__main__":
    harvest_reports()

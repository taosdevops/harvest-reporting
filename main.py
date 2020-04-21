import logging
import os

import sendgrid
from python_http_client.exceptions import UnauthorizedError

from hreporting.emails import SendGridSummaryEmail
from hreporting.harvest_client import HarvestClient
from hreporting.utils import (channel_post, exception_channel_post, load_yaml,
                              load_yaml_file, print_verify, read_cloud_storage,
                              truncate)


def main_method(bearer_token, harvest_account, send_grid_api, config, from_email):
    harvest_client = HarvestClient(bearer_token, harvest_account, config)

    sg_client = sendgrid.SendGridAPIClient(api_key=send_grid_api)

    active_clients = [
        client for client in harvest_client.list_clients() if client["is_active"]
    ]

    for client in active_clients:
        _send_notifications(harvest_client, sg_client, client, from_email)


def _send_notifications(harvest_client, sg_client, client, from_email) -> None:

    try:
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

        [
            channel_post(hook, used, clientName, percent, left)

            for hook in client_hooks["hooks"]
        ]

        email_summary = SendGridSummaryEmail(
            clientName,
            client_hooks["emails"],
            left,
            percent,
            sg_client,
            used,
            from_email,
        )
        email_summary.email_send()

    except UnauthorizedError as unauthorized:
        logging.error(unauthorized)
        exception_channel_post(
            unauthorized, client, harvest_client.get_exception_hook()
        )


def harvest_reports(*args):
    bearer_token = os.getenv("BEARER_TOKEN")
    bucket = os.getenv("BUCKET")
    config_path = os.getenv("CONFIG_PATH", "config/clients.yaml")
    harvest_account = os.getenv("HARVEST_ACCOUNT_ID", "1121001")
    send_grid_api = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("ORIGIN_EMAIL_ADDRESS", "DevOpsNow@taos.com")

    config = (
        load_yaml_file(config_path)

        if not bucket
        else load_yaml(read_cloud_storage(bucket, config_path))
    )

    return main_method(bearer_token, harvest_account, send_grid_api, config, from_email)


if __name__ == "__main__":
    harvest_reports()

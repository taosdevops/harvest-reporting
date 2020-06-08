import logging
import sys

from reporting import config
from harvestapi.client import HarvestAPIClient
from reporting.notifications import NotificationManager
from reporting.utils import (
    load_yaml,
    load_yaml_file,
    print_verify,
    read_cloud_storage,
    truncate,
)

logging.getLogger("harvest_reports")
logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(message)s"
)


def client_is_filtered(client, filter_list=None):
    if not filter_list:
        return client["is_active"]

    return client["is_active"] and client["name"] in filter_list


def main_method(
    bearer_token: str,
    harvest_account: str,
    global_config: str,
    from_email: str,
    exception_hooks: str = None,
):
    harvestapi_client = HarvestAPIClient(bearer_token, harvest_account, global_config)
    client_filter = global_config.get("client_filter", [])

    active_clients = [
        client
        for client in harvestapi_client.list_clients()
        if client_is_filtered(client, filter_list=client_filter)
    ]

    _send_notifications(
        harvestapi_client=harvestapi_client,
        active_clients=active_clients,
        from_email=from_email,
        global_config=global_config,
        exception_hooks=exception_hooks,
    )


def _send_notifications(
    harvestapi_client, active_clients, from_email, global_config, exception_hooks=None
) -> None:

    notifications = NotificationManager(
        clients=active_clients,
        fromEmail=from_email,
        exceptionHooks=global_config.get("exceptionHook"),
        emailTemplateId=global_config.get("emailTemplateId", None),
        harvestapi_client=harvestapi_client,
    )

    notifications.send()

    notifications.send_completion(
        verification_hook=global_config.get("sendVerificationHook"),
        clients=active_clients,
    )


def harvest_reports(*args):
    bearer_token = config.BEARER_TOKEN
    bucket = config.BUCKET
    config_path = config.CONFIG_PATH
    harvest_account = config.HARVEST_ACCOUNT
    from_email = config.ORIGIN_EMAIL_ADDRESS

    if not bucket:
        global_config = load_yaml_file(config_path)
    else:
        global_config = load_yaml(read_cloud_storage(bucket, config_path))

    return main_method(
        bearer_token=bearer_token,
        harvest_account=harvest_account,
        global_config=global_config,
        from_email=from_email,
    )


if __name__ == "__main__":
    harvest_reports()

import logging
import traceback

import yaml
from google.cloud import storage
from python_http_client.client import Response
from taosdevopsutils.slack import Slack
from sendgridapi.emails import SendGridSummaryEmail
from dacite import from_dict
from .config import ReporterConfig, EnvironmentConfiguration

SENDGRID_EMAILER = SendGridSummaryEmail()
SLACK_CLIENT = Slack()
ENV_CONFIG = EnvironmentConfiguration()


logger = logging.getLogger(__name__)


# Define decimal place to truncate
def truncate(n, decimals=0) -> float:
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def load_yaml_file(file_handle) -> ReporterConfig:
    return from_dict(
        data_class=ReporterConfig, data=yaml.load(open(file_handle), Loader=yaml.Loader)
    )


def load_yaml(yaml_string) -> ReporterConfig:
    return from_dict(
        data_class=ReporterConfig, data=yaml.load(yaml_string, Loader=yaml.Loader)
    )


def read_cloud_storage(bucket_name, file_name) -> str:
    """ Returns file contents from provided bucket and file names """
    client = storage.Client(project=ENV_CONFIG.project_id)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_name)
    response = blob.download_as_string()

    return response


def completion_notification(
    hook: str, active_clients: list, slack_client=SLACK_CLIENT
) -> dict:
    """
    Simple send to add a completion notice to the end of the client send.
    Makes it easy to see at the end of a notification block that all clients were sent.
    """

    active_client_count = str(len(active_clients))
    active_client_names = "\n".join([client["name"] for client in active_clients])

    fields = [
        {
            "title": "Client contacts attempted",
            "value": active_client_names,
            "short": "true",
        }
    ]

    for client in active_clients:
        fields.append(
            {"title": client["name"], "value": success_check(client), "short": "true"}
        )

    data = {
        "attachments": [
            {
                "color": "#ff00ff",
                "title": "Client Daily Hour reporting completed.",
                "text": "Clients in the list %s" % active_client_count,
                "fields": fields,
            }
        ]
    }

    response = slack_client.post_slack_message(hook, data)

    return response


def success_check(client: dict) -> str:
    question = client["result"]

    if type(question) is dict:
        return question["status_code"]

    if type(question) is Response:
        return question.status_code

    return f"{client['name']}: Caused an unexpected response"


def exception_channel_post(
    client_name: str, webhook_url: str, *args, slack_client=SLACK_CLIENT
) -> dict:
    """
    Performs a protected attempt to send slack message about an error.
    Wraps try blocks for assurance that the message will not further break the system.
    """

    data = {
        "attachments": [
            {
                "color": "#ff0000",
                "title": f"Exception while processing {client_name}",
                "text": "".join([*args, traceback.format_exc(limit=3)]),
            }
        ]
    }

    try:
        response = slack_client.post_slack_message(webhook_url, data)
        logging.error(response)

        return response
    except Exception:
        logging.error(traceback.format_exc(limit=3))

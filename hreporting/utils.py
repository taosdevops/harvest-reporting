import logging
import re
import traceback

import yaml
from google.cloud import storage
from slack.errors import SlackApiError
from taosdevopsutils.slack import Slack

from hreporting.emails import SendGridSummaryEmail

SENDGRID_EMAILER = SendGridSummaryEmail()
SLACK_CLIENT = Slack()

logging.getLogger("harvest_reports")


def print_verify(used, client_name, percent, left) -> None:
    """ Print Details for verification """

    hour_report_template = """
    Client:           {name}
    Used Hours:       {used}
    Remaining Hours:  {left}
    Color:            {color}
    Percent:          {percent}
    """
    logging.info(
        str.format(
            hour_report_template,
            name=client_name,
            used=used,
            left=left,
            percent="%d%%" % (percent),
            color=get_color_code_for_utilization(percent),
        )
    )


# Define decimal place to truncate
def truncate(n, decimals=0) -> float:
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def load_yaml_file(file_handle):
    return yaml.load(open(file_handle), Loader=yaml.Loader)


def load_yaml(yaml_string):
    return yaml.load(yaml_string, Loader=yaml.Loader)


def get_color_code_for_utilization(percent) -> str:
    blue = "#0000ff"
    green = "#33cc00"
    yellow = "#ffcc00"
    orange = "#ff6600"
    red = "#ff0000"

    if percent < 40:
        return blue

    if percent < 65:
        return green

    if percent < 87:
        return yellow

    if percent < 95:
        return orange

    return red


# Define types of payloads
def get_payload(used, client_name, percent, left, _format="slack") -> dict:
    """ Get payload for every type of format"""
    try:

        return {
            "slack": get_slack_payload,
            "teams": get_teams_payload,
            "email": get_email_payload,
        }[_format](used, client_name, percent, left)

    except KeyError:
        raise Exception(f"Invalid Payload format {_format}")


def get_slack_payload(used, client_name, percent, left, *args) -> dict:
    """ Format JSON body for Slack channel posting"""

    return {
        "attachments": [
            {
                "color": get_color_code_for_utilization(percent),
                "title": client_name,
                "text": "%d%%" % (percent),
                "fields": [
                    {"title": "Hours Used", "value": used, "short": "true"},
                    {"title": "Hours Remaining", "value": left, "short": "true"},
                ],
            }
        ]
    }


def get_teams_payload(used, client_name, percent, left, *args) -> dict:
    """ Format JSON body for MS Teams channel post"""

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": get_color_code_for_utilization(percent),
        "title": "DevOps Time Reports",
        "text": client_name,
        "sections": [
            {"text": "%d%%" % (percent)},
            {"activityTitle": "Hours Used", "activitySubtitle": used},
            {"activityTitle": "Hours Remaining", "activitySubtitle": left},
        ],
    }


def get_email_payload(used, client_name, percent, left, *args) -> str:
    return f"""
    Client:           {client_name}
    Used Hours:       {used}
    Remaining Hours:  {left}
    Percent:          {percent}
    """


# Post to channel/workspace
def channel_post(
    webhook_url: str,
    used,
    client_name,
    percent,
    left,
    slack_client=SLACK_CLIENT,
    sg_client=SENDGRID_EMAILER,
) -> dict:
    """ Posts payload to webhook provided """

    if webhook_url:
        post_format = (  # Identify Type of payload
            "teams"

            if webhook_url.startswith("https://outlook.office.com")
            else "email"

            if re.match(r"[^@]+@[^@]+\.[^@]+", webhook_url)
            else "slack"
        )

        data = get_payload(used, client_name, percent, left, _format=post_format)

        if post_format == "email":
            response = sg_client.email_send([webhook_url], client_name, data)
        else:
            response = slack_client.post_slack_message(webhook_url, data)

        logging.info(response)

        return response

    logging.warning("No webhook url found for %client_name", client_name)

    return dict()


def read_cloud_storage(bucket_name, file_name) -> str:
    """ Returns file contents from provided bucket and file names """
    client = storage.Client()
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

    data = {
        "attachments": [
            {
                "color": "#ff00ff",
                "title": "Client Daily Hour reporting completed.",
                "text": "Clients in the list %s" % active_client_count,
                "fields": [
                    {
                        "title": "Clients contacted",
                        "value": active_client_names,
                        "short": "true",
                    }
                ],
            }
        ]
    }

    response = slack_client.post_slack_message(hook, data)

    return response


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

    response = slack_client.post_slack_message(webhook_url, data)
    logging.error(response)

    return response

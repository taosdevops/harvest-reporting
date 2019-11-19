import yaml
import requests
import json
from google.cloud import storage
from taosdevopsutils.slack import Slack

# In the future if we need to auth with multiple workspaces we might need
# to move this to a factory method and pull a specific client for each token
slack_client = Slack()


def print_verify(used, clientName, percent, left) -> None:
    """ Print Details for verification """
    Hour_Report_Template = """
    Client:           {name}
    Used Hours:       {used}
    Remaining Hours:  {left}
    Color:            {color}
    Percent:          {percent}
    """
    print(
        str.format(
            Hour_Report_Template,
            name=clientName,
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


load_yaml_file = lambda file_handle: yaml.load(open(file_handle), Loader=yaml.Loader)
load_yaml = lambda yaml_string: yaml.load(yaml_string, Loader=yaml.Loader)


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


# Define if teams or slack
def get_payload(used, clientName, percent, left, *args, _format="slack") -> dict:
    if _format == "slack":
        return {
            "attachments": [
                {
                    "color": get_color_code_for_utilization(percent),
                    "title": clientName,
                    "text": "%d%%" % (percent),
                    "fields": [
                        {"title": "Hours Used", "value": used, "short": "true"},
                        {"title": "Hours Remaining", "value": left, "short": "true"},
                    ],
                }
            ]
        }
    if _format == "teams":
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": get_color_code_for_utilization(used),
            "title": "DevOps Time Reports",
            "text": clientName,
            "sections": [
                {"text": "%d%%" % (percent) },
                {"activityTitle": "Hours Used", "activitySubtitle": used },
                {"activityTitle": "Hours Remaining", "activitySubtitle": left },
            ]
        }
    raise Exception(f"Invalid Payload format {_format}")


# Post to channel/workspace
def channel_post(webhook_url: str, used, clientName, percent, left) -> dict:
    """ Posts payload to webhook provided """
    post_format = (
        "teams" if webhook_url.startswith("https://outlook.office.com") else "slack"
    )
    data = get_payload(used, clientName, percent, left, _format=post_format)
    response = slack_client.post_slack_message(webhook_url, data)
    print(response)
    return response


def read_cloud_storage(bucket_name, file_name) -> str:
    """ Returns file contents from provided bucket and file names """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_name)
    response = blob.download_as_string()
    return response

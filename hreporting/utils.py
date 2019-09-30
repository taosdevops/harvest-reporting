import yaml
import requests
import json
from google.cloud import storage
from taosdevopsutils.slack import Slack

# In the future if we need to auth with multiple workspaces we might need
# to move this to a factory method and pull a specific client for each token
slack_client = Slack()


def print_verify(used, clientName, percent, left):
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
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


load_yaml_file = lambda file_handle: yaml.load(open(file_handle), Loader=yaml.Loader)
load_yaml = lambda yaml_string: yaml.load(yaml_string, Loader=yaml.Loader)


def get_color_code_for_utilization(percent):
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


# Post to slackchannel
def slackPost(webhook_url: str, used, clientName, percent, left):
    slack_data = {
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
    response = slack_client.post_slack_message(webhook_url, slack_data)
    print(response)
    return response


def read_cloud_storage(bucket_name, file_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_name)
    response = blob.download_as_string()
    return response

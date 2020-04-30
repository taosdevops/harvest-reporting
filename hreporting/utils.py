import logging

import yaml
from google.cloud import storage

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
def get_payload(client, _format="slack") -> dict:
    """ Get payload for every type of format"""
    try:

        return {
            "slack": get_slack_payload,
            "teams": get_teams_payload,
            "email": get_email_payload,
        }[_format](
            client["hours_used"],
            client["name"],
            client["percent"],
            client["hours_left"],
        )

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


def read_cloud_storage(bucket_name, file_name) -> str:
    """ Returns file contents from provided bucket and file names """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(file_name)
    response = blob.download_as_string()

    return response

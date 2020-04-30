import logging
import re
import traceback

from taosdevopsutils.slack import Slack

from hreporting.emails import SendGridSummaryEmail, SendGridTemplateEmail
from hreporting.utils import get_payload, print_verify, truncate

logging.getLogger("harvest_reports")


class NotificationManager:
    def __init__(self, from_email, emailTemplateId):
        self.from_email = from_email
        self.emailTemplateId = emailTemplateId
        self.slack_client = Slack()

        self.emailer = (
            SendGridTemplateEmail() if self.emailTemplateId else SendGridSummaryEmail()
        )

    def send(self, harvest_client, client, exception_hooks=None) -> None:

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
                self.channel_post(hook, used, clientName, percent, left)
            except Exception:
                if exception_hooks:
                    for ehook in exception_hooks:
                        self.exception_channel_post(
                            clientName, ehook, f"Original Hook:{hook}\n"
                        )

    # Post to channel/workspace
    def channel_post(self, webhook_url: str, used, client_name, percent, left) -> dict:
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
                response = self.emailer.send([webhook_url], client_name, data)
            else:
                response = self.slack_client.post_slack_message(webhook_url, data)

            logging.info(response)

            return response

        logging.warning("No webhook url found for %client_name", client_name)

        return dict()

    def exception_channel_post(self, client_name: str, webhook_url: str, *args) -> dict:
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

        response = self.slack_client.post_slack_message(webhook_url, data)
        logging.error(response)

        return response

    def completion_notification(self, hook: str, active_clients: list) -> dict:
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

        response = self.slack_client.post_slack_message(hook, data)

        return response

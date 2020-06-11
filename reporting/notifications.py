import logging
import re
import traceback
import sys
from typing import List

from taosdevopsutils.slack import Slack

from harvest.harvest import Client
from sendgridapi.emails import SendGridSummaryEmail, SendGridTemplateEmail

from harvestapi.customer import HarvestCustomer
from .config import Recipients


logger = logging.getLogger(__name__)


class NotificationManager:
    SLACK_CLIENT = Slack()

    def __init__(self, clients: List[Client], recipients: List[Recipients]):
        self.clients = clients
        self.recipients = recipients

    # Post to channel/workspace
    def send_channel_post(self) -> dict:
        """ Posts payload to webhook provided """
        if webhook_url:
            post_format = (  # Identify Type of payload
                "teams"
                if webhook_url.startswith("https://outlook.office.com")
                else "templateEmail"
                if re.match(r"[^@]+@[^@]+\.[^@]+", webhook_url)
                and self.email_template_id
                else "email"
                if re.match(r"[^@]+@[^@]+\.[^@]+", webhook_url)
                else "slack"
            )

            data = get_payload(client, _format=post_format)

            if post_format == "email":
                response = self.emailer.send(webhook_url, client, data)
            else:
                response = NotificationManager.SLACK_CLIENT.post_slack_message(
                    webhook_url, data
                )

            logger.info(response)

            return response

        logger.warning("No webhook url found for %client_name", client.client_name)

        return dict()

    def _exception_channel_post(self, customer: HarvestCustomer, target: str) -> dict:
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

        response = NotificationManager.SLACK_CLIENT.post_slack_message(
            webhook_url, data
        )
        logger.error(response)

        return response

    @classmethod
    def send_completion(cls, verification_hook, clients: list) -> dict:
        """
        Simple send to add a completion notice to the end of the client send.
        Makes it easy to see at the end of a notification block that all clients were sent.
        """

        active_client_count = str(len(clients))
        active_client_names = "\n".join([client["name"] for client in clients])

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

        response = NotificationManager.SLACK_CLIENT.post_slack_message(
            verification_hook, data
        )

        return response

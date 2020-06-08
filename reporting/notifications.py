import logging
import re
import traceback

from taosdevopsutils.slack import Slack

from harvestapi.client import HarvestCustomer
from sendgridapi.emails import SendGridSummaryEmail, SendGridTemplateEmail
from reporting.utils import get_payload, print_verify, truncate

logging.getLogger("harvest_reports")


class NotificationManager:
    SLACK_CLIENT = Slack()

    def __init__(
        self,
        fromEmail,
        exceptionHooks,
        harvestapi_client,
        clients,
        emailTemplateId=None,
    ):

        self.harvestapi_client = harvestapi_client
        self.emailTemplateId = emailTemplateId
        self.exception_hooks = exceptionHooks
        self.from_email = fromEmail

        self.clients = [self._build_client(client) for client in clients]
        self.emailer = (
            SendGridTemplateEmail() if self.emailTemplateId else SendGridSummaryEmail()
        )

    def _build_client(self, client: dict) -> HarvestCustomer:
        client_id = client["id"]
        client_name = client["name"]

        hours_used = self.harvestapi_client.get_client_time_used(client_id)
        total_hours = self.harvestapi_client.get_client_time_allotment(client_name)
        hours_left = total_hours - hours_used
        percent = hours_used / total_hours * 100

        print_verify(hours_used, client_name, percent, hours_left)

        client_hooks = self.harvestapi_client.get_client_hooks(client_name)

        client_hooks = (
            client_hooks if isinstance(client_hooks, list) else list(client_hooks)
        )

        return HarvestCustomer(
            clientId=client_id,
            hooks=client_hooks,
            hoursLeft=hours_left,
            hoursTotal=total_hours,
            hoursUsed=hours_used,
            name=client_name,
            percent=percent,
            templateId=self.emailTemplateId,
        )

    def _hooks_send(self, client: HarvestCustomer):

        for hook in client.hooks:
            try:
                self.channel_post(hook, client)
            except Exception:
                if self.exception_hooks:
                    for ehook in self.exception_hooks:
                        self.exception_channel_post(
                            client.name, ehook, f"Original Hook:{hook}\n"
                        )

    def send(self) -> None:
        for client in self.clients:
            self._hooks_send(client)

    # Post to channel/workspace
    def channel_post(self, webhook_url: str, client: HarvestCustomer) -> dict:
        """ Posts payload to webhook provided """

        if webhook_url:
            post_format = (  # Identify Type of payload
                "teams"
                if webhook_url.startswith("https://outlook.office.com")
                else "templateEmail"
                if re.match(r"[^@]+@[^@]+\.[^@]+", webhook_url) and self.emailTemplateId
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

            logging.info(response)

            return response

        logging.warning("No webhook url found for %client_name", client.client_name)

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

        response = NotificationManager.SLACK_CLIENT.post_slack_message(
            webhook_url, data
        )
        logging.error(response)

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

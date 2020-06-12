import logging
import re
import sys
import traceback
from typing import List

import pymsteams
from harvest.harvest import Client
from taosdevopsutils.slack import Slack

from harvestapi.customer import HarvestCustomer
from sendgridapi.emails import SendGridSummaryEmail

from .config import Recipients

LOGGER = logging.getLogger(__name__)


class TeamsSendError(BaseException):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(f"Failed to send webhook to Teams channel {self.channel}")


class NotificationManager:
    SLACK_CLIENT = Slack()

    def __init__(self, customers: List[HarvestCustomer], global_recipients: Recipients):
        self.customers = customers
        self.recipients = global_recipients

    def send(self):
        for customer in self.customers:
            logging.debug(f"Starting to process notifications for {customer.data.name}")
            self._send_customer_notifications(customer)

        self._send_global_notifications()

    # Post to channel/workspace
    def _send_customer_notifications(self, customer: HarvestCustomer) -> dict:
        if customer.recipients:
            if len(customer.recipients.slack) > 0:
                self._send_slack_channels(customer.recipients.slack, [customer])

            if len(customer.recipients.teams) > 0:
                self._send_teams_channels(customer.recipients.teams, [customer])

            if len(customer.recipients.emails) > 0:
                self._send_email_channels(
                    customer.recipients.emails,
                    [customer],
                    customer.config.recipients.config.templateId,
                )

        return dict()

    def _send_global_notifications(self) -> dict:
        if self.recipients.slack:
            self._send_slack_channels(self.recipients.slack, self.customers)
        if self.recipients.teams:
            self._send_teams_channels(self.recipients.teams, self.customers)
        if self.recipients.emails:
            self._send_email_channels(
                self.recipients.emails,
                self.customers,
                self.recipients.config.templateId,
            )
        return dict()

    def _send_slack_channels(
        self, channels: List[str], customers: List[HarvestCustomer]
    ):
        for channel in channels:
            LOGGER.debug("Sending slack notification")
            response = NotificationManager.SLACK_CLIENT.post_slack_message(
                channel, self._get_slack_payload(customers)
            )
            LOGGER.debug(f"Sent slack notification")
            LOGGER.debug(f"Response: {response}")

    def _send_teams_channels(
        self, channels: List[str], customers: List[HarvestCustomer]
    ):
        for channel in channels:
            LOGGER.debug("Sending Teams notification")

            msg = pymsteams.connectorcard(channel)
            msg.payload = {
                "title": "DevOps Time Reports",
                "summary": "Accounting of currently used DevOps Now time",
                "sections": self._get_teams_sections(customers),
            }

            if not msg.send():
                raise TeamsSendError(channel)

            LOGGER.debug(f"Sent Teams notification to {channel}")

    def _send_email_channels(
        self,
        channels: List[str],
        customers: List[HarvestCustomer],
        templateId: str = "",
    ):

        LOGGER.debug("Sending email notifications")

        if templateId:
            email = SendGridSummaryEmail(templateId=templateId)
        else:
            email = SendGridSummaryEmail()

        LOGGER.debug(
            f"Response: {email.send(channels, customers, self._get_email_payload(customers))}"
        )

        LOGGER.debug(f"Sent email notification to {channels}")

    def _get_slack_payload(self, customers: List[HarvestCustomer]) -> dict:
        """ Format JSON body for Slack channel posting"""

        return {
            "attachments": [
                {
                    "color": self._get_color_code_for_utilization(
                        customer.percentage_hours_used()
                    ),
                    "title": customer.data.name,
                    "text": "%d%%" % (customer.percentage_hours_used()),
                    "fields": [
                        {
                            "title": "Hours Used",
                            "value": customer.time_used(),
                            "short": "true",
                        },
                        {
                            "title": "Hours Remaining",
                            "value": customer.time_remaining(),
                            "short": "true",
                        },
                    ],
                }
                for customer in customers
            ]
        }

    def send_exception_channel(self, customer: HarvestCustomer, target: str) -> dict:
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
        LOGGER.error(response)

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

    def _get_teams_sections(self, customers: List[HarvestCustomer]) -> List[dict]:
        sections = []
        for customer in customers:
            section = {
                "activityTitle": f"{customer.percentage_hours_used()}%",
                "text": f"Customer: {customer.data.name}",
                "facts": [
                    {"name": "Hours Used", "value": f"{customer.time_used()}"},
                    {
                        "name": "Hours Remaining",
                        "value": f"{customer.time_remaining()}",
                    },
                ],
            }
            sections.append(section)

        return sections

    def _get_email_payload(self, customers: List[HarvestCustomer]) -> List[str]:
        return "".join(
            [
                f"""Client:           {customer.data.name}
Used Hours:       {customer.time_used()}
Remaining Hours:  {customer.time_remaining()}
Percent:          {customer.percentage_hours_used()}

"""
                for customer in customers
            ]
        )

    def _get_color_code_for_utilization(self, percent: int) -> str:
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

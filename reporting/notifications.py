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


class SlackSendError(BaseException):
    def __init__(self, channel, status_code):
        self.channel = channel
        self.status_code = status_code
        super().__init__(f"Failed to send webhook to Slack channel {self.channel}. Status code: {self.status_code}")


class TeamsSendError(BaseException):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(f"Failed to send webhook to Teams channel {self.channel}.")


class EmailSendError(BaseException):
    def __init__(self, channels, status_code):
        self.channels = channels
        self.status_code = status_code
        super().__init__(f"Failed to send webhook to email addresses {self.channels}. Status code: {self.status_code}")


class NotificationManager:
    SLACK_CLIENT = Slack()

    def __init__(self, customers: List[HarvestCustomer], global_recipients: Recipients, exception_config: Recipients):
        self.customers = customers
        self.recipients = global_recipients
        self.exception_config = exception_config

    def send(self):
        for customer in self.customers:
            logging.debug(f"Starting to process notifications for {customer.data.name}")

            self._send_customer_notifications(customer)

        self._send_global_notifications()

    # Post to channel/workspace
    def _send_customer_notifications(self, customer: HarvestCustomer):
        if customer.recipients:
            if len(customer.recipients.slack) > 0:
                try:
                    self._send_slack_channels(self.recipients.slack,  self._get_slack_payload([customer]))
                except SlackSendError as e:
                    self._send_exception_channels(e, customer)

            if len(customer.recipients.teams) > 0:
                try:
                    self._send_teams_channels(self.recipients.teams,  self._get_teams_sections([customer]))
                except TeamsSendError as e:
                    self._send_exception_channels(e, customer)

            if len(customer.recipients.emails) > 0:
                try:
                    self._send_email_channels(
                        self.recipients.emails,
                        customer,
                        self._get_email_payload([customer]),
                        template_id=self.recipients.config.templateId,
                    )
                except EmailSendError as e:
                    self._send_exception_channels(e, customer)


    def _send_global_notifications(self):
        if self.recipients.slack:
            try:
                self._send_slack_channels(self.recipients.slack, self._get_slack_payload(self.customers))
            except Exception as e:
                self._send_exception_channels(e)
        if self.recipients.teams:
            try:
                self._send_teams_channels(self.recipients.teams, self._get_teams_sections(self.customers))
            except Exception as e:
                self._send_exception_channels(e)
        if self.recipients.emails:
            try:
                self._send_email_channels(
                    self.recipients.emails,
                    self.customers,
                    self._get_email_payload(self.customers),
                    template_id=self.recipients.config.templateId,
                )
            except Exception as e:
                self._send_exception_channels(e)


    def _send_exception_channels(self, e: Exception, customer: HarvestCustomer = None):
        if customer:
            err = f"Error sending report for {customer.data.name}: {str(e)}"
        else:
            err = str(e)

        if self.exception_config.teams:
            self._send_teams_channels(self.exception_config.teams, self._get_teams_exception_sections(err))
        if self.exception_config.emails:
            if self.exception_config.config:
                self._send_email_channels(
                    self.exception_config.emails,
                    err,
                    template_id=self.exception_config.config.templateId,
                )
            else:
                self._send_email_channels(
                    self.exception_config.emails,
                    [customer],
                    err,
                )
        if self.exception_config.slack:
            self._send_slack_channels(self.exception_config.slack, err)

    def _send_slack_channels(
        self, channels: List[str], msg: str
    ):
        for channel in channels:
            LOGGER.debug("Sending slack notification")
            response = NotificationManager.SLACK_CLIENT.post_slack_message(
                channel, msg
            )
            if response["status_code"] != 200:
                raise SlackSendError(channel, response["status_code"])

            LOGGER.debug(f"Sent slack notification")
            LOGGER.debug(f"Response: {response}")

    def _send_teams_channels(
        self, channels: List[str], msg: List[dict]
    ):
        for channel in channels:
            LOGGER.debug("Sending Teams notification")

            message = pymsteams.connectorcard(channel)
            message.payload = {
                "title": "DevOps Time Reports",
                "summary": "Accounting of currently used DevOps Now time",
                "sections": msg,
            }

            if not message.send():
                raise TeamsSendError(channel)

            LOGGER.debug(f"Sent Teams notification to {channel}")

    def _send_email_channels(
        self,
        channels: List[str],
        customers: List[HarvestCustomer],
        msg: str,
        template_id: str = "",
    ):

        LOGGER.debug("Sending email notifications")

        if template_id:
            email = SendGridSummaryEmail(template_id=template_id)
        else:
            email = SendGridSummaryEmail()

        response = email.send(channels, customers, msg)

        if response.status_code > 299:
            raise EmailSendError(channels, response.status_code)

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

    def _get_teams_exception_sections(self, err) -> List[dict]:
        sections = [{
            "activityTitle": f"ERROR",
            "text": err
        }]

        return sections

    def _get_email_payload(self, customers: List[HarvestCustomer]) -> List[str]:
        return "".join(
            [
                f"""Client:           {customer.data.name}
Used Hours:       {customer.time_used()}
Remaining Hours:  {customer.time_remaining()}
Percent:          {customer.percentage_hours_used()}%

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

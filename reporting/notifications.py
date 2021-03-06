import json
import logging
import os
import re
import sys
import traceback
from typing import List

import pymsteams
from google.cloud import pubsub_v1
from harvest.harvestdataclasses import Client

from harvestapi.customer import HarvestCustomer
from reporting.config import Recipients
from sendgridapi.emails import SendGridSummaryEmail

LOGGER = logging.getLogger(__name__)


class TeamsSendError(BaseException):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(f"Failed to send webhook to Teams channel {self.channel}.")


class EmailSendError(BaseException):
    def __init__(self, channels, message):
        self.channels = channels
        self.message = message
        super().__init__(
            f"Failed to send webhook to email addresses {self.channels}. {self.message}"
        )


def publish_to_pubsub(project_id: str, topic_id: str, payload: dict, attributes: dict):
    publisher = pubsub_v1.PublisherClient()
    try:
        LOGGER.debug(f"Sending Pub/Sub Message to {topic_id}...")
        topic_path = publisher.topic_path(project_id, topic_id)
        LOGGER.debug(f"Payload: {payload}")
        data = json.dumps(payload).encode("utf-8")
        future = publisher.publish(topic_path, data, **attributes)
        LOGGER.debug(f"Pub/Sub Message Published: {future.result()}")
    except:
        raise RuntimeError(f"Failed to send message to Pub/Sub: {project_id}, {topic_id}, {payload}, {attributes}")


class NotificationManager:
    def __init__(
        self,
        customers: List[HarvestCustomer],
        global_recipients: Recipients,
        exception_config: Recipients,
        sendgrid_api_key: str,
        from_email: str,
    ):
        self.sendgrid_api_key = sendgrid_api_key
        self.customers = customers
        self.recipients = global_recipients
        self.exception_config = exception_config
        self.from_email = from_email

    def send(self):
        for customer in self.customers:
            LOGGER.debug(f"Starting to process notifications for {customer.data.name}")

            self._send_customer_notifications(customer)

        self._send_global_notifications()

    # Post to channel/workspace
    def _send_customer_notifications(self, customer: HarvestCustomer):
        if customer.recipients:
            if len(customer.recipients.slack) > 0:
                self._send_slack_channels(
                    customer.recipients.slack, self._get_slack_payload([customer])
                )              

            if len(customer.recipients.teams) > 0:
                try:
                    self._send_teams_channels(
                        customer.recipients.teams, self._get_teams_sections([customer])
                    )
                except TeamsSendError as e:
                    self._send_exception_channels(e, customer)

            if len(customer.recipients.emails) > 0:
                try:
                    self._send_email_channels(
                        customer.recipients.emails, self._get_email_payload([customer]),
                    )
                except EmailSendError as e:
                    self._send_exception_channels(e, customer)

    def _send_global_notifications(self):
        try:
            if self.recipients.slack:
                self._send_slack_channels(
                    self.recipients.slack, self._get_slack_payload(self.customers)
                )
            if self.recipients.teams:
                self._send_teams_channels(
                    self.recipients.teams, self._get_teams_sections(self.customers)
                )
            if self.recipients.emails:
                self._send_email_channels(
                    self.recipients.emails,
                    self._get_email_payload(self.customers),
                    self.recipients.config.templateId,
                )
        except Exception as e:
                self._send_exception_channels(e)

    def _send_exception_channels(self, e: Exception, customer: HarvestCustomer = None):
        if customer:
            err = f"Error sending report for {customer.data.name}: {str(e)}"
        else:
            err = str(e)

        if self.exception_config.teams:
            self._send_teams_channels(
                self.exception_config.teams, 
                self._get_teams_exception_sections(err)
            )
        if self.exception_config.emails:
            self._send_email_channels(
                self.exception_config.emails,
                err,
                template_id=self.exception_config.config.templateId,
            )
        if self.exception_config.slack:
            self._send_slack_channels(self.exception_config.slack, err)

    def _send_slack_channels(self, channels: List[str], msg: dict):
        project_id = os.getenv("GCP_PROJECT", "dev-ops-now")
        for channel in channels:
            if "hooks.slack.com" in channel:
                attributes = {"incoming_webhook_url": channel}
            else:
                msg["channel"] = channel
                attributes = {"slack_api_method": "chat.postMessage"}
            publish_to_pubsub(project_id=project_id, topic_id="genericslackbot", payload=msg, attributes=attributes)

    def _send_teams_channels(self, channels: List[str], msg: List[dict]):
        for channel in channels:
            LOGGER.debug("Sending Teams notification")
            print(pymsteams.__dict__)
            message = pymsteams.connectorcard(channel)
            message.payload = {
                "title": "DevOps Time Reports",
                "summary": "Accounting of currently used DevOps Now time",
                "sections": msg,
            }

            try:
                if not message.send():
                    raise TeamsSendError(channel)
            except Exception as e:
                raise TeamsSendError(f"{channel}. Error: {e}")

            LOGGER.debug(f"Sent Teams notification to {channel}")

    def _send_email_channels(
        self, channels: List[str], msg: str, template_id: str = "",
    ):

        LOGGER.debug("Sending email notifications")

        email = SendGridSummaryEmail(
            api_key=self.sendgrid_api_key,
            from_email=self.from_email,
            template_id=template_id,
        )

        try:
            response = email.send(channels, msg)
        except Exception as e:
            raise EmailSendError(channels, e)

        if response.status_code > 299:
            raise EmailSendError(
                channels, "Status code: {}".format(response.status_code)
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
        sections = [{"activityTitle": f"ERROR", "text": err}]

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

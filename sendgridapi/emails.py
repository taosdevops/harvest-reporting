import logging
from datetime import date
from typing import List

import sendgrid
from sendgrid.helpers.mail import (Content, Email, Header, Mail, Subject,
                                   Substitution, TemplateId, To)

from harvestapi.customer import HarvestCustomer
from reporting.config import EnvironmentConfiguration

LOGGER = logging.getLogger(__name__)


class SendGridSummaryEmail:
    """Class used to create and send an email.
    """
    def __init__(
        self, api_key: str, from_email: str, template_id: str = "",
    ):
        self.sg_client = sendgrid.SendGridAPIClient(api_key=api_key)
        self.from_email = from_email
        # TODO: templateId is all piped in but it's not used anywhere.
        # Support for specifying a template ID should be verified and
        # added.
        self.template_id = template_id

    def construct_mail(self, emails: List[str], content: str) -> Mail:
        """Returns a Mail object that can be posted to the SendGrid API's email
        sending endpoint.

        Args:
            emails (List[str]): List of emails to add 'To' header
            content (str): String of content to add to the email body

            Mail: Completed Mail object capable of being sent

        Returns:
            sendgrid.helpers.mail.Mail()
        """
        current_date = date.today().strftime("%B %d, %Y")
        subject = Subject(f"DevOps Now hours usage as of {current_date}")
        content = Content("text/plain", content)
        to_emails = [To(email=email) for email in emails]
        from_email = Email(self.from_email)

        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            plain_text_content=content,
        )

        return message

    def send(self, emails: List[str], content: str) -> dict:
        """Performs the actual send of the email object in its current state.

        Args:
            emails (List[str]): A list of emails to which to send the email
            content (str): The plain text contents of the email

        Returns:
            dict: Returns the response object from the SendGrid API
        """
        if emails:
            mail = self.construct_mail(emails, content)

            LOGGER.info(f"Sending message to {emails} with content {content.encode('unicode_escape').decode()}")
            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        return dict()

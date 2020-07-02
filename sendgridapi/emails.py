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
        # message.template_id = TemplateId(self.templateId)

        return message

    def send(self, emails: List[str], content: str) -> dict:
        if emails:
            mail = self.construct_mail(emails, content)

            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        return dict()

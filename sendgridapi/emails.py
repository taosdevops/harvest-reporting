import logging
from datetime import date
from typing import List
import sendgrid
from sendgrid.helpers.mail import (
    Content,
    Email,
    Header,
    Mail,
    Subject,
    Substitution,
    TemplateId,
    To,
)

from reporting.config import EnvironmentConfiguration
from harvestapi.customer import HarvestCustomer


LOGGER = logging.getLogger(__name__)

ENV_CONFIG = EnvironmentConfiguration()
SENDGRID_CLIENT = sendgrid.SendGridAPIClient(api_key=ENV_CONFIG.sendgrid_api_key)


class SendGridSummaryEmail:
    def __init__(
        self,
        sg_client: sendgrid.SendGridAPIClient = SENDGRID_CLIENT,
        from_email: str = ENV_CONFIG.origin_email_address,
        template_id: str = "",
    ):
        self.sg_client = sg_client
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

    def send(
        self, emails: List[str], customers: List[HarvestCustomer], content: str
    ) -> dict:
        if emails:
            mail = self.construct_mail(emails, content)

            LOGGER.debug(mail)

            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        return dict()

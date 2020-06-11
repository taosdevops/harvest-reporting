import logging
from datetime import date

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


logger = logging.getLogger(__name__)

ENV_CONFIG = EnvironmentConfiguration()
SENDGRID_CLIENT = sendgrid.SendGridAPIClient(api_key=ENV_CONFIG.sendgrid_api_key)


class SendGridSummaryEmail:
    def __init__(
        self,
        sg_client: sendgrid.SendGridAPIClient = SENDGRID_CLIENT,
        from_email: str = ENV_CONFIG.origin_email_address,
    ):
        self.sg_client = sg_client
        self.from_email = from_email

    def construct_mail(self, emails: list, client: dict, content) -> Mail:
        current_date = date.today().strftime("%B %d, %Y")
        subject = Subject(
            f"{client['name']} usage of DevOps Now hours as of {current_date} "
        )

        content = Content("text/plain", content)

        return Mail(Email(self.from_email), list(emails), subject, content)

    def send(self, emails: list, client, config) -> dict:
        if emails:
            mail = self.construct_mail(emails, client, config)

            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        logger.warning("No Email addresses were found for %s", client["name"])

        return dict()


class SendGridTemplateEmail(SendGridSummaryEmail):
    """
    Provides interface to use dynamic templates from SendGrid
    """

    def construct_mail(self, emails: list, client: dict, content) -> Mail:
        """
        Constructs email from content.

        Replaces variables in the SendGrid email template such as
        My replacement goes here: {{value}}.
        Replacements happen everywhere {{replacement2}}
        ---
        client = {
            'template_id': '563533b6-b2df-4f29-8c54-06fc802bb115',
            'body': {
                'key': 'value',
                'replacement2': 'My replacement Value'
            },
            'header': {
                'value1': 'Replacement'
            }
        }
        """

        message = Mail()

        message.template_id = TemplateId(client["template_id"])

        # TODO We shouldn't need this check
        # Fix this hack

        if isinstance(emails, list):
            message.to = [To(email) for email in emails]
        else:
            message.to = To(emails)

        # TODO did i configure the pass through generations?
        # I don't thin i have any configs that are being passed

        if "body" in client.keys():
            message.substitution = [
                Substitution(key=key, value=value)
                for key, value in client["body"].items()
            ]

        if "header" in client.keys():
            message.header = [
                Header(key, value) for key, value in client["header"].items()
            ]

        return message

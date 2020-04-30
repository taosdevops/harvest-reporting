import logging
from datetime import date

import sendgrid
from sendgrid.helpers.mail import (Content, Email, Header, Mail, Subject,
                                   Substitution, TemplateId, To)

from hreporting import config

logging.getLogger("harvest_reports")

SENDGRID_CLIENT = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)


class SendGridSummaryEmail:
    def __init__(
        self, sg_client=SENDGRID_CLIENT, from_email: str = config.ORIGIN_EMAIL_ADDRESS
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

        logging.warning("No Email addresses were found for %s", client["name"])

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
        message.to = [To(email) for email in emails]

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

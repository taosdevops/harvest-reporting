import logging
from datetime import date

import sendgrid
from sendgrid.helpers.mail import (Content, Email, Header, Mail, Section,
                                   Subject, TemplateId, To)

from hreporting import config

logging.getLogger("harvest_reports")

SENDGRID_CLIENT = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)


class SendGridSummaryEmail:
    def __init__(
        self, sg_client=SENDGRID_CLIENT, from_email: str = config.ORIGIN_EMAIL_ADDRESS
    ):
        self.sg_client = sg_client
        self.from_email = from_email

    def construct_mail(self, emails, client_name: str, body) -> Mail:
        current_date = date.today().strftime("%B %d, %Y")
        subject = Subject(
            f"{client_name} usage of DevOps Now hours as of {current_date} "
        )

        content = Content("text/plain", body)

        return Mail(Email(self.from_email), list(emails), subject, content)

    def email_send(self, emails, client_name: str, body) -> dict:
        if emails:
            mail = self.construct_mail(emails, client_name, body)

            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        logging.warning("No Email addresses were found for %s", client_name)

        return dict()


class SendGridTemplateEmail(SendGridSummaryEmail):
    """
    Provides interface to use dynamic templates from SendGrid
    """

    def construct_mail(self, emails, client_name: str, template_variables) -> Mail:
        """
        Constructs email from template_variables.

        Replaces variables in the SendGrid email template such as
        My replacement goes here: {{value}}.
        Replacements happen everywhere {{replacement2}}
        ---
        template_variables = {
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

        message.template_id = TemplateId(template_variables.template_id)
        message.to = [To(email) for email in emails]

        if "body" in template_variables.keys():
            message.sections = [
                Section(key, value) for key, value in template_variables["body"]
            ]

        if "header" in template_variables.keys():
            message.header = [
                Header(key, value) for key, value in template_variables["header"]
            ]

        return message

import logging
from datetime import date

from sendgrid.helpers.mail import *

logging.getLogger("harvest_reports")


class SendGridSummaryEmail:
    def __init__(
        self,
        client_name: str,
        emails: list,
        left: float,
        percent: float,
        sg_client,
        used: float,
        from_email: str,
    ):

        self.client_name = client_name
        self.emails = map(To, emails)
        self.left = left
        self.percent = percent
        self.sg_client = sg_client
        self.used = used
        self.from_email = from_email

    def email_body(self) -> str:
        hour_report_template = """
        Client:           {name}
        Used Hours:       {used}
        Remaining Hours:  {left}
        Percent:          {percent}
        """
        return str.format(
            hour_report_template,
            name=self.client_name,
            used=self.used,
            left=self.left,
            percent="%d%%" % (self.percent),
        )

    def construct_mail(self) -> Mail:
        current_date = date.today().strftime("%B %d, %Y")
        subject = Subject(
            f"{self.client_name} usage of DevOps Now hours as of {current_date} "
        )

        content = Content("text/plain", self.email_body())

        return Mail(Email(self.from_email), list(self.emails), subject, content)

    def email_send(self) -> dict:
        if self.emails:
            mail = self.construct_mail()

            response = self.sg_client.client.mail.send.post(request_body=mail.get())

            return response

        logging.info(
            "No Email addresses were found for {client_name}".format(
                client_name=self.client_name
            )
        )
        return dict()

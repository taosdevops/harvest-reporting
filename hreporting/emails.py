from datetime import date

from sendgrid.helpers.mail import *


class SendGridSummaryEmail:
    def __init__(
        self,
        client_name: str,
        emails: list,
        left: float,
        percent: float,
        sg_client,
        used: float,
    ):

        self.client_name = client_name
        self.emails = map(To, emails)
        self.left = left
        self.percent = percent
        self.sg_client = sg_client
        self.used = used

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
        from_email = Email("DevOpsNow@nottaos.com")

        content = Content("text/plain", self.email_body())

        return Mail(from_email, list(self.emails), subject, content)

    def email_send(self,) -> dict:
        mail = self.construct_mail()

        response = self.sg_client.client.mail.send.post(request_body=mail.get())

        return response

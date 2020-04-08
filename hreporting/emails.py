from sendgrid.helpers.mail import *
from datetime import date


def email_body(used, client_name, percent, left) -> str:
    hour_report_template = """
    Client:           {name}
    Used Hours:       {used}
    Remaining Hours:  {left}
    Percent:          {percent}
    """
    return str.format(
        hour_report_template,
        name=client_name,
        used=used,
        left=left,
        percent="%d%%" % (percent),
    )


def email_send(
    emails: list, used: float, client_name: str, percent: float, left: float, sg_client
) -> dict:

    current_date = date.today.strftime("%B %d, %Y")
    subject = Subject(f"{client_name} usage of DevOps Now hours as of {current_date} ")
    from_email = Email("DevOpsNow@taos.com")

    content = Content("text/plain", email_body(used, client_name, percent, left))

    mail = Mail(from_email, emails, subject, content)

    response = sg_client.client.mail.send.post(request_body=mail.get())

    return response

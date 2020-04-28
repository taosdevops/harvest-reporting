import re
from unittest import TestCase
from unittest.mock import MagicMock

import sendgrid
from vcr_unittest import VCRTestCase

from hreporting.emails import SendGridSummaryEmail


class TestEmail(VCRTestCase):
    def setUp(self):

        self.client_name = "My Client Under Test"
        self.emails = ["emailToCheck@test.com", "GlobalEmailToTest@example.com"]
        self.left = 60
        self.percet = 28.4
        self.sg_client = MagicMock()
        self.used = 100

        self.test_body = """
        This is a test body
        """

        self.sg_email = SendGridSummaryEmail()

        # self.client_name,
        # self.emails,
        # self.left,
        # self.percet,
        # self.sg_client,
        # self.used,
        # "BadEmail@exmaple.com",
        # )

    def test_to_emails(self):
        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = self.emails

        email_under_test = self.sg_email.construct_mail(
            emails=self.emails, body=self.test_body, client_name=self.client_name
        )

        for personalization in email_under_test.personalizations:

            for pattern in patterns:
                expectation = re.search(pattern, str(personalization.tos))
                self.assertTrue(
                    expectation, f"Looking for {pattern} in {personalization}"
                )

    def test_email_send_returns_if_missing_emails(self):
        email_under_test = self.sg_email.email_send(
            emails=[], client_name=self.client_name, body=self.test_body
        )
        self.assertEqual({}, email_under_test)

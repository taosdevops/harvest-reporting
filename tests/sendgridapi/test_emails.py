import re
import os
from unittest.mock import MagicMock

from vcr_unittest import VCRTestCase

from sendgridapi.emails import SendGridSummaryEmail


class TestSummaryEmail(VCRTestCase):
    def setUp(self):

        self.customers = {
            "hours_used": 60,
            "name": "DSC",
            "percent": 50,
            "hours_left": 30,
        }

        self.client_name = "My Client Under Test"
        self.emails = ["emailToCheck@test.com", "GlobalEmailToTest@example.com"]
        self.left = 60
        self.percet = 28.4
        self.sg_client = MagicMock()
        self.used = 100

        self.test_body = """
        This is a test body
        """

        self.sg_email = SendGridSummaryEmail(
            api_key="testymctestface", from_email="test@example.com"
        )

    def test_to_emails(self):

        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = self.emails

        email_under_test = self.sg_email.construct_mail(
            self.emails, content=self.test_body
        )

        for personalization in email_under_test.personalizations:

            for pattern in patterns:
                expectation = re.search(pattern, str(personalization.tos))
                self.assertTrue(
                    expectation, f"Looking for {pattern} in {personalization}"
                )

    def test_email_send_returns_if_missing_emails(self):
        email_under_test = self.sg_email.send(emails=[], content=self.test_body)
        self.assertEqual({}, email_under_test)

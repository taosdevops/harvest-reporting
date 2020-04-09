import re
from unittest import TestCase
from unittest.mock import MagicMock

import vcr
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

        self.sg_email = SendGridSummaryEmail(
            self.client_name,
            self.emails,
            self.left,
            self.percet,
            self.sg_client,
            self.used,
        )

    def test_to_emails(self):
        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = self.emails

        email_under_test = self.sg_email.construct_mail()

        for personalization in email_under_test.personalizations:

            for pattern in patterns:
                expectation = re.search(pattern, str(personalization.tos))
                self.assertTrue(
                    expectation, f"Looking for {pattern} in {personalization}"
                )

    def test_email_body(self):
        patterns = [
            "Client",
            self.client_name,
            "Used Hours",
            str(self.used),
            "Remaining",
            str(self.left),
        ]

        email_under_test = self.sg_email.construct_mail()

        for pattern in patterns:
            for element in email_under_test.contents:

                expectation = re.search(pattern, element.content)
                self.assertTrue(
                    expectation,
                    f"Looking for body pattern of {pattern} in {element.content}",
                )

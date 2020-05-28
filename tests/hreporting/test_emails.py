import re
from unittest import TestCase
from unittest.mock import MagicMock

import sendgrid
from vcr_unittest import VCRTestCase

from hreporting.emails import SendGridSummaryEmail, SendGridTemplateEmail


class TestSummaryEmail(VCRTestCase):
    def setUp(self):
        self.client = {"hours_used": 60, "name": "DSC", "percent": 50, "hours_left": 30}

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

    def test_to_emails(self):

        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = self.emails

        email_under_test = self.sg_email.construct_mail(
            self.emails, self.client, self.test_body
        )

        for personalization in email_under_test.personalizations:

            for pattern in patterns:
                expectation = re.search(pattern, str(personalization.tos))
                self.assertTrue(
                    expectation, f"Looking for {pattern} in {personalization}"
                )

    def test_email_send_returns_if_missing_emails(self):
        email_under_test = self.sg_email.send(
            emails=[], client=self.client, config=self.test_body
        )
        self.assertEqual({}, email_under_test)


class TestTemplateEmail(VCRTestCase):
    def setUp(self):
        self.client = {
            "hours_used": 60,
            "name": "DSC",
            "percent": 50,
            "hours_left": 30,
            "template_id": "bogus sendgrid id",
            "body": {"first": "check", "second": "mate"},
            "header": {"into": "goal", "for": "win"},
        }

        self.client_name = "My Template Email Under Test"
        self.emails = ["emailToCheck@test.com", "GlobalEmailToTest@example.com"]
        self.left = 60
        self.percet = 28.4
        self.sg_client = MagicMock()
        self.used = 100

        self.sg_email = SendGridTemplateEmail()
        self.email_under_test = self.sg_email.construct_mail(
            emails=self.emails, client=self.client, content={}
        )

    def test_to_emails(self):
        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = self.emails

        for personalization in self.email_under_test.personalizations:

            for pattern in patterns:
                expectation = re.search(pattern, str(personalization.tos))
                self.assertTrue(
                    expectation, f"Looking for {pattern} in {personalization}"
                )

    def test_email_send_returns_if_missing_emails(self):
        email_under_test = self.sg_email.send(emails=[], client=self.client, config={})
        self.assertEqual({}, email_under_test)

    def test_substution_working(self):
        expected_subs = self.client["body"]

        for subs_under_test in self.email_under_test.personalizations:

            for target, value in expected_subs.items():
                expectation = re.search(value, str(subs_under_test.substitutions))
                self.assertTrue(
                    expectation,
                    f"Looking for {value} to have replaced {target} in {subs_under_test.substitutions}",
                )

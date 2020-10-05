import os
import re
import unittest
import unittest.mock

from vcr_unittest import VCRTestCase

import sendgridapi.emails


class TestSummaryEmail(VCRTestCase):
    @unittest.mock.patch('sendgridapi.emails.sendgrid.SendGridAPIClient')
    def setUp(self, mock_sg_client):

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
        self.used = 100
        self.test_body = "This is a test body"
        self.sg_email = sendgridapi.emails.SendGridSummaryEmail(
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

    def test_construct_mail(self):
        msg = self.sg_email.construct_mail(self.emails, self.test_body)

        for email in self.emails:
            for personalization in msg.personalizations:
                self.assertTrue(re.search(email, str(personalization.tos)))

        for content in msg._contents:
            assert self.test_body == content._content

    def test_send(self):
        with unittest.mock.patch.object(sendgridapi.emails.SendGridSummaryEmail, "construct_mail") as mocked_construct_mail:
            self.sg_email.send(self.emails, self.test_body)

            mocked_construct_mail.assert_called_once()
            mocked_construct_mail.assert_called_with(self.emails, self.test_body)
            self.sg_email.sg_client.client.mail.send.post.assert_called_with(request_body=mocked_construct_mail().get())

            self.sg_email.sg_client.client.mail.send.post.assert_called_once()

            assert self.sg_email.send([], self.test_body) == {}




    def test_email_send_returns_if_missing_emails(self):
        email_under_test = self.sg_email.send(emails=[], content=self.test_body)
        self.assertEqual({}, email_under_test)

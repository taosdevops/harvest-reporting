import re
from unittest import TestCase


from hreporting.emails import email_body


class TestGetEmailPayload(TestCase):
    def test_returns_email_payload(self):
        channel_post_under_test = email_body(60, "SVB", 50, 30)

        # Excluding @ and .com for regex issues. Checking for the prefix is just as effective
        patterns = ["Used Hours", "Percent", "Remaining"]

        for pattern in patterns:
            expectation = re.search(pattern, str(channel_post_under_test))
            self.assertTrue(expectation)

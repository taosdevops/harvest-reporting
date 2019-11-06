from unittest import TestCase, skip
from hreporting.utils import get_color_code_for_utilization, get_payload, channel_post
from taosdevopsutils.slack import Slack
import re

class TestUtilsColorCode(TestCase):
    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(get_color_code_for_utilization(101), "#ff0000")


class TestGetPayload(TestCase):
    def test_returns_slack_payload(self):
        payload_under_test = get_payload(60, "DSC", 50, 30,)
        pattern = "attachments"
        expectation = re.search(pattern, str(payload_under_test)) 
        self.assertTrue(expectation)

    def test_returns_teams_payload(self):
            payload_under_test = get_payload(60, "SVB", 50, 30, _format="teams")
            pattern = "MessageCard"
            expectation = re.search(pattern, str(payload_under_test)) 
            self.assertTrue(expectation)
    
    def test_returns_raise_exeption(self):
        with self.assertRaises(Exception): 
            get_payload(60, "SVB", 50, 30, _format="expected failure")
    
    
    def test_returns_channel_post(self):
        channel_post_under_test = channel_post("https://outlook.office.com/", 60, "SVB", 50, 30,)
        pattern = "MessageCard"
        expectation = re.search(pattern, str(channel_post_under_test)) 
        self.assertTrue(expectation)



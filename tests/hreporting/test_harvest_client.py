from unittest import TestCase
from hreporting.harvest_client import HarvestClient
import vcr
from vcr_unittest import VCRTestCase

account = "1121001"
btoken = "SomeBearerToken"


class TestHarvestClient(VCRTestCase):
    def test_list_clients_calls_uri(self):
        account_list = HarvestClient(btoken, account).list_clients()
        # account_list = HarvestClient(bearer_token, account).list_clients()

        self.assertEqual(
            self.cassette.requests[0].uri, "https://api.harvestapp.com/v2/clients"
        )
        self.assertEqual(
            self.cassette.requests[0].headers["Harvest-Account-ID"], "1121001"
        )
        self.assertEqual(len(account_list), 9)

    def test_get_client_time_used(self):
        time_used = HarvestClient(btoken, account).get_client_time_used(8544728)
        self.assertEqual(
            self.cassette.requests[0].uri,
            "https://api.harvestapp.com/v2/time_entries?client_id=8544728",
        )
        self.assertEqual(time_used, 16.03)


from unittest import TestCase

import vcr
from vcr_unittest import VCRTestCase

from harvestapi.customer import HarvestCustomer

account = "1121001"
btoken = "SomeBearerToken"


class TestHarvestCustomer:
    def test_get_client_time_used(self):
        time_used = HarvestCustomer().get_client_time_used(
            8544728, month="09", year="2019"
        )
        self.assertEqual(
            self.cassette.requests[0].uri,
            "https://api.harvestapp.com/v2/time_entries?client_id=8544728",
        )
        self.assertEqual(time_used, 16.03)

    def test_get_client_hooks_gets_named_hook(self):
        hook_url = "http://123.com"
        config = {"clients": [{"name": "dsc", "hooks": [hook_url]}]}
        client = HarvestAPIClient(btoken, account, config)
        hooks = client.get_client_hooks("dsc")
        self.assertEqual(hooks, [hook_url])

    def test_get_client_hooks_compiles_global_hooks(self):
        hook_url = "http://123.com"
        global_hook = "http://456.com"
        config = {
            "clients": [{"name": "dsc", "hooks": [hook_url]}],
            "globalHooks": [global_hook],
        }
        client = HarvestAPIClient(btoken, account, config)
        hooks = client.get_client_hooks("dsc")
        self.assertEqual(hooks, [hook_url, global_hook])

    def test_get_time_alloted(self):
        config = {"clients": [{"name": "dsc", "hours": 60}]}
        client = HarvestAPIClient(btoken, account, config)
        allotment = client.get_client_time_allotment("dsc")
        self.assertEqual(allotment, 60)

    def test_get_time_alloted_defaults_to_80(self):
        config = {"clients": [{"name": "dsc"}]}
        client = HarvestAPIClient(btoken, account, config)
        allotment = client.get_client_time_allotment("dsc")
        self.assertEqual(allotment, 80)

import os
import unittest
import unittest.mock

import vcr
from harvest.harvest import Harvest, PersonalAccessToken
from harvest.harvestdataclasses import Client, TimeEntries, TimeEntry
from vcr_unittest import VCRTestCase
import gzip
from dacite import from_dict
import yaml

import harvestapi.customer as customer
import reporting.config

HARVEST_ENDPOINT = "https://api.harvestapp.com/api/v2"

VCR = vcr.VCR(
    cassette_library_dir='tests/harvestapi/cassettes',
    filter_headers=["authorization"],
)

class TestHarvestCustomer(VCRTestCase):
    def setUp(self):
        os.environ["HARVEST_ACCOUNT_ID"] = "dummy_account"
        os.environ["BEARER_TOKEN"] = "dummy_token"

        self.customer = customer.HarvestCustomer(
                client=Harvest(
                    HARVEST_ENDPOINT,
                    PersonalAccessToken(
                        reporting.config.HARVEST_ACCOUNT_ID, reporting.config.BEARER_TOKEN
                    ),
                ),
                config=reporting.config.Customer(name="Testy McTest", hours=80, recipients=reporting.config.Recipients()),
                recipients=reporting.config.Recipients(),
                customer=Client(id="9172713", address="Whatever"),
            )

    @VCR.use_cassette
    def test_time_used(self):
        assert self.customer.time_used(month="06", year="2020") == 46.6

    @VCR.use_cassette
    def test_get_time_entries(self):
        entries = self.customer._get_time_entries()

        assert type(entries) == list

        for entry in entries:
            assert type(entry) == TimeEntry

    @VCR.use_cassette
    def test_time_remaining(self):
        assert self.customer.time_remaining(month="06", year="2020") == 33.4

    @VCR.use_cassette
    def test_percentage_hours_used(self):
        assert self.customer.percentage_hours_used(month="06", year="2020") == 58.2

    def test_get_recipients_from_config(self):
        # Client object to use to search against test configs
        test_client = Client(name="Testy McTest", address="Test")

        cust_recipients = reporting.config.Recipients(emails=["test@example.com"], slack=["https://test.slack.com/webhook"])
        cust_with_recipients = reporting.config.Customer(name="Testy McTest", hours=80, recipients=cust_recipients)
        global_recipients = reporting.config.Recipients(emails=["global@example.com"], slack=["https://globaltest.slack.com/webhook"])

        config = reporting.config.ReporterConfig(
            customers=[cust_with_recipients],
            recipients=global_recipients,
            exceptions=reporting.config.Recipients()
        )

        assert customer.get_recipients_from_config(test_client, config) == cust_recipients

        # No recipients for customer in recipients config
        cust_without_recipients = reporting.config.Customer(name="Testy McTest", hours=80)

        config = reporting.config.ReporterConfig(
            customers=[cust_without_recipients],
            recipients=global_recipients,
            exceptions=reporting.config.Recipients()
        )

        assert customer.get_recipients_from_config(test_client, config) == reporting.config.Recipients()

        # Customer not matching any in recipients config
        cust_not_matching = reporting.config.Customer(name="McTester Test", hours=80, recipients=cust_recipients)

        config = reporting.config.ReporterConfig(
            customers=[cust_not_matching],
            recipients=global_recipients,
            exceptions=reporting.config.Recipients()
        )

        assert customer.get_recipients_from_config(test_client, config) == reporting.config.Recipients()


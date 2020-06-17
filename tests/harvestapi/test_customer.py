import os
import unittest
import unittest.mock

import vcr
from harvest.harvest import Harvest, PersonalAccessToken
from harvest.harvestdataclasses import Client, TimeEntries, TimeEntry
from vcr_unittest import VCRTestCase
import gzip

import harvestapi.customer as customer
from reporting.config import (Customer, EnvironmentConfiguration, Recipients,
                              ReporterConfig)

HARVEST_ENDPOINT = "https://api.harvestapp.com/api/v2"

VCR = vcr.VCR(
    cassette_library_dir='tests/harvestapi/cassettes',
    filter_headers=["authorization"],
)


class TestHarvestCustomer(VCRTestCase):
    def setUp(self):
        os.environ["HARVEST_ACCOUNT_ID"] = "dummy_account"
        os.environ["BEARER_TOKEN"] = "dummy_token"

        ENV_CONFIG = EnvironmentConfiguration()

        self.customer = customer.HarvestCustomer(
                client=Harvest(
                    HARVEST_ENDPOINT,
                    PersonalAccessToken(
                        ENV_CONFIG.harvest_account, ENV_CONFIG.bearer_token
                    ),
                ),
                config=Customer(name="Testy McTest", hours=80, recipients=Recipients()),
                recipients=Recipients(),
                customer=Client(id="9172713", address="Whatever"),
            )

    @VCR.use_cassette
    def test_time_used(self):
        print(self.customer.time_used())
        assert self.customer.time_used() == 46.629999999999995

    @VCR.use_cassette
    def test_get_time_entries(self):
        entries = self.customer._get_time_entries()

        assert type(entries) == list

        for entry in entries:
            assert type(entry) == TimeEntry

    @VCR.use_cassette
    def test_time_remaining(self):
        print(self.customer.time_remaining(month="06", year="2020"))
        assert self.customer.time_remaining(month="06", year="2020") == 33.370000000000005

    @VCR.use_cassette
    def test_percentage_hours_used(self):
        assert self.customer.percentage_hours_used() == 59


    def test_get_recipients_from_config(self):
        cust_recipients = Recipients(emails=["test@example.com"], slack=["https://test.slack.com/webhook"])
        cust = Customer(name="Testy McTest", hours=80, recipients=cust_recipients)
        global_recipients = Recipients(emails=["global@example.com"], slack=["https://globaltest.slack.com/webhook"])

        config = ReporterConfig(
            customers=[cust],
            recipients=global_recipients,
            exceptions=Recipients()
        )

        assert customer.get_recipients_from_config(cust, config) == cust_recipients


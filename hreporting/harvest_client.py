import requests
import datetime
import re


def _get_current_month():  # Maybe move ??
    dm = datetime.datetime.today().month
    return f"{dm:02}"


class HarvestClient:
    base_url = "https://api.harvestapp.com/v2/"
    client_endpoint = "clients"
    client_time_endpoint = "time_entries?client_id="

    def _get_client_config(self, client_name: str):
        try:
            return [
                client_entry
                for client_entry in self.config["clients"]
                if client_entry["name"] == client_name
            ][0]
        except IndexError:
            return {}

    def __init__(self, bearer_token: str, account_id: str, config=None):
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Harvest-Account-ID": account_id,
        }
        self.config = config

    def list_clients(self) -> list:
        """ Returns array of harvest Clients"""
        uri = self.base_url + self.client_endpoint
        response = requests.get(uri, headers=self.headers)
        json_response = response.json()
        return json_response["clients"]

    def get_client_time(self, client_id: str):
        """ Returns Time entries for Harvest Clients """
        uri = self.base_url + self.client_time_endpoint + str(client_id)
        response = requests.get(uri, headers=self.headers)
        json_response = response.json()
        return json_response["time_entries"]

    def get_client_time_used(self, client_id: str, month=_get_current_month()):
        regex = re.compile("([0-9]{4})-([0-9]{2})-([0-9]{2})")
        return sum(
            [
                item["hours"]
                for item in self.get_client_time(client_id)
                if regex.search(item["spent_date"]).group(2) == month
            ]
        )

    def get_client_time_allotment(self, client_name):
        client_config = self._get_client_config(client_name)
        return client_config.get("hours", self.config.get("default_hours", 80))

    def get_client_hooks(self, client_name):
        client_config = self._get_client_config(client_name)
        return [*client_config.get("hooks", []), *self.config.get("globalHooks", [])]
        # client_config.get('hours',self.config.get('default_hours'),80)

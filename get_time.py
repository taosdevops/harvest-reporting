#!/usr/bin/env python3
import re
import os
import json
import fileinput
import urllib.request
from datetime import date
from datetime import time

url = "https://api.harvestapp.com/v2/time_entries?client_id=8102048"
headers = {
    "User-Agent": "Python Harvest API Sample",
    "Authorization": "Bearer 1958933.pt.AQdIixLiVPwHPcd0qwPxL0qYh3bKGanbkPBm3yraWoDHA9BNReJODWQfeWnAQZDC9KBmEws1gwDOpVdJB4LIrw",
    "Harvest-Account-ID": "1121001"
}

request = urllib.request.Request(url=url, headers=headers)
response = urllib.request.urlopen(request, timeout=5)
responseBody = response.read().decode("utf-8")
jsonResponse = json.loads(responseBody)
timeEntries = jsonResponse["time_entries"]

regex = re.compile('([0-9]{4})-([0-9]{2})-([0-9]{2})')
today = date.today().strftime('%Y-%m-%d')
currentMonth = regex.search(today).group(2)
#print(currentMonth)

for items in timeEntries:
    m = regex.search(items["spent_date"]).group(2)
    if str(m) == str(currentMonth):
      #print(m)
      print(json.dumps(items["hours"], sort_keys=True, indent=4))
      #print(json.dumps(items["spent_date"], sort_keys=True, indent=4))

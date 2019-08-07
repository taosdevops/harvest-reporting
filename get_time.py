#!/usr/bin/env python3
import re
import os
import json
import math
import fileinput
import urllib.request
from decimal import *
from datetime import date
from datetime import time

from time import gmtime, strftime

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

hours_used = 0.0


for items in timeEntries:
    m = regex.search(items["spent_date"]).group(2)
    if str(m) == str(currentMonth):
      #print(m)
        total = items["hours"]
        hours_used += total
      #total = (items["hours"])
      #total = sum(add)
      # print(total)
      #print(json.dumps(items["spent_date"], sort_keys=True, indent=4))
      
      #total = sum(add)
      #print (total)


result = strftime("%H:%M:%S", gmtime(hours_used * 60))

print(result, "Hours Used")



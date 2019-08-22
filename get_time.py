#!/usr/bin/env python3
import re
import os
import json
import math
import fileinput
import urllib.request
from datetime import date
from datetime import time

# Build headers
headers = {
    'Authorization': 'Bearer 1958933.pt.AQdIixLiVPwHPcd0qwPxL0qYh3bKGanbkPBm3yraWoDHA9BNReJODWQfeWnAQZDC9KBmEws1gwDOpVdJB4LIrw',
    'Harvest-Account-ID': '1121001'
}

# Define uri's
api = 'https://api.harvestapp.com/v2/'
clientUri = 'clients'
timeEntriesUri = 'time_entries?client_id=' 

# Build url to get clients
getClient = api+clientUri

# Get client name and id
clientRequest = urllib.request.Request(url=getClient, headers=headers)
clientResponse = urllib.request.urlopen(clientRequest, timeout=5)
responseBody = clientResponse.read().decode('utf-8')
jsonResponse = json.loads(responseBody)
clientList = jsonResponse['clients']

for client in clientList:
    clientId = client['id']
    clientName = client['name']

    # Build url to get time
    getTime = str(api) + str(timeEntriesUri) + str(clientId)

    # Get client time entries
    timeRequest = urllib.request.Request(url=getTime, headers=headers)
    timeResponse = urllib.request.urlopen(timeRequest, timeout=5)
    responseBody = timeResponse.read().decode('utf-8')
    jsonResponse = json.loads(responseBody)
    timeEntries = jsonResponse['time_entries']

    # Define regex pattern based on todays date, match month
    regex = re.compile('([0-9]{4})-([0-9]{2})-([0-9]{2})')
    today = date.today().strftime('%Y-%m-%d')
    currentMonth = regex.search(today).group(2)
    
    # Define hours
    hours_used = 0.00
    total_hours = 80.00
   
    # Get time entries based on regex month match
    for item in timeEntries:
        m = regex.search(item['spent_date']).group(2)
        if str(m) == str(currentMonth):
           #print(m)
           total = item['hours']
           hours_used += total
    hours_left = total_hours - hours_used
    
    # Define decimal place to truncate
    def truncate(n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    # Only keep 2 decimal places
    used = truncate(hours_used, 2)
    left = truncate(hours_left, 2)

    Hour_Report_Template = '''
    Client:           {clientName}
    Used Hours:       {used}
    Remaining Hours:  {left}
    '''

    print (str.format(
    Hour_Report_Template,
    clientName = clientName,
    used = used,
    left = left,
    ))

#!/usr/bin/python
# -*- coding: utf-8 -*-
# <bitbar.title>Alpha Vantage Stock Ticker</bitbar.title>
# <bitbar.version>0.1</bitbar.version>
# <bitbar.author>Ben Rogers</bitbar.author>
# <bitbar.author.github>benson8</bitbar.author.github>
# <bitbar.desc>Provides a rotating stock ticker in your menu bar</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>
import urllib2
import json
import time
from datetime import date, timedelta
import decimal
import os
from pprint import pprint

# support for touching a file
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

today = date.today()
yesterday = date.today() - timedelta(1)
todayString = str(today)
yesterdayString = str(yesterday)

### REPLACE THESE VALUES
stocks="STOCK_SYMBOL"
apiKey="APIKEY"
###

# Currently only supports one stock
query = ""
for i in stocks:
    query = i + "," + query

# daily url gives us open price
dailyUrl = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=compact&apikey={}".format(stocks, apiKey)
# batch url gives us current price
batchUrl = "https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols={}&apikey={}".format(stocks, apiKey)

lastResponse = open("/tmp/lastprice.json", "w")
readFromCache = False
try:
   u = urllib2.urlopen(batchUrl)
except urllib2.HTTPError as err:
   if err.code == 503:
      readFromCache = True
   else:
      raise

apiDown = False
if readFromCache == False: 
   query = u.read()
   lastResponse.write(query)
   lastResponse.close()
else:
   responseCache = open("/tmp/lastprice.json", "r")
   query = responseCache.read()
   apiDown = True

batchJson = json.loads(query)

currentPrice = round(float(batchJson['Stock Quotes'][0]['2. price']), 2)

if not os.path.isfile('/tmp/stock.txt'):
   touch('/tmp/stock.txt')

foundYesterDaysPrice = False
stockFile = open("/tmp/stock.txt", "r")
for line in stockFile:
   if yesterdayString in line:
      price = line.split(':')
      yesterdayPrice = round(float(price[1]), 2)
      foundYesterdaysPrice = True

stockFile.close()

if foundYesterDaysPrice == False:
   y = urllib2.urlopen(dailyUrl)
   query = y.read()
   dailyJson = json.loads(query)
   closePrice = round(float(dailyJson['Time Series (Daily)'][yesterdayString]['4. close']), 2)
   with open('/tmp/stock.txt', 'a') as stock_txt:
      stock_txt.write("{}: {:,.2f}\n".format(yesterdayString, closePrice))

stock_txt.close()

foundOpenPrice = False
# make only one call to dailyUrl every day, since it is slow
stockFile = open("/tmp/stock.txt", "r")
for line in stockFile:
   if todayString in line:
      price = line.split(':')
      openPrice = round(float(price[1]), 2)
      foundOpenPrice = True

if foundOpenPrice == False:
   y = urllib2.urlopen(dailyUrl)
   query = y.read()
   dailyJson = json.loads(query)
   openPrice = round(float(dailyJson['Time Series (Daily)'][todayString]['1. open']), 2)
   with open('/tmp/stock.txt', 'a') as stock_txt:
      stock_txt.write("{}: {:,.2f}\n".format(todayString, openPrice))

#priceChange = currentPrice - openPrice
priceChange = currentPrice - yesterdayPrice

if apiDown == False: 
   color = "red" if priceChange < 0 else "green"
else:
   color = "gray"

print("{} ${:,.2f} {:+.2f} | color={}".format(
     stocks, currentPrice, priceChange, color
))


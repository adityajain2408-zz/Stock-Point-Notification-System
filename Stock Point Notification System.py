# -*- coding: utf-8 -*-

import os
import pandas as pd 
import datetime, time

class YahooDailyReader():
    
    def __init__(self, symbol=None, start=None, end=None):
        self.symbol = symbol
        
        ## initialize start/end dates if not provided
        if end is None:
            end = datetime.datetime.today()
        if start is None:
            start = datetime.datetime(2010,1,1)
        
        self.start = start
        self.end = end
        
        # convert dates to unix time strings
        unix_start = int(time.mktime(self.start.timetuple()))
        day_end = self.end.replace(hour=23, minute=59, second=59)
        unix_end = int(time.mktime(day_end.timetuple()))
        
        url = 'https://finance.yahoo.com/quote/{}/history?'
        url += 'period1={}&period2={}'
        url += '&filter=history'
        url += '&interval=1d'
        url += '&frequency=1d'
        self.url = url.format(self.symbol, unix_start, unix_end)
        
    def read(self):
        import requests, re, json
       
        r = requests.get(self.url)
        
        ptrn = r'root\.App\.main = (.*?);\n}\(this\)\);'
        txt = re.search(ptrn, r.text, re.DOTALL).group(1)
        jsn = json.loads(txt)
        df = pd.DataFrame(
                jsn['context']['dispatcher']['stores']
                ['HistoricalPriceStore']['prices']
                )
        #print df.columns
        df.insert(0, 'symbol', self.symbol)
        df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
        
        # drop rows that aren't prices
        df = df.dropna(subset=['close'])
        
        df = df[['symbol', 'date', 'high', 'low', 'open', 'close', 
                 'volume', 'adjclose']]
        df = df.set_index('symbol')
        return df

## Function which send msg to (Adi's US phone number)
def send_iMessage(msg, buddies):
    for buddy in buddies:
        cmd = '''osascript<<END

        tell application "Messages"

        send "''' + msg + '''" to buddy "''' + buddy + '''" of (service 1 whose service type is iMessage)

        end tell

        END'''
        os.system(cmd)

Stock_Name = 'NBEV'
while 1==1 :
    ydr = YahooDailyReader(Stock_Name)

    df = ydr.read()

    finaldf = df.head(1)
    #print finaldf
    price_in_float = float(finaldf['close'].values[0])
    text_to_be_sent = Stock_Name + " Current Price: " + str(price_in_float)


    ## put the numbers the msgs should be sent to here:
    recipients = ["+15405562408"]

    ## Threshold Price
    Up_Threshold = 19.99
    Down_Threshold = 15.00
    if price_in_float > Up_Threshold or price_in_float < Down_Threshold:
        print text_to_be_sent
        send_iMessage(text_to_be_sent, recipients)
        break
    
    time.sleep(30)

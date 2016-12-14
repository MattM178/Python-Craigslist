# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 11:33:25 2016

@author: MattMoss

updated Nov 7th 2:12:00 2016
"""

import pandas as pd
import requests
import numpy as np
import string
from bs4 import BeautifulSoup as bs4

url_base = 'https://cleveland.craigslist.org/search/apa?query=tremont'
#params = dict(bedrooms=1)
rsp = requests.get(url_base)
#print(rsp.url)

html = bs4(rsp.text, 'html.parser')
#print(html.prettify()[:1000])

apts = html.find_all('p', attrs={'class': 'result-info'})
#print(len(apts))

this_appt = apts[15]
#print(this_appt.prettify())

size = this_appt.findAll(attrs={'class': 'housing'})[0].text
#print(size)

def find_size_and_brs(size):
    #print(size)
    split = size.split('-')
   # print(split)
    #print(len(split))
    if len(split) == 3:
        n_brs = split[0].replace('br', '')
        this_size = split[1].replace('ft2', '')
    elif 'br' in split[0]:
        # It's the n_bedrooms
        n_brs = split[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in split[0]:
        # It's the size
        this_size = split[0].replace('ft2', '')
        n_brs = np.nan
    return float(this_size), float(n_brs)

this_size, n_brs = find_size_and_brs(size)
this_time = this_appt.find('time')['datetime']
this_time = pd.to_datetime(this_time)
this_price = float(this_appt.find('span', {'class': 'result-price'}).text.strip('$'))
this_title = this_appt.find('a', attrs={'class': 'result-title hdrlnk'}).text

#print('\n'.join([str(i) for i in [this_size, n_brs, this_time, this_price, this_title]]))

def find_prices(results):
    prices = []
    for rw in results:
        price = rw.find('span', {'class': 'result-price'})
        if price is not None:
            price = float(price.text.strip('$'))
        else:
            price = np.nan
        prices.append(price)
    return prices

def find_times(results):
    times = []
    for rw in apts:
        if time is not None:
            time = time['datetime']
            time = pd.to_datetime(time)
        else:
            time = np.nan
        times.append(time)
    return times
# Now loop through all of CL and store the results
results = []  # We'll store the data here
# Careful with this...too many queries == your IP gets banned temporarily
search_indices = np.arange(0, 2500, 100)
#for loc in loc_prefixes:
    #print(loc)
for i in search_indices:
        url = 'http://cleveland.craigslist.org/search/apa'
        resp = requests.get(url, params={'bedrooms': 1, 's': i})
        txt = bs4(resp.text, 'html.parser')
        apts = txt.findAll(attrs={'class': "result-info"})
        
        # Find the size of all entries
        size_text = [rw.findAll(attrs={'class': 'housing'})[0].text
                     for rw in apts]
        sizes_brs = [find_size_and_brs(stxt) for stxt in size_text]
        sizes, n_brs = zip(*sizes_brs)  # This unzips into 2 vectors
     
        # Find the title and link
        title = [rw.find('a', attrs={'class': 'result-title hdrlnk'}).text
                      for rw in apts]
        links = [rw.find('a', attrs={'class': 'result-title hdrlnk'})['href']
                 for rw in apts]
        
        # Find the time
        time = [pd.to_datetime(rw.find('time')['datetime']) for rw in apts]
        price = find_prices(apts)
        
        # We'll create a dataframe to store all the data
        data = np.array([time, price, sizes, n_brs, title, links])
        col_names = ['time', 'price', 'size', 'brs', 'title', 'link']
        df = pd.DataFrame(data.T, columns=col_names)
        df = df.set_index('time')
        
        # Add the location variable to all entries
        #df['loc'] = loc
        results.append(df)
        
# Finally, concatenate all the results
results = pd.concat(results, axis=0)

#Deprecated format
#results[['price', 'size', 'brs']] = results[['price', 'size', 'brs']].convert_objects(convert_numeric=True)

#New format
results[['price', 'size', 'brs']] = results[['price', 'size', 'brs']].apply(pd.to_numeric)

results.head()

ax = results.hist('price', bins=np.arange(0, 4000, 100))[0, 0]
ax.set_title('Apartments for Rent.', fontsize=20)
ax.set_xlabel('Price', fontsize=18)
ax.set_ylabel('Count', fontsize=18)

use_chars = string.ascii_letters +\
    ''.join([str(i) for i in range(10)]) +\
    ' /\.'
results['title'] = results['title'].apply(
    lambda a: ''.join([i for i in a if i in use_chars]))

#enter your own path for saving csv
results.to_csv('C:\\Users\\craigslist_results.csv')
print('Done')

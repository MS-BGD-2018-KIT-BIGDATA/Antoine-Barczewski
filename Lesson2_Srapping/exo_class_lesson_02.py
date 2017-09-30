
import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://www.cdiscount.com/search/10/acer.html'


def getSoupFromURL(url):
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    else:
        return None


def getPrices(soup):
    previousPrice = pd.DataFrame(list(map(lambda x: x.text.replace(',','.'),soup.find_all(class_= 'prdtPInfoTC'))), columns=['previousPrice']).astype(float)
    currentPrice = pd.DataFrame(list(map(lambda x:x.text.replace('€','.'),soup.find_all(class_='prdtPrice'))),columns=['currentPrice']).astype(float)
    prtID = pd.DataFrame(list(map(lambda x: x.text,soup.find_all(class_= 'prdtBTit'))),columns=['prtID'])
    prices = pd.concat([prtID, previousPrice, currentPrice], axis=1)
    return prices

soup = getSoupFromURL(url)
prices = getPrices(soup)

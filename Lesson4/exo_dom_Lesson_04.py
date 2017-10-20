# Script to retrive all zoe offers on boncoin and compare price with lacentral's

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import itertools
import ipdb


def getSoupFromURL(url, method='get', data={}):

    if method == 'get':
        res = requests.get(url)
    elif method == 'post':
        res = requests.post(url, data=data)
    else:
        return None

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    else:
        return None


def urlBonCoin(region, page, brand, model):
    return 'https://www.leboncoin.fr/voitures/offres/'+region+'/?o='+str(page)+'&brd='+brand+'&mdl='+model


def getBonCoinTable(url, itemInfo_class = 'list_item clearfix trackable', carName_loc = 'title', carURI_loc = 'href'):
    soup = getSoupFromURL(url)
    if soup:
        content = soup.find_all(class_=itemInfo_class)
        carName = []
        carURI = []
        for car in content:
            carName += [car.get(carName_loc)]
        for car in content:
            carURI += ['https:' + car.get(carURI_loc)]
        return pd.DataFrame({'carName': carName, 'carURI': carURI})
    else:
        0


def getBonCoinIntel(url, submodel, zipcodeDefault=75001):
    soup = getSoupFromURL(url)
    # Retrieve properties and values from table
    properties = list(map(lambda x: x.text.strip(),
                      soup.find_all("span", class_='property')))
    values = list(map(lambda x: x.text.strip(),
                      soup.find_all("span", class_='value')))
    car_intel = {property: value for
                 property, value in zip(properties, values)}
    # Retrieve car model
    model = re.search(submodel,
                      soup.find(attrs={'itemprop': 'description'}).text.lower())
    if model:
        car_intel['model'] = model.group(0)
    else:
        car_intel['model'] = 'inconnu'
    # Retrieve user phone
    phone = re.search(r'(\d{2}(\.|\s)?){5}',
                      soup.find(attrs={'itemprop': 'description'}).text.lower())
    if phone:
        car_intel['phone'] = phone.group(0)
    else:
        car_intel['phone'] = 'inconnu'
    # Retrieve user zipcode
    zipcode = re.search(r'(\d{5})$', car_intel['Ville'])
    if zipcode:
        car_intel['zipcode'] = int(zipcode.group(0))
    else:
        car_intel['zipcode'] = zipcodeDefault
    # Clean data
    car_intel['Prix'] = int(re.search('\d+', car_intel['Prix'].replace(' ', '')).group(0))
    car_intel['Kilométrage'] = int(re.search('\d+', car_intel['Kilométrage'].replace(' ', '')).group(0))

    return car_intel


# Main
if __name__ == "__main__":
    regions = ['ile_de_france', 'PACA']
    maxPage = 6
    cat = 'auto'
    brand = 'Renault'
    model = 'Zoe'
    submodel = 'zen|intens|life'

    df_boncoin = pd.DataFrame(columns=['carName', 'carURI'])
    for region in regions:
        for page in range(maxPage):
            url_boncoin = urlBonCoin(region, page, brand, model)
            df_boncoin_modelURI = getBonCoinTable(url_boncoin)
            df_boncoin = df_boncoin.append(df_boncoin_modelURI)
    ipdb.set_trace()
    df_car_intel = pd.DataFrame(list(map(getBonCoinIntel,
                                     df_boncoin['carURI'],
                                     itertools.repeat(submodel, len(df_boncoin['carURI'])))))
    df_boncoin[df_car_intel.columns] = df_car_intel

    urlCentral = 'https://www.lacentrale.fr/cote-'+cat+'-'+brand+'-'+model+'-'
    df_boncoin['cote'] = df_boncoin.apply(lambda x: getSoupFromURL(urlCentral+x['model']+
                                                    '-'+x['Année-modèle']+'.html', 'post',
                                                    {'km': x['Kilomètrage'], 'zipcode': x['zipcode']}).
                                                    find(class_='jsRefinedQuot').text)

    df_boncoin.to_csv('boncoinCote.csv')

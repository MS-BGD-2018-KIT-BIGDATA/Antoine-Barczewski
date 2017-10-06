import pandas as pd
import googlemaps

url = 'https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peupl%C3%A9es'


def getAuthentification():
    with open('secret', 'r', encoding='utf8') as input_file:
        token = input_file.readline().strip()
    return token


def getTable(url):
    df_html = pd.read_html(url)
    df_html = df_html[0].ix[1:, :1]
    df_html.rename(columns={0: 'rang', 1: 'ville'}, inplace=True)
    return df_html


def getVille(df, numberOfTown):
    origins = df.ix[:numberOfTown, 'ville']
    destinations = origins.copy()
    return origins, destinations


df = getTable(url)
origins, destinations = getVille(df, 10)

# Iinit api client
key = getAuthentification()
client = googlemaps.Client(key=key)

res = pd.DataFrame(index=origins, columns=destinations)
res = client.distance_matrix(origins, destinations)['rows']

res_df = pd.DataFrame(list(map(lambda x: x['elements'], res)),
                      index=origins, columns=destinations)\
                      .applymap(lambda x: x['distance']['text'])

res_df.to_csv('distance_matrix.csv')

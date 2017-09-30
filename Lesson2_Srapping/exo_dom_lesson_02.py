import pandas as pd
import re
import os

#define function  to get metrics from dataframe
def getMetrics(df,strates,metrics,columnsName_Strate):
    sep = '|'
    sel = sep.join(strates)
    df = df.ix[df.Strate.str.contains('=\s('+sel+')$'),metrics+[columnsName_Strate]]
    metrics_series = pd.Series(metrics)
    if not metrics_series.str.contains('Euros').empty:
        for euroName in metrics_series[metrics_series.str.contains('Euros')]:
            df[euroName] = df[euroName].apply(lambda x: int(str(x).replace(' ','')))
    if not metrics_series.str.contains('milliers').empty:
        for milliersName in metrics_series[metrics_series.str.contains('milliers')]:
            df[milliersName] = df[milliersName]*1000
    return df

def getTable(year,formatTable,columnsName_Strate):
    df_html = pd.read_html(url+str(year),skiprows=formatTable['skiprows'],header=formatTable['header'])[formatTable['tableOfInterestIndex']]
    df_html = df_html.rename(columns={df_html.columns[formatTable['columnNumber_Strate']]:columnsName_Strate})
    return df_html


url = 'http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=056&dep=075&type=BPS&param=5&exercice=' #note that year has been removed from url parameter
yearmax = 2015
yearmin = 2010
strates = ['A','B','C','D']
metrics = ['Euros par habitant','En milliers d\'Euros']
formatTable = {'skiprows':5,'header':0,'columnNumber_Strate':3,'tableOfInterestIndex':0} #init format of table to retrieve
columnsName_Strate = 'Strate'

#init result table (df_res) for first year (to lazy to write column names)
df_html = getTable(year=yearmin,formatTable=formatTable,columnsName_Strate=columnsName_Strate)
df_html = getMetrics(df=df_html,strates=strates,metrics=metrics,columnsName_Strate=columnsName_Strate)
df_html['Annee'] = yearmin
df_res = df_html.copy()

#loop over years of table to scrap
years = range(yearmin+1,yearmax+1)
for year in years:
    df_html = getTable(year=year,formatTable=formatTable,columnsName_Strate=columnsName_Strate)
    df_html = getMetrics(df=df_html,strates=strates,metrics=metrics,columnsName_Strate=columnsName_Strate)
    df_html['Annee'] = year
    df_res = df_res.append(df_html)

path = os.getcwd()
filename = 'exo_dom_lesson_02_output.csv'
df_res.to_csv(path+'/'+filename,index=False)

de= pd.dfz

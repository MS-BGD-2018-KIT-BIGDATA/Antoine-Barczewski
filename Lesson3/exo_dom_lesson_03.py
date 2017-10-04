# Récupération des des users sur la page  https://gist.github.com/paulmillr/2657075
import pandas as pd
from multiprocessing import Pool
import re


url = 'https://gist.github.com/paulmillr/2657075'
p = Pool(3)


def getTable(url):
    df_html = pd.read_html(url)
    return df_html[0]


def getUserName(string):
    pattern = '([^\s]+)'
    user = re.search(pattern, string)
    if user is None:
        return None
    else:
        return user.group(1)


def getUser(df, columnName='User'):
    userList = df[columnName]
    userList = p.map(getUserName, userList)
    return list(userList)


df = getTable(url)
userList = getUser(df)

# Récupération des données par l'API GitHub
# en utilisant l'API Pyhton PyGithub

# from github import Github
#
# g = Github("c7939dc6289b311963d555b614e1ac2d187cc29d")
#
# for repo in g.get_user().get_repos():
#     print(repo.name)

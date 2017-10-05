# Récupération des des users sur la page
# https://gist.github.com/paulmillr/2657075
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import pandas as pd
from multiprocessing import Pool
import re
from github import Github
import ipdb

url = 'https://gist.github.com/paulmillr/2657075'
p = Pool(3)


def getTable(url):
    df_html = pd.read_html(url)
    return df_html[0]


def getUserName(string):
    pattern = '([^\s]+)'
    user = re.search(pattern, string)
    return user.group(1)


def getUser(df, columnName=['User', 'Contribs']):
    userFrame = df[columnName]
    userFrame['User'] = list(map(getUserName, userFrame['User']))
    return userFrame


# Récupération des données par l'API GitHub
# en utilisant l'API Pyhton PyGithub
g = Github('c7939dc6289b311963d555b614e1ac2d187cc29d')


def getReposTable(name):
    paginReposList = g.get_user(name).get_repos()
    reposName = []
    reposStar = []
    for repo in paginReposList:
        reposStar += [repo.stargazers_count]
        reposName += [repo.name]
    return pd.DataFrame({'name': name, 'repo': reposName,
                        'starCount': reposStar})


# if __name__ == '__main__':
#     df = getTable(url)
#     userFrame = getUser(df)
df = getTable(url)
userFrame = getUser(df)

repoTable = pd.DataFrame(columns=['name', 'repo', 'starCount'])
for name in userFrame['User'][:5]:
    repoTable = repoTable.append(getReposTable(name))

starAvg = repoTable.groupby(['name']).agg({'repo': 'count',
                                          'starCount': 'sum'})
starAvg_nContribs = starAvg.merge(userFrame, left_index=True, right_on='User',
                                  how='inner')

# Let's plot results
# Init seaborn
sns.set_context("poster")
sns.set_palette("colorblind")
sns.axes_style()
sns.set_style({'legend.frameon': True})

# retrieve metrics and label
x = starAvg_nContribs.Contribs
y = starAvg_nContribs.starCount / starAvg_nContribs.repo
n = starAvg_nContribs.User

fig, ax1 = plt.subplots()

ax1.scatter(x, y, alpha=0.5)
ax1.set_xlabel('contribs')
ax1.set_ylabel('avg_starPerRepo')

for i, name in enumerate(n):
    ax1.annotate(name, (x[i], y[i]))

plt.rcParams.update({'font.size': 9})

fig.tight_layout()
plt.show()

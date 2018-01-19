## Create interaction matrix of Destinations and Tags so Xij = 0 if Destination i has Tag j and 0 otherwise
## Create matrix of Users and Tags so Yij = sum(Tags j from User i's favorites sites)
## Find dot product of these two matrices and sort descending to determine whih destinations User i is most likely to like

## This is a large WIP and I'll probably end up employing a bunch of weird libraries I don't currently know about

import numpy as np
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='Jacob',
                             password='691748jw',
                             db='travelers',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cur = connection.cursor()
cur.execute("SELECT TagID FROM tags")
tags = cur.fetchall()

cur.execute("SELECT * FROM destinations")
dest = cur.fetchone()
cur.execute("SELECT TagID FROM dest_tags WHERE DestID = 12")
dest_tags = cur.fetchall()
cur.close()

destTags = []
i = 0
while i < len(tags):
    destTags.append(tag['TagID'])

listofzeros = [0] * len(tags)
print(listofzeros)
print(destTags)
# zeros = 
# destList = []
# destList.append(dest['DestName'])
# for tag in dest_tags:
#     if tag['DestID'] == dest['DestID']:
#         print(tag)

# dests = [0, 1, 1, 0]
# users = [7, 4, 0, 6]
# result = np.dot(dests, users)
# print(result)
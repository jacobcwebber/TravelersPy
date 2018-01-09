## Create interaction matrix of Destinations and Tags so Xij = 0 if Destination i has Tag j and 0 otherwise
## Create matrix of Users and Tags so Yij = sum(Tags j from User i's favorites sites)
## Find dot product of these two matrices and sort descending to determine whih destinations User i is most likely to like

## This is a large WIP and I'll probably end up employing a bunch of weird libraries I don't currently know about

import numpy
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
dests = cur.fetchall()

cur.execute("SELECT TagID FROM dest_tags")
dest_tags = cur.fetchall()
cur.close()

destList = []
for dest in dests:
    destList.append(dest['DestName'].encode("ascii"))
print(destList)

# dests = [0, 1, 1, 0]
# users = [7, 4, 0, 6]
# result = numpy.dot(dests, users)
# print(result)
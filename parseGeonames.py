#!/usr/bin/python3

import sqlite3 as sq 
import csv

dbConnection = sq.connect("annot.db")
db = dbConnection.cursor()

# remove everything from table
#db.execute("delete from locations")
#db.execute("DELETE FROM sqlite_sequence WHERE name = 'locations'")

geoFile = open("geonames/allCountries.txt", "r")
reader = csv.reader(geoFile, delimiter='\t')

num = 0
numToInsert = 0
countries = ["ES","FR","DE","BE","IT","GB", "AT"]

for line in reader:
    geonameId = line[0]
    name = line[1]
    alternate = line[3]
    latCoord = line[4]
    longCoord = line[5]
    featureClass = line[6]
    featureCode = line[7]
    country = line[8]

    num += 1
    if num%10000==0:
        print("checking index",num)

    if country not in countries:
        continue

    sql = 'INSERT INTO locations (geonameId, name, alternate, lat, long, class, code, country) VALUES (?,?,?,?,?,?,?,?)'
    values = (geonameId, name, alternate, latCoord, longCoord, featureClass, featureCode, country)
    db.execute(sql, values)

    numToInsert += 1

    if numToInsert%10000==0:
        print("committing",numToInsert)
        dbConnection.commit()

# last inserts    
dbConnection.commit()
print("inserted: ",numToInsert,"from:",num,"records")


from mongoengine import connect
from flask import Flask,jsonify,url_for,request,render_template, Response,helpers
from flask_restful import reqparse
import os, urllib
from openpyxl import load_workbook
from collections import defaultdict, OrderedDict
from werkzeug.contrib.atom import AtomFeed, FeedEntry
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
import jxmlease
import csv
from modal import Attendance, Year, EntryScore, Score, Nongov, Gov, Spec

###### Upload source to the database
app = Flask(__name__)

cwd = os.getcwd()
cwd1 = cwd + '/attendance.csv'
address = "https://data.cese.nsw.gov.au/data/dataset/68b47d34-a014-4345-b41c-c97b8b58aca3/resource/d7decef3-e026-4268-a5f3-8caad0322f90/download/2011-2017-attendance-rates-by-nsw-government-schools.csv"
urllib.request.urlretrieve(address, cwd1)
with open('attendance.csv','r') as f:
 a = csv.reader(f)
 lines = [row for row in a]
 lines.pop()
 for i in range(1,len(lines)):
     year = list()
     n = 2
     while n <= 8:
         year.append(Year(lines[0][n],lines[i][n]))
         n += 1
     attendance = Attendance(lines[i][0],lines[i][1],year)
     attendance.save()

cwd2 = cwd + '/entry score.csv'
address = "https://data.cese.nsw.gov.au/data/dataset/bf5acb6c-2e6d-3b7e-be62-881f434fb122/resource/44188b49-7044-453a-a77d-4090b1f00d55/download/2015-2018-selective-high-schools-minimum-entry-scores.csv"
urllib.request.urlretrieve(address, cwd2)
with open('entry score.csv','r') as f:
 b = csv.reader(f)
 lines = [row for row in b]
 for i in range(1, len(lines)):
     score = list()
     n = 1
     while n <= 4:
         score.append(Score(int(lines[0][n][-4:]), int(lines[i][n])))
         n += 1
     entryscore = EntryScore(lines[i][0], score)
     entryscore.save()



cwd3 = cwd + '/Nongov school.csv'
address = "https://data.cese.nsw.gov.au/data/dataset/1d019767-d953-426c-8151-1a6503d5a08a/resource/a5871783-7dd8-4b25-be9e-7d8b9b85422f/download/datahub_nongov_locations-2017.csv"
urllib.request.urlretrieve(address, cwd3)
with open('Nongov school.csv','r',encoding = "ISO-8859-1") as f:
 f.readline()
 c = csv.reader(f)
 for line in c:
     nongov = Nongov(line[2],line[6],line[7],line[3],line[4],line[5])
     nongov.save()

cwd4 = cwd + '/gov school.csv'
address = "https://data.cese.nsw.gov.au/data/dataset/027493b2-33ad-3f5b-8ed9-37cdca2b8650/resource/2ac19870-44f6-443d-a0c3-4c867f04c305/download/masterdatasetnightlybatchcollections.csv"
urllib.request.urlretrieve(address, cwd4)
with open('gov school.csv','r',encoding = "ISO-8859-1") as f:
 f.readline()
 d = csv.reader(f)
 for line in d:
     gov = Gov(line[0],line[2],line[13],line[22],line[3],line[4],line[5])
     gov.save()


cwd5 = cwd + "/specialist school.csv"
address = "https://data.cese.nsw.gov.au/data/dataset/85699cfe-366e-4caa-910f-bb7bedfdc311/resource/a963949f-99b5-49a9-a208-d15ab9a4d320/download/masterdatasetnightlybatchsupport.csv"
urllib.request.urlretrieve(address, cwd5)
with open('specialist school.csv','r',encoding = "ISO-8859-1") as f:
    f.readline()
    e = csv.reader(f)
    for line in e:
        spec = Spec(line[0],line[1],line[3],line[2],line[6])
        spec.save()


if __name__ == "__main__":
    app.run()
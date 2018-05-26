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


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
connect(host = 'mongodb://jnie1026:Ray38208382@ds151809.mlab.com:51809/my_database')
###### disable class is saved in a dict
raw_input = {"Autism (Au)" : 1,
            "Moderate/Severe intellectual disability (IO/IS)" : 2,
            "MC Multi Categorical" : 3,
            "EI Early Intervention" : 4,
            "Moderate intellectual disability (IO)" : 5,
            "Autism/moderate intellectual disability (IO/Au)" : 6,
            "Mild intellectual disability (IM)" : 7,
            "Mental health issues (ED Emotional Disturbance)" : 8,
            "Deaf/hearing impaired (H)" : 9,
            "Physical disability (P)" : 10,
            "Behavioural issues (BD)" : 11,
            "Severe intellectual disability (IS)" : 12,
            "Blind/vision impaired (V)" : 13}

disable = {1: ("Supporting students with autism (Au)","Supporting students with autism and/or moderate intellectual disability (IO/Au)") ,
           2: "Supporting students with moderate and students with severe intellectual disability (IO/IS)",
           3: "Supporting students with a range of disabilities with similar support needs (MC Multi Categorical)",
           4: "Supporting students with disability prior to school (EI Early Intervention)",
           5: ("Supporting students with moderate intellectual disability (IO)","Supporting students with autism and/or moderate intellectual disability (IO/Au)"),
           6: "Supporting students with autism and/or moderate intellectual disability (IO/Au)",
           7: "Supporting students with mild intellectual disability (IM)",
           8: "Supporting students with mental health issues (ED Emotional Disturbance)",
           9: "Supporting students who are deaf or hearing impaired (H)",
           10: "Supporting students with physical disability (P)",
           11: "Supporting students with behavioural issues (BD)",
           12: ("Supporting students with severe intellectual disability (IS)","Supporting students with moderate and students with severe intellectual disability (IO/IS)"),
           13: "Supporting students who are blind or vision impaired (V)"}

###### Upload source to the database

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
     nongov = Nongov(line[2],line[6],line[7],line[3],line[4],line[5],line[15],line[8])
     nongov.save()

cwd4 = cwd + '/gov school.csv'
address = "https://data.cese.nsw.gov.au/data/dataset/027493b2-33ad-3f5b-8ed9-37cdca2b8650/resource/2ac19870-44f6-443d-a0c3-4c867f04c305/download/masterdatasetnightlybatchcollections.csv"
urllib.request.urlretrieve(address, cwd4)
with open('gov school.csv', 'r', encoding="ISO-8859-1") as f:
    f.readline()
    d = csv.reader(f)
    for line in d:
        gov = Gov(line[0], line[2], line[13], line[22], line[3], line[4], line[5], line[6], line[7], line[8], line[9])
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
 

#### look up non-government school
@app.route("/")
def root():
    return render_template("client.html")

@app.route("/school/all", methods=['GET'])
def search_all():
    output,locations = search_gov()
    output2,locations2 =search_nongov()
    name_list = list(output.keys())
    locations_list = google_maps.form_geocode_list(name_list,locations) 
    name_list = list(output2.keys())
    locations_list2 = google_maps.form_geocode_list(name_list,locations2) 
    return render_template("all.html",schools = output,locations=locations_list,schools2=output2,locations2=locations_list2)


@app.route("/school/nongov", methods=['GET'])
def print_nongov():
    output,locations = search_nongov()
    name_list = list(output.keys())
    locations_list = google_maps.form_geocode_list(name_list,locations) 
    return render_template("non_gov.html",schools=output,locations=locations_list)

def search_nongov():
    parser = reqparse.RequestParser()
    parser.add_argument('condition')
    args = parser.parse_args()
    condition = args.get("condition")
    address = list()
    if condition.isdigit():
        output = OrderedDict()
        for school in Nongov.objects(postcode = condition):
            content = OrderedDict()
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"', '')
            content['school website'] = school.url
            content['sector'] = school.sector
            output[school.name] = content
            address.append(school.street.replace('"', '') + ', ' + school.suburb+'nsw')     
        return output, address
    
    else:
        output = OrderedDict()
        for school in Nongov.objects(suburb = condition):
            content = OrderedDict()
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"', '')
            content['school website'] = school.url
            content['sector'] = school.sector
            output[school.name] = content
            address.append(school.street.replace('"', '') + ', ' + school.suburb+'nsw')
        return output, address

 
#### look up government school
@app.route('/school/gov', methods=['GET'])

def print_gov():
    output,locations = search_gov()
    name_list = list(output.keys())
    locations_list = google_maps.form_geocode_list(name_list,locations)
    return render_template("gov.html",schools=output,locations=locations_list)

def search_gov():
    parser = reqparse.RequestParser()
    parser.add_argument('condition')
    args = parser.parse_args()
    condition = args.get('condition')
    condition = condition.strip()
    address = []
    count=0
    disable_support = False
    if condition.isdigit():
        output = OrderedDict()
        for school in Gov.objects(postcode=condition):
            count+=1
            content = OrderedDict()
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"', '')
            content['count']='a'+str(count)

            content['schooling'] = school.schooling
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['code'] = school.code
            content['phone'] = school.phone
            content['school email'] = school.school_email
            content['fax'] = school.fax
            content['student number'] = school.student_number

            attendance_rate = [['Year', 'Attendance Rate']]
            for a in Attendance.objects(code=school.code):
                for y in a.year:
                    attendance_list = []
                    attendance_list.append(int(y.year))
                    attendance_list.append(float(y.rate))
                    attendance_rate.append(attendance_list)
                content['attendence rate'] = attendance_rate
            entry_rate = [['Year', 'Entry Score']]
            for s in EntryScore.objects(name=school.name):
                for y in s.score:
                    entry_list = []
                    entry_list.append(int(y.year))
                    entry_list.append(float(y.score))
                    entry_rate.append(entry_list)
                content['entry score'] = entry_rate
            for s in Spec.objects(name = school.name):
                disable_support = True
                content['disable_support'] = disable_support
            output[school.name] = content
            address.append(school.street.replace('"', '') + ', ' + school.suburb+'NSW')
        return output, address

    else:
        output = OrderedDict()
        for school in Gov.objects(suburb=condition):
            count+=1
            content = OrderedDict()
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"', '')
            content['count']=str(count)

            content['schooling'] = school.schooling
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['code'] = school.code
            content['phone'] = school.phone
            content['school email'] = school.school_email
            content['fax'] = school.fax
            content['student number'] = school.student_number

            attendance_rate = [['Year', 'Attendance Rate']]
            for a in Attendance.objects(code=school.code):
                for y in a.year:
                    attendance_list = []
                    attendance_list.append(int(y.year))
                    attendance_list.append(float(y.rate))
                    attendance_rate.append(attendance_list)
                content['attendence rate'] = attendance_rate
            entry_rate = [['Year', 'Entry Score']]
            for s in EntryScore.objects(name=school.name):
                for y in s.score:
                    entry_list = []
                    entry_list.append(int(y.year))
                    entry_list.append(float(y.score))
                    entry_rate.append(entry_list)
                content['entry score'] = entry_rate
            for s in Spec.objects(name = school.name):
                disable_support = True
                content['disable_support'] = disable_support
            output[school.name] = content
            address.append(school.street.replace('"', '') + ', ' + school.suburb+'NSW')
        return output, address

if __name__ == "__main__":
    app.run()

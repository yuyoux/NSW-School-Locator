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
disable ={1:"Supporting students with autism (Au)", 2:"Supporting students with moderate and students with severe intellectual disability (IO/IS)",
          3:"Supporting students with a range of disabilities with similar support needs (MC Multi Categorical)", 4:"Supporting students with disability prior to school (EI Early Intervention)",
          5:"Supporting students with moderate intellectual disability (IO)", 6:"Supporting students with autism and/or moderate intellectual disability (IO/Au)",
          7:"Supporting students with mild intellectual disability (IM)", 8:"Supporting students with mental health issues (ED Emotional Disturbance)" ,
          9:"Supporting students who are deaf or hearing impaired (H)", 10:"Supporting students with physical disability (P)",
          11:"Supporting students with behavioural issues (BD)", 12:"Supporting students with severe intellectual disability (IS)",
          13:"Supporting students who are blind or vision impaired (V)"}

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
 

#### look up non-government school
@app.route("/")
def root():
    return render_template("client.html")

@app.route("/school/all", methods=['GET'])
def search_all():
    output = search_nongov
    output +=search_specialist()
    output +=search_gov()
    return render_template("all.html",schools = output)


@app.route("/school/nongov", methods=['GET'])
def print_nongov():
    output = search_nongov()
    return render_template("non_gov.html",schools=output)

def search_nongov():
    parser = reqparse.RequestParser()
    parser.add_argument('querytype')
    parser.add_argument('condition')
    args = parser.parse_args()
    querytype = args.get("querytype")
    condition = args.get("condition")
    address = list()
    if querytype=='Postcode':
        output = OrderedDict()
        for school in Nongov.objects(postcode = condition):
            content = OrderedDict()
            content['schooling'] = school.schooling
            content['school gender'] = school.school_gender
            content['street'] = school.street
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            output[school.name] = content
            address.append(school.street + ', ' + school.suburb)     
        return output, address
    if querytype=='Suburb':
        output = OrderedDict()
        for school in Nongov.objects(suburb = condition):
            content = OrderedDict()
            content['schooling'] = school.schooling
            content['school gender'] = school.school_gender
            content['street'] = school.street
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            output[school.name] = content
            address.append(school.street + ', ' + school.suburb)
        return output, address

    if querytype=='Partial School Name':
        name = condition.lower()
        output = OrderedDict()
        for school in Nongov.objects:
            if name in school.name.lower():
                content = OrderedDict()
                content['schooling'] = school.schooling
                content['school gender'] = school.school_gender
                content['street'] = school.street
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                output[school.name] = content
                address.append(school.street + ', ' + school.suburb)
        return output, address
        

 
#### look up school with special support 
@app.route("/school/specialist", methods=['GET'])
def print_special():
    output =search_specialist()
    return render_template("special.html",schools=output)
     
def search_specialist():
    parser = reqparse.RequestParser()
    parser.add_argument('querytype')
    parser.add_argument('condition')
    parser.add_argument('disabled')
    args = parser.parse_args()
    querytype = args.get("querytype")
    condition = args.get("condition")
    disabled = args.get("disabled")
    address = list()
    if querytype=='Postcode':
        if disabled =='class type': ####### Did not select disable class
            output = OrderedDict()
            for school in Spec.objects(postcode = condition):
                if school.name in output:
                    output[school.name]['class type'].append(school.class_type)
                    continue
                content = OrderedDict()
                content['code'] = school.code
                for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                content['class type'] = [school.class_type]
                for score_record in EntryScore.objects(name = school.name):
                    entry_score = OrderedDict()
                    for score in score_record.score:
                        entry_score[str(score.year)] = score.score
                    content['entry score'] = entry_score
                for attendace in Attendance.objects(code = school.code):
                    attend = OrderedDict()
                    for year in attendace.year:
                        attend[str(year.year)] = year.rate
                    content['attendance rate'] = attend
                output[school.name] = content
            return output, address
        ################################################################need modify disable dict
        output = OrderedDict()
        for school in Spec.objects(postcode=condition,class_type = disable[int(class_type)]):
            content = OrderedDict()
            content['code'] = school.code
            for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['class type'] = [school.class_type]
            for score_record in EntryScore.objects(name=school.name):
                entry_score = OrderedDict()
                for score in score_record.score:
                    entry_score[str(score.year)] = score.score
                content['entry score'] = entry_score
            for attendace in Attendance.objects(code=school.code):
                attend = OrderedDict()
                for year in attendace.year:
                    attend[str(year.year)] = year.rate
                content['attendance rate'] = attend
            output[school.name] = content
        return output,address


    if querytype=='Suburb':
        if disabled =='class type':
            output = OrderedDict()
            for school in Spec.objects(suburb = condition):
                if school.name in output:
                    output[school.name]['class type'].append(school.class_type)
                    continue
                content = OrderedDict()
                content['code'] = school.code
                for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                content['class type'] = [school.class_type]
                for score_record in EntryScore.objects(name = school.name):
                    entry_score = OrderedDict()
                    for score in score_record.score:
                        entry_score[str(score.year)] = score.score
                    content['entry score'] = entry_score
                for attendace in Attendance.objects(code = school.code):
                    attend = OrderedDict()
                    for year in attendace.year:
                        attend[str(year.year)] = year.rate
                    content['attendance rate'] = attend
                output[school.name] = content
                print(output)
            return output, address

        output = OrderedDict()
        for school in Spec.objects(suburb = condition, class_type=disable[int(class_type)]):
            content = OrderedDict()
            content['code'] = school.code
            for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['class type'] = [school.class_type]
            for score_record in EntryScore.objects(name=school.name):
                entry_score = OrderedDict()
                for score in score_record.score:
                    entry_score[str(score.year)] = score.score
                content['entry score'] = entry_score
            for attendace in Attendance.objects(code=school.code):
                attend = OrderedDict()
                for year in attendace.year:
                    attend[str(year.year)] = year.rate
                content['attendance rate'] = attend
            output[school.name] = content
        return output, address

    if querytype=='School Code':
        if disabled =='class type':
            output = OrderedDict()
            for school in Spec.objects(code = condition):
                if school.name in output:
                    output[school.name]['class type'].append(school.class_type)
                    continue
                content = OrderedDict()
                content['code'] = school.code
                for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                content['class type'] = [school.class_type]
                for score_record in EntryScore.objects(name = school.name):
                    entry_score = OrderedDict()
                    for score in score_record.score:
                        entry_score[str(score.year)] = score.score
                    content['entry score'] = entry_score
                for attendace in Attendance.objects(code = school.code):
                    attend = OrderedDict()
                    for year in attendace.year:
                        attend[str(year.year)] = year.rate
                    content['attendance rate'] = attend
                output[school.name] = content
            return output, address

        output = OrderedDict()
        for school in Spec.objects(code = condition, class_type=disable[int(class_type)]):
            content = OrderedDict()
            content['code'] = school.code
            for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['class type'] = [school.class_type]
            for score_record in EntryScore.objects(name=school.name):
                entry_score = OrderedDict()
                for score in score_record.score:
                    entry_score[str(score.year)] = score.score
                content['entry score'] = entry_score
            for attendace in Attendance.objects(code=school.code):
                attend = OrderedDict()
                for year in attendace.year:
                    attend[str(year.year)] = year.rate
                content['attendance rate'] = attend
            output[school.name] = content
        return output, address

    if querytype=='Partial School Name':
        if disabled =='class type':
            name = condition.lower()
            output = OrderedDict()
            for school in Spec.objects:
                if name in school.name.lower():
                    if school.name in output:
                        output[school.name]['class type'].append(school.class_type)
                        continue
                    content = OrderedDict()
                    content['code'] = school.code
                    for item in Gov.objects(code = school.code):
                        content['street'] = item.street
                        address.append(item.street + ', ' + school.suburb)
                    content['suburb'] = school.suburb
                    content['postcode'] = school.postcode
                    content['class type'] = [school.class_type]
                    for score_record in EntryScore.objects(name=school.name):
                        entry_score = OrderedDict()
                        for score in score_record.score:
                            entry_score[str(score.year)] = score.score
                        content['entry score'] = entry_score
                    for attendace in Attendance.objects(code=school.code):
                        attend = OrderedDict()
                        for year in attendace.year:
                            attend[str(year.year)] = year.rate
                        content['attendance rate'] = attend
                    output[school.name] = content
            return output, address

        name = condition.lower()
        output = OrderedDict()
        for school in Spec.objects:
            if name in school.name.lower() and school.class_type == disable[int(class_type)]:
                content = OrderedDict()
                content['code'] = school.code
                for item in Gov.objects(code = school.code):
                    content['street'] = item.street
                    address.append(item.street + ', ' + school.suburb)
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                content['class type'] = [school.class_type]
                for score_record in EntryScore.objects(name=school.name):
                    entry_score = OrderedDict()
                    for score in score_record.score:
                        entry_score[str(score.year)] = score.score
                    content['entry score'] = entry_score
                for attendace in Attendance.objects(code=school.code):
                    attend = OrderedDict()
                    for year in attendace.year:
                        attend[str(year.year)] = year.rate
                    content['attendance rate'] = attend
                output[school.name] = content
        return output, address

       


#### look up government school
@app.route('/school/gov', methods=['GET'])
def print_gov():
    output = search_gov()
    return render_template("gov.html",schools=output)

def search_gov():
    parser = reqparse.RequestParser()
    parser.add_argument('querytype')
    parser.add_argument('condition')
    args = parser.parse_args()
    querytype = args.get('querytype')
    condition = args.get('condition')
    condition=condition.strip()
    address = []
    if querytype=='Postcode':
        output = OrderedDict()
        for school in Gov.objects(postcode=condition):
            content = OrderedDict()
            content['schooling'] = school.schooling
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"','')
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['code'] = school.code
            output[school.name] = content
            address.append(school.street + ', ' + school.suburb)
        return output, address

    if querytype=='Suburb':
        output = OrderedDict()
        for school in Gov.objects(suburb=condition):
            content = OrderedDict()
            content['schooling'] = school.schooling
            content['school gender'] = school.school_gender
            content['street'] = school.street.replace('"','')
            content['suburb'] = school.suburb
            content['postcode'] = school.postcode
            content['code'] = school.code
            output[school.name] = content
            address.append(school.street + ', ' + school.suburb)
        return output, address

    if querytype=='Partial School Name':
        name = condition.lower()
        output = OrderedDict()
        for school in Gov.objects:
            if name in school.name.lower():
                content = OrderedDict()
                content['schooling'] = school.schooling
                content['school gender'] = school.school_gender
                content['street'] = school.street.replace('"','')
                content['suburb'] = school.suburb
                content['postcode'] = school.postcode
                content['code'] = school.code
                output[school.name] = content
                address.append(school.street + ', ' + school.suburb)
        return output, address

    if not condition:
        return 'False'


##entry_score-related search
@app.route('/entryscore', methods = ["GET"])
def show_entry():
    connect(host='mongodb://yuyoux:yongbao1110@ds231090.mlab.com:31090/9321a3')
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str)
    parser.add_argument('score', type=int)
    args = parser.parse_args()
    name = args.get('name')
    if name:
        name = name.lower()
        output = OrderedDict()
        for s in EntryScore.objects:
            content = OrderedDict()
            if name in s.name.lower():
                content['name'] = s.name
                entry = OrderedDict()
                for y in s.score:
                    entry[str(y.year)] = y.score
                content['entry score'] = entry
                output[s.name] = content
                return output
            else:
                return 'False'
    score = args.get('score')
    if score:
        output = []
        for s in EntryScore.objects:
            for y in s.score:
                if y.year == 2018 and int(y.score) <= score:
                    output.append(s.name)
        return output



if __name__ == "__main__":
    app.run()

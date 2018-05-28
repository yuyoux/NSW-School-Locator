from mongoengine import IntField, Document, EmbeddedDocument,ListField, EmbeddedDocumentField, StringField
import googlemaps


class GoogleMaps(object):
    # google maps service
    def __init__(self):
 
        self._GOOGLE_MAPS_KEY = 'AIzaSyDAkguZ-aHXwBGG4E79WDbSHsocwLIyeOU'
        self._Google_Geocod = googlemaps.Client(key=self._GOOGLE_MAPS_KEY)
 
    def convert_to_geocode(self,address):
        res = self._Google_Geocod.geocode(address) 
        return res[0]["geometry"]["location"]

    def form_geocode_list(self,ls1,ls2):
        res=[['Lat', 'Long', 'Name']]
        for i in range(len(ls1)):
            name = ls1[i]
            geo = self.convert_to_geocode(ls2[i])
            lat=geo['lat']
            lng=geo['lng']
            res.append([lat,lng,name])
        return res
        
    def form_geocodes(self,ls):
        res=[]
        for ele in ls:
            geo = self.convert_to_geocode(ele)
            res.append(geo)
        return res   
   
   
class Year(EmbeddedDocument):
    year = IntField(required=True)
    rate = StringField()

    def __init__(self, year,rate,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.rate = rate


class Attendance(Document):
    code = IntField(required=True)
    name = StringField(required=True)
    year = ListField(EmbeddedDocumentField(Year))

    def __init__(self, code,name, year=[],*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.name = name
        self.year = year

class Score(EmbeddedDocument):
    year = IntField(required=True)
    score = IntField(required=True)

    def __init__(self, year,score,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.score = score

class EntryScore(Document):
    name = StringField(required=True)
    score = ListField(EmbeddedDocumentField(Score))

    def __init__(self, name,score=[],*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.score = score

class Nongov(Document):
    name = StringField(required=True)
    schooling = StringField(required=True)
    school_gender = StringField(required=True)
    street = StringField(required=True)
    suburb = StringField(required=True)
    postcode = IntField(required=True)
    url = StringField()
    sector = StringField()

    def __init__(self, name, schooling, school_gender, street, suburb, postcode, url, sector,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.schooling = schooling
        self.school_gender = school_gender
        self.street = street
        self.suburb = suburb
        self.postcode = postcode
        self.url = url
        self.sector = sector

class Gov(Document):
    code = IntField(required=True)
    name = StringField(required=True)
    schooling = StringField(required=True)
    school_gender = StringField(required=True)
    street = StringField(required=True)
    suburb = StringField(required=True)
    postcode = IntField(required=True)
    phone = StringField(required=True)
    school_email = StringField(required=True)
    fax = StringField(required=True)
    student_number = StringField(required=True)

    def __init__(self, code,name, schooling, school_gender, street, suburb, postcode, phone, school_email, fax, student_number,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.name = name
        self.schooling = schooling
        self.school_gender = school_gender
        self.street = street
        self.suburb = suburb
        self.postcode = postcode
        self.phone = phone
        self.school_email = school_email
        self.fax = fax
        self.student_number = student_number

class Spec(Document):
    code = IntField(required=True)
    name = StringField(required=True)
    suburb = StringField(required=True)
    postcode = IntField(required=True)
    class_type = StringField()

    def __init__(self, code,name, suburb, postcode,class_type,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.name = name
        self.suburb = suburb
        self.postcode = postcode
        self.class_type = class_type

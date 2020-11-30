import sys
from pymongo import MongoClient
import json
from datetime import datetime
from entities import Patient, Disease

HOST = 'db'
PORT = 27017
client = MongoClient(host=HOST, port=PORT)
db = client['patients']
collection = db['patient']

def init():
    f = open('init.json', 'r')
    data = json.loads(f.read())
    print(data)
    for tmp in data:
        tmp['date'] = datetime.fromtimestamp(int((tmp['date_of_birth']['$date'])) / 1000).strftime('%Y-%m-%d')
        if collection.count({'phone_number': tmp['phone_number']}) > 0:
            continue
        else:
            patient = Patient(phone_number=tmp['phone_number'], name=tmp['name'],
                              date_of_birth=datetime.strptime(tmp['date'], '%Y-%m-%d'),
                              country=tmp['country'], city=tmp['city'])
            for c in tmp['diseases']:
                patient.diseases.append(c)
            for c in tmp['contacts']:
                patient.contacts.append(c)
            for c in tmp['symptoms']:
                patient.symptoms.append({'symptom':c['symptom'], 'date':c['date']})
            print(patient.__dict__)
            collection.insert_one(patient.__dict__)

init()

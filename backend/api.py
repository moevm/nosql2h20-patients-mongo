import json
from datetime import datetime
from bson import json_util
from flask import Blueprint, request, Response
from pymongo import *
from backend.db import *
from backend.entities import Disease, Patient

patients = Blueprint(name='patients', import_name=__name__)

patient = Blueprint(name='patient', import_name=__name__)
patient_delete = Blueprint(name='patient_delete', import_name=__name__)

patient_contacts = Blueprint(name='patient_contacts', import_name=__name__)
patient_diseases = Blueprint(name='patient_diseases', import_name=__name__)
patient_symptoms = Blueprint(name='patient_symptoms', import_name=__name__)

patient_contacts_put = Blueprint(name='patient_contacts_put', import_name=__name__)
patient_diseases_put = Blueprint(name='patient_diseases_put', import_name=__name__)
patient_symptoms_put = Blueprint(name='patient_symptoms_put', import_name=__name__)

patient_contacts_delete = Blueprint(name='patient_contacts_delete', import_name=__name__)
patient_diseases_delete = Blueprint(name='patient_diseases_delete', import_name=__name__)
patient_symptoms_delete = Blueprint(name='patient_symptoms_delete', import_name=__name__)

patients_add = Blueprint(name='patients_add', import_name=__name__)

patient_contacts_edit = Blueprint(name='patient_contacts_edit', import_name=__name__)
patient_diseases_edit = Blueprint(name='patient_diseases_edit', import_name=__name__)
patient_symptoms_edit = Blueprint(name='patient_symptoms_edit', import_name=__name__)


@patients.route('/patients', methods=['GET'])
def get_patients():
    docs_list = list(collection.find({}))
    return {"patient": json.loads(json.dumps(docs_list, default=json_util.default))}


@patient.route('/patient/<phone>', methods=['GET'])
def get_patient(phone):
    patient = collection.find_one({"phone_number": phone})
    return json.dumps(patient, default=json_util.default)


@patient_contacts.route('/patient/<phone>/contacts', methods=['GET'])
def get_patient_contacts(phone):
    contacts = collection.find_one({"phone_number": phone}, {"_id": 0, "contacts": 1})
    return {"phone": phone, "contacts": contacts['contacts']}


@patient_diseases.route('/patient/<phone>/diseases', methods=['GET'])
def get_patient_diseases(phone):
    diseases = collection.find_one({"phone_number": phone}, {"_id": 0, "diseases": 1})
    return {"phone": phone, "diseases": diseases['diseases']}


@patient_symptoms.route('/patient/<phone>/symptoms', methods=['GET'])
def get_patient_symptoms(phone):
    symptoms = collection.find_one({"phone_number": phone}, {"_id": 0, "symptoms": 1})
    return {"phone": phone, "symptoms": symptoms['symptoms']}


@patient_diseases_delete.route('/patient/<phone>/diseases', methods=['DELETE'])
def delete_patient_disease(phone):
    req = request.form
    disease = req['index']
    # db.patient.update({phone_number: "89516491048"}, {$unset:{"diseases.3":1}})
    collection.update_one({'phone_number': phone}, {'$unset': {'diseases.' + disease: 1}})
    collection.update_one({'phone_number': phone}, {'$pull': {'diseases': None}})
    return Response(status=200)


@patient_symptoms_delete.route('/patient/<phone>/symptoms', methods=['DELETE'])
def delete_patient_symptom(phone):
    req = request.form
    disease = req['index']
    collection.update_one({'phone_number': phone}, {'$unset': {'symptoms.' + disease: 1}})
    collection.update_one({'phone_number': phone}, {'$pull': {'symptoms': None}})
    return Response(status=200)


@patient_contacts_delete.route('/patient/<phone>/contacts', methods=['DELETE'])
def delete_patient_contact(phone):
    req = request.form
    disease = req['index']
    collection.update_one({'phone_number': phone}, {'$unset': {'contacts.' + disease: 1}})
    collection.update_one({'phone_number': phone}, {'$pull': {'contacts': None}})
    return Response(status=200)


@patient_contacts_put.route('/patient/<phone>/contacts', methods=['PUT'])
def add_patient_contact(phone):
    req = request.form
    contact = req['contact']
    collection.update_one({'phone_number': phone}, {'$push': {'contacts': contact}})
    return Response(status=200)


@patient_diseases_put.route('/patient/<phone>/diseases', methods=['PUT'])
def add_patient_disease(phone):
    req = request.form
    disease = req['disease']
    collection.update_one({'phone_number': phone}, {'$push': {'diseases': disease}})
    return Response(status=200)


@patient_symptoms_put.route('/patient/<phone>/symptoms', methods=['PUT'])
def add_patient_symptom(phone):
    req = request.form
    symptom = req['symptom']
    date = req['date']
    disease = Disease(symptom=symptom, date=date)
    collection.update_one({'phone_number': phone}, {'$push': {'symptoms': disease.__dict__}})
    return Response(status=200)


@patient_contacts_edit.route('/patient/<phone>/contacts', methods=['POST'])
def edit_patient_contact(phone):
    req = request.form
    contact_index = req['index']
    new_value = req['value']
    collection.update_one({'phone_number': phone}, {'$set': {'contacts.' + contact_index: new_value}})
    return Response(status=200)


# db.patient.update({phone_number:"89516491048"}, {$set:{"contacts.1": "DIMA"}})
@patient_diseases_edit.route('/patient/<phone>/diseases', methods=['POST'])
def edit_patient_disease(phone):
    req = request.form
    disease_index = req['index']
    new_value = req['value']
    collection.update_one({'phone_number': phone}, {'$set': {'diseases.' + disease_index: new_value}})
    return Response(status=200)


@patient_symptoms_edit.route('/patient/<phone>/symptoms', methods=['POST'])
def edit_patient_symptom(phone):
    req = request.json
    disease_index = req['index']
    new_value = req['value']
    collection.update_one({'phone_number': phone}, {'$set': {'symptoms.' + str(disease_index):
                                                                 Disease(symptom=new_value['symptom'],
                                                                         date=new_value['date']).__dict__
                                                             }})
    return Response(status=200)


@patients_add.route('/addPatient', methods=['POST'])
def add_patient():
    req = request.form
    patient = Patient(req['phone_number'], req['name'],
                      date_of_birth=datetime.strptime(req['date'], '%Y-%m-%d'),
                      country=req['country'], city=req['city'])
    collection.insert_one(patient.__dict__)
    return Response(status=200)


@patient_delete.route('/patient/<phone>', methods=['DELETE'])
def delete_patient(phone):
    collection.delete_one({"phone_number": phone})
    return Response(status=200)

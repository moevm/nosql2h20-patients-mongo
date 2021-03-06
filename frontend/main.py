import operator

from flask import Flask, render_template, send_file, request, redirect, send_from_directory, Response
import requests
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime, date
import json
import sys

app = Flask(__name__)
app.url_map.strict_slashes = False
PROTOCOL = 'http'
HOST = 'localhost'
if len(sys.argv) > 2:
    HOST = sys.argv[2]
PORT = '5000'
URL = PROTOCOL + '://' + HOST + ':' + PORT


@app.route('/export', methods=['POST', 'GET'])
def export_json():
    json_f = requests.get(URL+'/export').json()['patients']
    print(json_f)
    with open('static/data.json', 'w+', encoding='utf-8') as f:
        json.dump(json_f, f, ensure_ascii=False)
    return send_from_directory('./', 'static/data.json', as_attachment=True)


@app.route('/import', methods=['POST', 'GET'])
def import_json():
    if request.method == 'GET':
        return render_template('index.html')
    file = request.files['file']
    file.save(os.path.join('./static/', file.filename))
    with open('./static/' + file.filename) as f:
        data = json.load(f)
    requests.post(URL+'/import', data={"patients": json.dumps(data)})
    return redirect('/')


@app.route("/", methods=['GET', 'POST'])
def init():
    select = 'none'
    tmp_people = []
    people = requests.get(URL + '/patients')
    people = people.json()
    for ppl in people['patient']:
        tmp_people.append([
            ppl['phone_number'], ppl['name'],
            ppl['country'], ppl['city'],
            datetime.fromtimestamp(int((ppl['date_of_birth']['$date'])) / 1000).strftime('%Y-%m-%d')
        ])
    if request.method == 'POST':
        result = request.form
        tmp = request.form.get('input_search')
        for _, item in result.items():
            select = item
        if select == 'none':
            pass
        elif select == 'name':
            tmp_people = [tmp_people[i] for i in range(len(tmp_people)) if tmp_people[i][1] == tmp]
        elif select == 'country':
            tmp_people = [tmp_people[i] for i in range(len(tmp_people)) if tmp_people[i][2] == tmp]
        elif select == 'city':
            tmp_people = [tmp_people[i] for i in range(len(tmp_people)) if tmp_people[i][3] == tmp]
        elif select == 'phone':
            tmp_people = [tmp_people[i] for i in range(len(tmp_people)) if tmp_people[i][0] == tmp]
    return render_template("index.html", people=tmp_people)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_patient = {"phone_number": request.form.get('phone'), "name": request.form.get('name'),
                       "country": request.form.get('country'), "city": request.form.get('city'),
                       "date": request.form.get('birthday')}

        r = requests.post(URL + '/addPatient', new_patient)
        requests.put(URL + '/patient/' + new_patient['phone_number'] + '/symptoms',
                     data={'symptom': 'Zabolel',
                           'date': datetime.strftime(datetime.fromtimestamp(datetime.today().timestamp()).date(),
                                                     '%Y-%m-%d')})
        print(r.status_code)
        if r.status_code == 302:
            return render_template('add.html')
        else:
            return redirect(PROTOCOL + '://' + 'localhost' + ':8080')
    return render_template('add.html')


def age_from_date(date_of_birth):
    tmp_date = datetime.fromtimestamp(int(date_of_birth) / 1000).strftime('%Y-%m-%d')
    tmp_date = datetime.strptime(tmp_date, '%Y-%m-%d')
    today = date.today()
    return today.year - tmp_date.year - ((today.month, today.day) < (tmp_date.month, tmp_date.day))


@app.route("/chart/<tmp>/<time>", methods=['GET', 'POST'])
def chart(tmp, time):
    dict = {}
    tick_label = []
    if request.method == 'GET':
        ans = requests.get(URL + '/patients')
        tmp_people = ans.json()['patient']
        if tmp == 'Date':
            today = datetime.today()
            today_seconds = today.timestamp()
            tick_label.append(datetime.strftime(datetime.fromtimestamp(today_seconds).date(), '%Y-%m-%d'))
            for i in range(7):
                today_seconds = today_seconds - 86400
                tick_label.append(datetime.strftime(datetime.fromtimestamp(today_seconds).date(), '%Y-%m-%d'))
            tick_label.reverse()
            for n in tick_label:
                dict.update({n: 0})
        for p in tmp_people:  # in tmp_people
            if tmp == 'Date':
                if len(p['symptoms']) > 0:
                    if p['symptoms'][0]['date'] in tick_label:
                        dict[p['symptoms'][0]['date']] += 1
            if tmp == 'Country':
                if dict.get(p['country']) is None:
                    dict.update({p['country']: 1})
                    tick_label.append(p['country'])
                else:
                    dict[p['country']] += 1

            if tmp == 'City':
                if dict.get(p['city']) is None:
                    dict.update({p['city']: 1})
                    tick_label.append(p['city'])
                else:
                    dict[p['city']] += 1
            if tmp == 'Age':
                age = age_from_date(p['date_of_birth']['$date'])
                if dict.get(age) is None:
                    dict.update({age: 1})
                    tick_label.append(age)
                else:
                    dict[age] += 1
    left = range(len(dict))
    plt.bar(left, dict.values(), tick_label=tick_label, width=0.8, color=['red', 'green'])
    plt.ylabel('Кол-во')
    plt.xlabel(tmp)
    plt.title('Число заболевших')
    plt.tick_params(axis='both', which='major', labelsize=6)
    plt.savefig('./static/plot.png')
    plt.close()
    return send_file('./static/plot.png', mimetype='image/gif')


@app.route("/statistic", methods=['GET', 'POST'])
def statistic():
    tmp = 'Country'
    if request.method == 'GET':
        result = request.args
        for _, item in result.items():
            tmp = item
    return render_template("statistic.html", tmp=tmp, time=str(time.time()))


@app.route("/card/<phone_number>")
def card_patient(phone_number):
    patient = requests.get(URL + '/patient/' + phone_number)
    patient = patient.json()
    patient['date_of_birth']['$date'] = datetime.fromtimestamp(
        int((patient['date_of_birth']['$date'])) / 1000).strftime('%Y-%m-%d')
    return render_template("card.html", patient=patient)


@app.route("/card/<phone_number>/edit", methods=['GET', 'POST', 'DELETE'])
def edit_card(phone_number):
    if request.method == 'DELETE':
        p = requests.delete(URL+'/patient/'+phone_number)
        return Response(status=200)
    p = requests.get(URL + '/patient/' + phone_number)
    p = p.json()
    p['$date'] = datetime.fromtimestamp(
        int((p['date_of_birth']['$date'])) / 1000).strftime('%Y-%m-%d')
    if request.method == 'POST':
        new_card = {"phone_number": request.form.get('phone'), "name": request.form.get('name'),
                    "country": request.form.get('country'), "city": request.form.get('city')}
        new_card.update({'date': {'$date': request.form.get('birthday')}})
        # request to edit card ???
        p['phone_number'] = request.form.get('phone')
        p["name"] = request.form.get('name')
        p["country"] = request.form.get('country')
        p["city"] = request.form.get('city')
        p["date_of_birth"] = request.form.get('birthday')
        requests.post(URL + '/editPatient/' + phone_number, data=p)
        return redirect(PROTOCOL + '://' + 'localhost' + ':8080' + '/card/' + p['phone_number'])

    return render_template("edit_patient.html", patient=p)


@app.route("/card/<phone_number>/contacts", methods=['GET', 'POST'])
def contacts(phone_number):
    people = requests.get(URL + '/patients/').json()
    people = people['patient']
    p = requests.get(URL + '/patient/' + phone_number)
    p = p.json()
    contacts = p['contacts']
    names_of_contacts = []
    for contact in contacts:
        flag = True
        for person in people:
            print(person)
            if contact == person['phone_number']:
                names_of_contacts.append(person['name'])
                flag = False
        if flag == True:
            names_of_contacts.append('Contact undefined ' + contact)

    return render_template("contacts.html", contacts=names_of_contacts, phone_number=phone_number)


@app.route("/card/<phone_number>/contacts/<index>", methods=['GET', 'POST', 'DELETE'])
def contact_edit(phone_number, index):
    if request.method == 'DELETE':
        requests.delete(URL + '/patient/' + phone_number + '/contacts',
                  data={'index': index})
        return Response(status=200)
    value = request.form.get('phone')
    requests.post(URL + '/patient/' + phone_number + '/contacts', {'index': index, 'value': value})
    new_p = requests.get(URL + '/patient/' + phone_number)
    new_p = new_p.json()
    return render_template("edit_contacts.html", contact=new_p['contacts'][int(index)], phone_number=phone_number)


@app.route("/card/<phone_number>/contacts/add", methods=['GET', 'POST', 'PUT'])
def add_contact(phone_number):
    if request.method == 'POST':
        contact = {'contact': request.form.get('phone')}
        requests.put(URL + '/patient/' + phone_number + '/contacts', contact)
    return render_template("add_contact.html")


@app.route("/card/<phone_number>/diseases", methods=['GET', 'POST'])
def diseases(phone_number):
    diseases = requests.get(URL + '/patient/' + phone_number + '/diseases').json()
    return render_template('diseases.html', diseases=diseases, phone_number=phone_number)


@app.route("/card/<phone_number>/diseases/<index>", methods=['GET', 'POST', 'DELETE'])
def disease_edit(phone_number, index):
    if request.method == 'DELETE':
        requests.delete(URL + '/patient/' + phone_number + '/diseases',
                  data={'index': index})
        return Response(status=200)
    dis = request.form.get('disease')
    requests.post(URL + '/patient/' + phone_number + '/diseases',
                  {'index': index, 'value': request.form.get('disease')})
    return render_template("edit_disease.html", phone_number=phone_number, disease=request.form.get('disease'))


@app.route("/card/<phone_number>/diseases/add", methods=['GET', 'POST', "PUT"])
def add_disease(phone_number):
    if request.method == 'POST':
        disease = {'disease': request.form.get('disease')}
        requests.put(URL + '/patient/' + phone_number + '/diseases', disease)
    return render_template("add_disease.html", phone_number=phone_number)


@app.route("/card/<phone_number>/dynamic", methods=['GET', 'POST'])
def dynamic(phone_number):
    diseases = requests.get(URL + '/patient/' + phone_number + '/symptoms').json()
    return render_template('dynamic.html', symptoms=diseases['symptoms'], phone_number=phone_number)


@app.route("/card/<phone_number>/dynamic/<index>", methods=['GET', 'POST', 'DELETE'])
def symptom_edit(phone_number, index):
    if request.method == 'DELETE':
        requests.delete(URL + '/patient/' + phone_number + '/symptoms',
                  data={'index': index})
        return Response(status=200)
    if request.method == 'POST':
        requests.post(URL + '/patient/' + phone_number + '/symptoms',
                  json={'index': index, 'value': {'symptom': request.form.get('symptom'),
                                                  'date': request.form.get('date')}})
    old_symp = requests.get(URL + '/patient/' + phone_number + '/symptoms').json()
    old_symp = old_symp['symptoms'][int(index)]
    
    return render_template("edit_symptom.html", phone_number=phone_number, old_symp=old_symp, index = index)


@app.route("/card/<phone_number>/dynamic/add", methods=['GET', 'POST', "PUT"])
def add_symptom(phone_number):
    if request.method == 'POST':
        symptom = {'symptom': request.form.get('symptom'), 'date': request.form.get('date')}
        requests.put(URL + '/patient/' + phone_number + '/symptoms', symptom)
    return render_template("add_symptom.html", phone_number=phone_number)


if __name__ == "__main__":
    app.debug = True
    HOST = 'localhost'
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    app.run(port=8080, host=HOST)

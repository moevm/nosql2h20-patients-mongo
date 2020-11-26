from flask import Flask, render_template, send_file, request, redirect
import requests
import matplotlib.pyplot as plt
import os
import time

app = Flask(__name__)
#people = [{"phone_number": "4444", "name": "1231231", "country": "5555", "city": "1231231", "date_of_birth": {"$date": -27080352000000}, "contacts": ["89516491048"], "diseases": [], "symptoms": [{"symptom": "123", "date": "2222-02-12T11:11"}]}, {"phone_number": "89516491048", "name": "Dmitry", "country": "Беларусь", "city": "Baranovichi", "date_of_birth": {"$date": 958003200000}, "contacts": ["12312", "DIMA"], "diseases": ["loh", {"symptom": "DIMADIMADIMA", "date": "11-11-4231"}, "lays s krabom"], "symptoms": [{"symptom": "golova bobo", "date": "2020-11-05"}, {"symptom": "DIMADIMADIMA1", "date": "11-11-4231"}, {"symptom": "31312", "date": "1111-03-12T12:30"}, {"symptom": "qweqw", "date": "2312-03-1212:22"}]}, {"phone_number": "12312", "name": "1231231", "country": "112312", "city": "1231231", "date_of_birth": {"$date": -27080352000000}, "contacts": [], "diseases": [], "symptoms": [{"symptom": "123", "date": "2222-02-12T11:11"}]}]
@app.route("/", methods=['GET','POST'])
def init():
    select = 'none'
    tmp_people = []
    people = requests.get('http://localhost:5000/patients')
    people = people.json()
    print(len(people['patient']))
    for i in range(len(people['patient'])):
        tmp_people.append([
                            people['patient'][i]['phone_number'], people['patient'][i]['name'],
                            people['patient'][i]['country'], people['patient'][i]['city'],
                            people['patient'][i]['date_of_birth']['$date']
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
    return render_template("index.html", people = tmp_people)



@app.route("/add", methods=['GET','POST'])
def add():
    if request.method == 'POST':
        new_patient = {"phone_number":request.form.get('phone'), "name":request.form.get('name'),
                        "country":request.form.get('country'), "city":request.form.get('city'),
                        "date":request.form.get('birthday')}

        requests.post('http://localhost:5000/addPatient', new_patient)
    return render_template("add.html")

@app.route("/chart/<tmp>/<time>", methods=['GET','POST'])
def chart(tmp, time):
    dict = {}
    left = 0
    tick_label =[]
    if request.method == 'GET':
        ans = requests.get('http://localhost:5000/patients')
        tmp_people = ans.json()['patient']
        for p in tmp_people: #in tmp_people
            if tmp == 'Country':
                if dict.get(p['country']) == None:
                    dict.update({p['country']: 1})
                    tick_label.append(p['country'])
                else:
                    dict[p['country']] += 1

            if tmp == 'City':
                if dict.get(p['city']) == None:
                    dict.update({p['city']: 1})
                    tick_label.append(p['city'])
                else:
                    dict[p['city']] += 1
    left = range(len(dict))
    print(dict.keys(), dict.values(), tick_label, len(tick_label))
    plt.bar(left, dict.values(), tick_label=tick_label, width=0.8, color=['red', 'green'])
    plt.ylabel('Кол-во')
    plt.xlabel(tmp)
    plt.title('Число заболевших')
    plt.savefig('D:/bd/static/plot.png')
    plt.close()
    return send_file('D:/bd/static/plot.png', mimetype='image/gif')

@app.route("/statistic", methods=['GET','POST'])
def statistic():
    tmp = 'Country'
    if request.method == 'GET':
        result = request.args
        for _, item in result.items():
            tmp = item
    new_time = time.time()
    return render_template("statistic.html", tmp = tmp, time = str(time.time()))

@app.route("/card/<phone_number>")
def card_patient(phone_number):
    patient = requests.get('http://localhost:5000/patient/'+phone_number)
    patient = patient.json()
    return render_template("card.html", patient = patient)

@app.route("/card/<phone_number>/edit", methods=['GET','POST'])
def edit_card(phone_number):
    p = requests.get('http://localhost:5000/patient/'+phone_number)
    old_card = p
    p = p.json()

    if request.method == 'POST':
        new_card = {"phone_number":request.form.get('phone'), "name":request.form.get('name'),
                        "country":request.form.get('country'), "city":request.form.get('city')}
        new_card.update({'date':{'$date' : request.form.get('birthday')}})

        #request to edit card ???


        p['phone_number'] = request.form.get('phone')
        p["name"] =request.form.get('name')
        p["country"] = request.form.get('country')
        p["city"] = request.form.get('city')
        p["date_of_birth"]["$date"] = request.form.get('birthday')
        return redirect("http://localhost:5000", code=302)

    return render_template("edit_patient.html", patient = old_card)

@app.route("/card/<phone_number>/contacts", methods=['GET','POST'])
def contacts(phone_number):
    people = requests.get('http://localhost:5000/patients/').json()
    people = people['patient']
    p = requests.get('http://localhost:5000/patient/'+phone_number)
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

    return render_template("contacts.html", contacts = names_of_contacts, phone_number = phone_number)

@app.route("/card/<phone_number>/contacts/<index>", methods=['GET','POST'])
def contact_edit(phone_number, index):
    new_p = None
    p = requests.get('http://localhost:5000/patients/' + phone_number)
    value = request.form.get('phone')
    requests.post('http://localhost:5000/patient/' + phone_number + '/contacts', {'index':index, 'value': value})
    new_p = requests.get('http://localhost:5000/patient/' + phone_number)
    new_p = new_p.json()
    return render_template("edit_contacts.html", contact = new_p['contacts'][int(index)], phone_number = phone_number)

@app.route("/card/<phone_number>/contacts/add", methods=['GET','POST', 'PUT'])
def add_contact(phone_number):
    if request.method == 'POST':
        contact = {'contact':request.form.get('phone')}
        requests.put('http://localhost:5000/patient/'+ phone_number + '/contacts', contact)
    return render_template("add_contact.html")

@app.route("/card/<phone_number>/diseases", methods=['GET','POST'])
def diseases(phone_number):
    diseases = requests.get('http://localhost:5000/patient/' + phone_number + '/diseases').json()
    return render_template('diseases.html', diseases = diseases, phone_number = phone_number)

@app.route("/card/<phone_number>/diseases/<index>", methods=['GET','POST'])
def disease_edit(phone_number, index):
    requests.post('http://localhost:5000/patient/'+ phone_number + '/diseases', {'index':index, 'value':request.form.get('disease')})
    return render_template("edit_disease.html",  phone_number = phone_number)

@app.route("/card/<phone_number>/diseases/add", methods=['GET','POST', "PUT"])
def add_disease(phone_number):
    if request.method == 'POST':
        disease = {'disease':request.form.get('disease')}
        requests.put('http://localhost:5000/patient/'+ phone_number + '/diseases', disease)
    return render_template("edit_disease.html",  phone_number = phone_number)

@app.route("/card/<phone_number>/dynamic", methods=['GET','POST'])
def dynamic(phone_number):
    diseases = requests.get('http://localhost:5000/patient/' + phone_number + '/symptoms').json()
    return render_template('dynamic.html', symptoms = diseases['symptoms'], phone_number = phone_number)

@app.route("/card/<phone_number>/dynamic/<index>", methods=['GET','POST'])
def symptom_edit(phone_number, index):
    old_symp = requests.get('http://localhost:5000/patient/' + phone_number + '/symptoms').json()
    old_symp = old_symp['symptoms'][int(index)]
    requests.post('http://localhost:5000/patient/'+ phone_number + '/symptoms',
                json={'index':index, 'value':{'symptom':request.form.get('symptom'),
                'date':request.form.get('date')}})
    return render_template("edit_symptom.html",  phone_number = phone_number, old_symp = old_symp)

@app.route("/card/<phone_number>/dynamic/add", methods=['GET','POST', "PUT"])
def add_symptom(phone_number):
    if request.method == 'POST':
        symptom = {'symptom':request.form.get('symptom'), 'date':request.form.get('date')}
        requests.put('http://localhost:5000/patient/'+ phone_number + '/symptoms', symptom)
    return render_template("add_symptom.html",  phone_number = phone_number)
if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)

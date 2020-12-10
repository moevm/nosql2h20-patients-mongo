from flask import Flask

from api import *
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

app.url_map.strict_slashes = False

app.register_blueprint(patients)
app.register_blueprint(patients_add)

app.register_blueprint(patient)
app.register_blueprint(patient_delete)

app.register_blueprint(patient_contacts)
app.register_blueprint(patient_diseases)
app.register_blueprint(patient_symptoms)

app.register_blueprint(patient_contacts_put)
app.register_blueprint(patient_diseases_put)
app.register_blueprint(patient_symptoms_put)

app.register_blueprint(patient_contacts_delete)
app.register_blueprint(patient_diseases_delete)
app.register_blueprint(patient_symptoms_delete)

app.register_blueprint(patient_symptoms_edit)
app.register_blueprint(patient_diseases_edit)
app.register_blueprint(patient_contacts_edit)
app.register_blueprint(patients_edit)
app.register_blueprint(export)
app.register_blueprint(imprt)

if __name__ == '__main__':
    HOST = 'localhost'
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    app.run(host=HOST)

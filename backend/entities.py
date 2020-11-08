class Patient(object):
    def __init__(self, phone_number, name, country, city, date_of_birth,
                 contacts=None, diseases=None, symptoms=None):
        """

        :rtype: object
        """
        if symptoms is None:
            symptoms = []
        if contacts is None:
            contacts = []
        if diseases is None:
            diseases = []
        self.phone_number = phone_number
        self.name = name
        self.country = country
        self.city = city
        self.date_of_birth = date_of_birth
        self.contacts = contacts
        self.diseases = diseases
        self.symptoms = symptoms


class Disease(object):
    def __init__(self, symptom, date):
        self.symptom = symptom
        self.date = date

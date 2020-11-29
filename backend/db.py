import sys

from pymongo import MongoClient

HOST = 'db'
PORT = 27017
client = MongoClient(host=HOST, port=PORT)
db = client['patients']
collection = db['patient']

import sys

from pymongo import MongoClient

HOST = sys.argv[1]
PORT = 27017
client = MongoClient(host=HOST, port=PORT)
db = client['patients']
collection = db['patient']

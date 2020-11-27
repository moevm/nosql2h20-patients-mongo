import sys

from pymongo import MongoClient

HOST = 'localhost'
if len(sys.argv) > 1:
    HOST = sys.argv[1]
PORT = 27017
client = MongoClient(host=HOST, port=PORT)
db = client['patients']
collection = db['patient']

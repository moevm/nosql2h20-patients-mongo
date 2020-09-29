from pymongo import *
from flask import Flask, request
from flask import jsonify
import json
from bson import json_util

app = Flask(__name__)

client = MongoClient('db', 27017)
db = client['patients']
collection = db['patient']
post = {"author": "Dima",
         "text": "Test pymongo",
         "tags": ["mongodb", "python", "pymongo"]}
collection.insert_one(post)

@app.route('/')
def hello_world():
    docs_list = list(collection.find())
    return json.dumps(docs_list, default=json_util.default)

@app.route('/add')
def add_to_db():
    obj = {"author":request.args['author'], "text": request.args['text'],
         "tags": request.args['tags'].split(",")}
    docs_list = list(collection.find())
    return json.dumps(docs_list, default=json_util.default)

@app.route('/del')
def del_from_db():
    obj = request.args['author']
    myquery = {"author": obj}
    collection.delete_one(myquery)
    docs_list = list(collection.find())
    return json.dumps(docs_list, default=json_util.default)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

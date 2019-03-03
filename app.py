from flask import Flask
from flask import request
import Main as M
import json
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'

@app.route('/update/<int:id>', methods=['GET'])
def create_update_id(id):
    return M.create_update_id(id)

@app.route('/delete/<int:id>', methods=['GET'])
def delete_id(id):
    return M.delete_id(id)

@app.route('/check/<int:id>', methods=['GET'])
def check_by_id(id):
    return M.check_post(id)

@app.route('/check/request', methods=['GET'])
def check_by_req():
    data =  request.get_json()
    return M.check_post(data)

@app.route('/check/all', methods=['GET'])
def check_all():
    return M.check_all()


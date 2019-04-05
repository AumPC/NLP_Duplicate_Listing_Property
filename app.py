from flask import Flask
from flask import request
import src.Main as M
app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/clone', method=['POST'])
def clone():
    return M.clone()


@app.route('/update/<int:post_id>', methods=['POST'])
def update_id(post_id):
    return M.update(post_id)


@app.route('/check/<int:post_id>', methods=['POST'])
def check_by_id(post_id):
    return M.check_post(post_id)


@app.route('/check/request', methods=['POST'])
def check_by_req():
    data = request.get_json()
    return M.check_post(data)


@app.route('/check/all', methods=['POST'])
def check_all():
    return M.check_all()

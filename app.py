from flask import Flask
from flask import request
import src.Main as M
app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return "hello world"


@app.route('/clone', methods=['POST'])
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
    if type(data) != dict:
        return 'ERROR: invalid data type', 401
    require_fields = ['id', 'condo_project_id', 'title', 'price', 'size', 'tower', 'floor', 'bedroom', 'bathroom', 'detail']
    for field in require_fields:
        if field not in data:
            return f'ERROR: {field} is not found', 401
    return M.check_post(data)


@app.route('/check/all', methods=['POST'])
def check_all():
    return M.check_all()


@app.route('/parameter', methods=['GET'])
def get_parameter():
    return M.get_parameter()


@app.route('/parameter', methods=['POST'])
def set_parameter():
    data = request.get_json()
    if type(data) != dict:
        return 'ERROR: invalid data type', 401
    return M.set_parameter(data)


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)

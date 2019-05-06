from flask import Flask
from flask import request
import src.Main as Main
app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return "hello world"


@app.route('/clone', methods=['POST'])
def clone():
    return Main.clone()


@app.route('/update/<int:post_id>', methods=['POST'])
def update_id(post_id):
    return Main.update(post_id)


@app.route('/check/<int:post_id>', methods=['POST'])
def check_by_id(post_id):
    return Main.check_post(post_id)


@app.route('/check/request', methods=['POST'])
def check_by_req():
    data = request.get_json()
    if type(data) != dict:
        return 'ERROR: invalid data type', 401
    require_fields = ['id', 'project', 'title', 'price', 'size', 'tower', 'floor', 'bedroom', 'bathroom', 'detail']
    for field in data:
        if field not in require_fields:
            return f'ERROR: {field} is not found', 401
        if field == 'id':
            if not isinstance(data[field], int):
                return f'ERROR: invalid {field} type: expect int', 401
        elif field == 'project':
            if not (isinstance(data[field], int) or data[field] is None):
                return f'ERROR: invalid {field} type: expect int or None', 401
        elif field in ['title', 'tower', 'floor', 'bedroom', 'bathroom', 'detail']:
            if not isinstance(data[field], str):
                try:
                    data[field] = str(data[field])
                except ValueError:
                    return f'ERROR: invalid {field} type: expect string', 401
        elif field == 'size':
            if not (isinstance(data[field], float) or isinstance(data[field], int)):
                try:
                    data[field] = float(data[field])
                except ValueError:
                    return f'ERROR: invalid {field} type: expect int or float', 401
                if data[field] < 0:
                    return f'ERROR: invalid {field} range', 401
        elif field == 'price':
            if isinstance(data[field], list):
                if len(data[field]) != 2:
                    return f'ERROR: invalid {field} format: must have length 2', 401
                for index in [0, 1]:
                    if not (isinstance(data[field][index], float) or isinstance(data[field][index], int)):
                        try:
                            data[field][index] = float(data[field][index])
                        except ValueError:
                            return f"ERROR: invalid {field}'s element type: expect int or float", 401
                if not 0 <= data[field][0] <= data[field][1]:
                    return f'ERROR: invalid {field} range', 401
            elif data[field] is not None:
                return f'ERROR: invalid {field} type: expect list or None', 401
    return Main.check_post(data)


@app.route('/check/all', methods=['POST'])
def check_all():
    return Main.check_all()


@app.route('/parameter', methods=['GET'])
def get_parameter():
    return Main.get_parameter()


@app.route('/parameter', methods=['POST'])
def set_parameter():
    data = request.get_json()
    if type(data) != dict:
        return 'ERROR: invalid data type', 401
    return Main.set_parameter(data)


@app.route('/parameter/reset', methods=['POST'])
def reset_parameter():
    return Main.reset_parameter()


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)

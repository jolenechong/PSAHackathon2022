from flask import Flask, jsonify, request, make_response
import shelve
import os
import datetime
from functools import total_ordering
from math import floor
from pprint import pprint
from AI_Model.data_model import DataModel
import numpy
from tensorflow import keras

# start flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_secret')

from flask_cors import CORS
cors = CORS(app)

# TODO: configure/initialise db with all "tables"

# configure routes
with app.app_context():
    from auth import auth
    # from api import api
    
app.register_blueprint(auth, url_prefix='/auth')

@app.route("/api/test", methods=['GET'])
def test():
    return jsonify({'message': 'hEllo yES woRking :")'})

@app.route('/api/predict', methods=['POST'])
def predict_route_delays():
    def read_input():
        str = input() #take in input from the front end here
        m = DataModel()
        m.from_strdate(str)
        return m.to_row()

    # load saved model 
    model = keras.models.load_model('model')

    def predict(data):
        return model.predict(data, verbose=1)
    row_input = read_input()

    # initialise empty array to store data
    prediction_array = []
    row_input.pop(5)

    # prints prediction of delay for all 32 roads
    for i in range(32):
                row_input[4] = i + 1
                mdata = DataModel()
                mdata.from_row(row_input)
                norm_row = mdata.to_row_normalized()
                norm_row.pop(5)
                prediction_array.append(norm_row)
    prediction_array = numpy.array(prediction_array)

    # predict delay & store in dictionary format
    res = predict(prediction_array)
    predicted_delays = {}

    # print(res), max delay is 30 mins
    for i in range(32):
        predicted_delays["Road " + str(i + 1)] = max(0, floor(res[i][0] * 30))
        
    return jsonify(predicted_delays) #returns dictionary of predicted delays at all 32 roads

    
# app.register_blueprint(api, url_prefix='/api')

# configure warnings
if os.environ.get('JWT_secret') is None:
    print('->> JWT_secret not set in environment!!')
if os.environ.get('FLASK_secret') is None:
    print('->> FLASK_secret not set in environment!!')

print('hereee', os.environ.get('JWT_secret'))

# UPLOAD_FOLDER = 'static/assets/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
   
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3001)

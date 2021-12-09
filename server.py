from flask import Flask, render_template, request, Response, url_for, jsonify

import json
import jsonpickle

from task import process_image_text

import io
import base64
from PIL import Image

import os
from werkzeug.utils import secure_filename
from tempfile import TemporaryFile
import uuid

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/result', methods=['POST'])
def send_result():
    image_string = request.data
    if(image_string != ""):
        image = io.BytesIO(base64.b64decode(image_string))
        img = Image.open(image)

        new_file = img.save("processed_image"+str(uuid.uuid4())+".jpg")
        

        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_file))


        #Encode response using jsonpickle
        response_pickled = jsonpickle.encode({'result':'task complete'})
    else:
        #Encode response using jsonpickle
        response_pickled = jsonpickle.encode({'result':'task failed'})

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/submit', methods=['POST'])
def submit_job():

    request_data = request.data

    #Convert data to json
    data_obj = json.loads(request_data)

    #Get parameters and send it over to queue job
    image_string = data_obj['image_string']

    jobs = data_obj['jobs']
    for job in jobs:
        text = job['text']
        coords = job['coords']
        position = job['position']
        color = job['color']
        text_size = job['text_size']
        font = job['font']

        result = process_image_text.delay(image_string,text,coords,position,color,text_size,font)
        print("result-id:",result)

    #Encode response using jsonpickle
    response_pickled = jsonpickle.encode({'result':'tasks have been sent'})

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/')
def hello():
    return render_template('main.html')

if __name__ == '__main__':
    app.run()
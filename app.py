from flask import Flask, flash, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os
import json
import uuid

load_dotenv()

URI = os.getenv("MONGO_URI")

cluster = MongoClient(URI)
db = cluster["imagesDb"]
collection = db["images"]

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    documents = collection.find()
    print(documents)
    return render_template('index.html', documents=documents)


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/insert', methods=['GET', 'POST'])
def insert():

    if request.method == 'POST':

        name = request.form['owner'].lower()
        file = request.files['file']

        if file.filename == '':
            return redirect('/')

        filename = secure_filename(file.filename)
        filename = my_custom_name(filename)

        if file and is_allowed(filename):

            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            collection.insert_one({'owner': name, "filename": filename})

    return redirect('/')


@app.route('/delete/<id>')
def delete(id):
    document = collection.find_one({"_id": ObjectId(id)})
    filename = document["filename"]

    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], str(filename))):
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], str(filename)))
    collection.delete_one({"_id": ObjectId(id)})

    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        photographer = request.form['search']
        photographer = photographer.lower()
        documents = collection.find({'owner': photographer})
        return render_template('index.html', documents=documents)
    except:
        print('Invalid Data')


def my_custom_name(filename):
    suffix = filename.split(".")[0] + str(uuid.uuid4())
    prefix = filename.split(".")[1]
    return suffix + "." + prefix

def is_allowed(filename):
    return filename.split(".")[1] in ALLOWED_EXTENSIONS

if(__name__ == "__main__"):
    app.run(debug=True)

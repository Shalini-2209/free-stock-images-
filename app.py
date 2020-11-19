from flask import Flask, flash, render_template,request,redirect,url_for
import pymongo
from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv
from bson.objectid import ObjectId

app = Flask(__name__)
load_dotenv()

URI = os.getenv("MONGO_URI")


cluster = MongoClient(URI)
db = cluster.drive
img_collection = db.images


@app.route('/')
def home():
    documents = img_collection.find()
    return render_template('index.html', documents = documents)

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/insert', methods = ['GET', 'POST'])
def insert():
  
    if request.method == 'POST':
        file = request.form['img']
        name = request.form['owner'].lower()

        post = {'img_src': file, 'owner':name}
       
        img_collection.insert_one(post)
        return  redirect('/')
        
    return redirect('/upload')   


@app.route('/delete/<id>')
def delete(id):
    try:
        img_collection.delete_one({"_id":ObjectId(id)})
        return redirect('/')   
    except:
        redirect('/upload')   


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        photographer = request.form['search']
        photographer = photographer.lower()
        documents = img_collection.find({'owner': photographer})
        print(documents)
        return render_template('index.html', documents = documents)

    except:
        print('Invalid Data')

if(__name__ == "__main__"):
    app.run(debug=True)
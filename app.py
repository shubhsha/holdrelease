from bson.json_util import dumps, loads
#import pandas
from pymongo import MongoClient
from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import json
import requests
ordNum = ""
instance = ""

app = Flask(__name__)

title = "QA Hold Release Support Tool"
heading = "Hold list on :- "

#client = MongoClient("mongodb://127.0.0.1:27017") #host uri
#db = client.shubham #Select the database
#todos = db.shubhamDb #Select the collection name

def connect(instance):
    #uri = "mongodb://127.0.0.1:27017"
    uri3 = "mongodb://opl_ro:By3-roUs6@mgcf-oplts3-npd1-1:28090/?connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1&3t.uriVersion=3&3t.connection.name=New+OPL+Ts3"
    uri1 = "mongodb://opllt_ro:Oplltro_420@mgcf-opl-lt2-2:28090/?connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1&3t.uriVersion=3&3t.connection.name=OPL+Ts1"

    if(instance == "TS1"):
        client = MongoClient(uri1) #host uri
        print("connected to TS1")
    else:
        client = MongoClient(uri3)
        print("connected to TS3")

        #db = client.opldb #Select the database
        #todos = db.oplOrderHolds #Select the collection name

    return(client)


def redirect_url():
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')



@app.route("/")
#@app.route("/list")
def lists ():
    #Display the all Tasks
#    todos_l = todos.find()
    a1="active"
    return render_template('index.html',a1=a1,t=title,h=heading)



@app.route("/releaseFlag")
def releaseFlag ():
    #Done-or-not ICON
    id=request.values.get("_id")
    task=todos.find({"_id":ObjectId(id)})
    if(task[0]["releaseFlag"]=="Y"):
        todos.update({"_id":ObjectId(id)}, {"$set": {"releaseFlag":"N"}})
    else:
        todos.update({"_id":ObjectId(id)}, {"$set": {"releaseFlag":"Y"}})
    redir=redirect_url()
    return redirect(redir)


@app.route("/remove")
def remove ():
    #running post request for Hold Release
    key=request.values.get("_id")
    #holdNm=request.values.get("holdNm")
    #print("holdNm is: -",holdNm)
    print(key)
    print(len(key))

    x = len(key)-10
    print(x)
    lnRefNum = key[x:x+9]
    print("lnRefNum",lnRefNum)
    if(lnRefNum == "Undefined"):
        print("Header Hold")
    else:
        x = len(key)-11
        print(x)
        lnRefNum = key[x:x+9]
        print(lnRefNum)
    print("Final Line: -",lnRefNum)
    aList = list(key)
    doc = key.split(',')
    holdId = doc[2]
    holdId = holdId.strip()
    print("holdId",holdId)
    holdNm = doc[1]
    holdNm = holdNm.strip()
    y = len(holdNm)
    print(y)

    holdNm = holdNm[1:y-1]
    print(holdNm)

    print("holdNm",holdNm)
    releaseFlag=aList[2]
    print("Release Flag",releaseFlag)
    if (releaseFlag == "Y"):
        #return redirect("/HoldReleased.html")
        return render_template('HoldReleased.html',t=title,h=heading)


    if ("CMFS-Credit Check Pending" in holdNm): ##CMFS hold release
        print("CMFS Hold Release")
        global ordNum
        #a_file = open("C:\Python\qaSupport\cmfs.json", "r")
        a_file = open("cmfsjsonfortool.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        for test in json_object["HoldRequest"]["requestPayload"]:
            test['sourceOrderID'] = ordNum

        response = requests.post('https://oplservice-hold-ts3.cisco.com/processHolds', json=json_object, auth = ('ordermgmt.gen', 'cisco123'))

        a_file = open("cmfsjsonfortool.json", "w")
        json.dump(json_object, a_file, indent = 2)
        a_file.close()
        return render_template('HoldReleased.html',t=title,h=heading)

    elif ((lnRefNum == "Undefined")):  ##header hold release
        print("Header Hold Release")
        #a_file = open("C:\Python\qaSupport\header.json", "r")
        a_file = open("headerjsonfortool.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        for test in json_object["HoldRequest"]["requestPayload"]:
            test['sourceOrderID'] = ordNum
            test['holdID'] = holdId
            test['holdName'] = holdNm

        response = requests.post('https://oplservice-hold-ts3.cisco.com/processHolds', json=json_object, auth = ('ordermgmt.gen', 'cisco123'))

        #a_file = open("C:\Python\qaSupport\header.json", "w")
        a_file = open("headerjsonfortool.json", "w")
        json.dump(json_object, a_file, indent = 2)
        a_file.close()
        return render_template('HoldReleased.html',t=title,h=heading)

    else: ##line hold release
        print("Line Hold Release")
        a_file = open("linejsonfortool.json", "r")
        #a_file = open("C:\Python\qaSupport\line.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        for test in json_object["HoldRequest"]["requestPayload"]:
            test['sourceOrderID'] = ordNum
            test['sourceLineID'] = lnRefNum
            test['holdID'] = holdId
            test['holdName'] = holdNm

        response = requests.post('https://oplservice-hold-ts3.cisco.com/processHolds', json=json_object, auth = ('ordermgmt.gen', 'cisco123'))

        a_file = open("linejsonfortool.json", "w")
        json.dump(json_object, a_file, indent = 2)
        a_file.close()
        return render_template('HoldReleased.html',t=title,h=heading)


@app.route("/search", methods=['GET'])
def search():
    #Searching a Task with various references
    key=request.values.get("key")
    refer=request.values.get("refer")
    global ordNum
    global instance
    client = connect(refer)
    db = client.opldb #Select the database
    todos = db.oplOrderHolds #Select the collection name
    ordNum = key
    print(ordNum)
    print("here")
    todos_l = todos.find({"ordNum":ordNum})
    print(todos_l)
    client.close
    heading = "Hold list on Order:-"+ ordNum
    return render_template('searchlist.html',todos=todos_l,t=title,h=heading)
    return(ordNum)
    return(instance)


if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=8080)
    app.run()

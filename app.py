import sqlite3
from flask import Flask,render_template
from flask import request
import json
import time
import requests

PORT=4400
URL='http://localhost:5555/health/gethealthdata'
app=Flask(__name__)
@app.route("/report",methods=['POST'])
def report():
    incoming_report = request.get_json()
    username=incoming_report["USER_NAME"]
    time_epoch=incoming_report["epoch_time"]
    server_name=incoming_report["SERVER_NAME"]
    bytes_write=incoming_report["bytes_write"]
    bytes_sent=incoming_report["bytes_sent"]
    bytes_recv=incoming_report["bytes_recv"]
    bytes_read = incoming_report["bytes_read"]
    conn=sqlite3.connect("Health.db")
    response_message={"message":"Generating Health Report"}
    
    try:
        conn.execute(f"create table if not exists {username}_{server_name} (HEALTH_ID integer primary key AUTOINCREMENT,Time_Epoch float,Bytes_Write float,Bytes_Sent float, Bytes_Recv float,Bytes_Read float);")
        
        conn.execute(f'insert into {username}_{server_name} (Time_Epoch,Bytes_Write,Bytes_Sent,Bytes_Recv,Bytes_Read) values {time_epoch,bytes_write,bytes_sent,bytes_recv, bytes_read}')
        return response_message
    except:
        return "Generation Failed"

    finally:
        try:
            conn.commit()
        except:
            "DB commit failed"  


@app.route("/Display",methods=['POST'])
def display():
    object=request.json
    username=object["Username"]
    servername=object["Servername"]
    conn=sqlite3.connect("Health.db")
    # health_dict={'Health_id':[],'Epoch_Time':[],'bytes_write':[],'bytes_sent':[],'CPU_Usage_Percent':[],'CPU_Time':[], "Bytes_Read":[]} 
    
    try:
        cur=conn.cursor()
        cur.execute(f" select * from {username}_{servername} order by HEALTH_ID")
        health_list=[] 
        for row in cur:
               
            tuple1=row[1:]
            tuple2=('Epoch_Time','Bytes_Write','Bytes_Sent','Bytes_Recv','Bytes_Read')
            health_dict=dict(zip(tuple2,tuple1))
            health_list.append(health_dict)
    except Exception as e:
        return {"Error":str(e)}       
    finally:
        try:
            conn.commit()
        except:
            return "DB commit failed"
    health=json.dumps(health_list)
    return health

if __name__ ==("__main__"):
    print("Emitter flask server is running...")
    print(f"listening at port {PORT}...")
    app.run(host='0.0.0.0',debug=True,port=PORT)
    

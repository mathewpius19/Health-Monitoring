import sqlite3
from flask import Flask,render_template
from flask import request
import json
import time
import requests
import pandas as pd 
import numpy as np
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense, LSTM
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

PORT=4400
URL='http://localhost:5555/health/gethealthdata'
app=Flask(__name__)
@app.route("/report",methods=['POST'])
def report():
    incoming_report = request.get_json()
    username=incoming_report["USER_NAME"]
    time_epoch=incoming_report["epoch_time"]
    server_name=incoming_report["SERVER_NAME"]
    bytes_read = incoming_report["bytes_read"]
    bytes_write = incoming_report["bytes_write"]
    bytes_sent = incoming_report["bytes_sent"]
    bytes_recv = incoming_report["bytes_recv"]
    conn=sqlite3.connect("Health.db")
    response_message={"message":"Generating Health Report"}
    
    try:
        conn.execute(f"create table if not exists {username}_{server_name} (HEALTH_ID integer primary key AUTOINCREMENT,Time_Epoch float,Bytes_Read float, Bytes_Write float, Bytes_Sent float, Bytes_Recv float);")
        
        conn.execute(f'insert into {username}_{server_name} (Time_Epoch,Bytes_Read, Bytes_Write, Bytes_Sent, Bytes_Recv) values {time_epoch, bytes_read, bytes_write, bytes_sent, bytes_recv}')
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
    try:
        cur=conn.cursor()
        sqlquery = (f"SELECT COUNT(*) FROM {username}_{servername}")
        cur.execute(sqlquery)
        res = cur.fetchall()
        for row in res:
            x = (row[0]) 
        if x > 50:
            print("Enough Rows")
            if x> 800:
                cur.execute(f"DELETE FROM {username}_{servername} WHERE HEALTH_ID IN (SELECT HEALTH_ID FROM TEST ORDER BY HEALTH_ID ASC LIMIT 500)")
                h_dict = prediction(username,servername, conn)

            else:
                h_dict = prediction(username,servername, conn)   
            
        else:
            return "Not Enough Data for Prediction"
    except Exception as e:
        return {"Error":str(e)}       
    finally:
        try:
            conn.commit()
        except:
            return "DB commit failed"
    health=json.dumps(h_dict)
    return health



def prediction(un, sn, conn):
    sq = (f"SELECT * FROM {un}_{sn} ORDER BY HEALTH_ID ASC")
    health_list = []
    health_dict={'Epoch_Time':[], "Bytes_Read":[], "Bytes_Write" : [], "Bytes_Sent" : [], "Bytes_Recv" : [], "P_Read": [], "P_Write": [], "P_Sent": [], "P_Recv": []} 
    df = pd.read_sql_query(sq,conn)
    X = df[['Time_Epoch']]
    y = df[['Bytes_Read','Bytes_Write', 'Bytes_Sent', 'Bytes_Recv']]
    X = X.values
    X = X.reshape(X.shape[0], X.shape[1], 1)
    in_dim = (X.shape[1], X.shape[2])
    out_dim = y.shape[1]
    xtrain, xtest, ytrain, ytest=train_test_split( X, y, test_size=0.20,shuffle = False)
    model = Sequential()
    model.add(LSTM(64, input_shape=in_dim, activation="relu", dropout= 0.2))
    model.add(Dense(out_dim))
    model.compile(loss="mse", optimizer="adam") 
    
    model.fit(xtrain, ytrain, batch_size=4, epochs=100, verbose=0)
  
    ypred = model.predict(xtest) #arr [[], [], []]
    j = (ytest.index.values)
    epoch_list = []
    for x in j:
        epoch_list.append(df.at[x, 'Time_Epoch'])
    epoch_list = np.array(epoch_list)
    ytest_np = ytest.to_numpy()
    test_vals = np.append(ytest_np,epoch_list[:,None],axis=1)
    for val in ypred:
        health_dict['P_Read'].append((val[0]).item())
        health_dict['P_Write'].append((val[1]).item())
        health_dict['P_Sent'].append((val[2]).item())
        health_dict['P_Recv'].append((val[3]).item())
    for row in test_vals:
        health_dict['Epoch_Time'].append((row[4]))
        health_dict["Bytes_Read"].append((row[0]).item())
        health_dict["Bytes_Write"].append((row[1]).item())
        health_dict["Bytes_Sent"].append((row[2]).item())
        health_dict["Bytes_Recv"].append((row[3]).item())
    health_list.append(health_dict)
    return health_list




if __name__ ==("__main__"):
    print("Emitter flask server is running...")
    print(f"listening at port {PORT}...")
    app.run(host='0.0.0.0',debug=True,port=PORT)
    

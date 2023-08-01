import sys
import os

import boto3

#import random

from datetime import date, timedelta
import time

import numpy as np
import math
import pandas as pd

from pandas_datareader import data as pdr
import yfinance as yf
import ast

from concurrent.futures import ThreadPoolExecutor
import http
import json
from flask import Flask, render_template, request,redirect,url_for, jsonify
from ec2 import aws_ec2

user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/pujariakshayk/Data-Science &&
cd Data-Science
sudo apt install --yes python3-pip &&
pip install -r requirements.txt
'''
app=Flask(__name__)

def RandomHandler():
  
    yf.pdr_override()

    today = date.today()
    decadeAgo = today - timedelta(days=3652)

    data = pdr.get_data_yahoo('NFLX', start=decadeAgo, end=today).reset_index()
   
    data["Date"] = data["Date"].apply(lambda x: pd.Timestamp(x).date().strftime('%m/%d/%Y'))

    data['Buy']=0
    data['Sell']=0
    
    for i in range(len(data)):
     
        realbody=math.fabs(data.Open[i]-data.Close[i])
        bodyprojection=0.1*math.fabs(data.Close[i]-data.Open[i])

        if data.High[i] >= data.Close[i] and data.High[i]-bodyprojection <= data.Close[i] and data.Close[i] > data.Open[i] and data.Open[i] > data.Low[i] and data.Open[i]-data.Low[i] > realbody:
            data.at[data.index[i], 'Buy'] = 1
           
        if data.High[i] > data.Close[i] and data.High[i]-data.Close[i] > realbody and data.Close[i] > data.Open[i] and data.Open[i] >= data.Low[i] and data.Open[i] <= data.Low[i]+bodyprojection:
            data.at[data.index[i], 'Buy'] = 1
            
        if data.High[i] >= data.Open[i] and data.High[i]-bodyprojection <= data.Open[i] and data.Open[i] > data.Close[i] and data.Close[i] > data.Low[i] and data.Close[i]-data.Low[i] > realbody:
            data.at[data.index[i], 'Sell'] = 1
            
        if data.High[i] > data.Open[i] and data.High[i]-data.Open[i] > realbody and data.Open[i] > data.Close[i] and data.Close[i] >= data.Low[i] and data.Close[i] <= data.Low[i]+bodyprojection:
            data.at[data.index[i], 'Sell'] = 1
            
    return data


def aws_lambda(res,his,shots,T,data_close,all_data):
    values = []
    thead=[]

    with ThreadPoolExecutor() as executor:
        for i in range(int(res)):
            thead.append(i)
            try:    
                print("ThreadID: ",i) 
                data_close
                c = http.client.HTTPSConnection("nzf1krohn2.execute-api.us-east-1.amazonaws.com")      
                
                data = {"his": his, "shots": shots, "T": T, "data_close":data_close, "all_data":all_data}
                
                # print('daafafadada',data)

                # print("sending data...",type(json.dumps(data)))
                    
                c.request("POST", "/default/cc_cw_3", json.dumps(data))        
                response = c.getresponse()  
                
                # print('I am here response',response)      

                data = json.loads(response.read().decode('utf-8') ) 
                print('test_data',data)
                values.append(ast.literal_eval(data['op']))

            except IOError:        
                print( 'Failed to open ', "nzf1krohn2.execute-api.us-east-1.amazonaws.com" )    
                print(data+" from "+str(i)) # May expose threads as completing in a different order    
                return "page "+str(i)
            
    return (values,thead)

def final_mean(values):
    means = []
    for j in (values):
        for i in j:
            means.append([i[0],np.mean(i[1]),np.mean(i[2])])
    return means
'''
os.environ['AWS_ACCESS_KEY_ID']='AKIATF5S43MLGDN2OAEZ'
os.environ['AWS_SECRET_ACCESS_KEY']='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'
#s3 = boto3.resource('s3')
s3 = boto3.client(
    's3',
    region_name = 'us-east-2', 
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), 
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

def writetos3bucket(dft):
    wr.s3.to_csv(df=dft, path='s3://cc-cw-1/cw/cc_cw_1.csv')
    return "Uploaded File"

'''
app = Flask(__name__)

@app.route("/",methods = ["POST","GET"])
def Calling_function():
    if request.method == "POST":
        
        s=request.form['S']
        his=request.form['H']
        shots=request.form['D']
        res=request.form['R']
        T=request.form['T']
        print("inputs",s,his,shots,res,T)
        
        if s=='Lambda':
            data= RandomHandler()
            
            data_close = data.Close.values.tolist()
            
            all_data = data.values.tolist()
            
            values,thead= aws_lambda(res,his,shots,T,data_close,all_data)
            
            final_values = final_mean(values)
            
            bucket_name='cc-cw-1'
            
            val95=[]
            val99=[]
            date=[]
            for i in final_values:
                val95.append(i[1])
                val99.append(i[2])
                date.append(i[0])
                 
            d = zip(date, val95, val99)
            cols =  ['Date', 'Val95', 'Val99']
            dft = pd.DataFrame(d, columns=cols)
            
            return render_template('graph.html',final_values=final_values,val95=val95,val99=val99,date=date)
        elif s=='EC2':
            li=aws_ec2(res,his,shots,user_data)
            val95=[]
            val99=[]
            date=[]
            elapsed=[]
            for i in li:
                k=ast.literal_eval(i)
                for key, value in k.items():
                    for i in k['val_risk']:
                        date.append(i[0])
                        val95.append(i[1])
                        val99.append(i[2])
                    elapsed.append((k['Elp_time']))
            return render_template('graph.html',val95=val95,val99=val99,date=date)

            
    else:
        return render_template('front.html')

if __name__ == "__main__":
    app.run(debug=True)

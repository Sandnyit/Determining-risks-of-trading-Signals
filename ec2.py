import json
import ast
from paramiko import SSHClient
import boto3
import time
import ast
import paramiko

user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/pujariakshayk/Data-Science &&
cd Data-Science
sudo apt install --yes python3-pip &&
pip install -r requirements.txt
'''


date=[]
val95=[]
val99=[]
elapsed=[]

# creating Ec2 instance

values_from_EC2=[]
final_values=[]
def creatingEC2Instance():
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id="AKIATF5S43MLGDN2OAEZ",
            aws_secret_access_key="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")
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            UserData=user_data, 
            KeyName="cc_cw_1",
            SecurityGroupIds=['sg-074b8f5df6c9fa37a']
        )
        print("end of request")
    except Exception as e:
        print(e)

def ec2_details():
    instance_ids = []
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id="AKIATF5S43MLGDN2OAEZ",
            aws_secret_access_key="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")
        for i in resource_ec2.describe_instances()["Reservations"]:

            print(i["Instances"][0]["InstanceId"])
            instance_ids.append(i["Instances"][0]["InstanceId"])
        
        print("DONE")
        return instance_ids
    except Exception as e:
        print(e)


def getting_instance_public_ipAddress(instanceDetails):
    ec2_client = boto3.client("ec2", region_name="us-east-1",aws_access_key_id="AKIATF5S43MLGDN2OAEZ",
            aws_secret_access_key="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")
    reservations = ec2_client.describe_instances(InstanceIds=[instanceDetails]).get("Reservations")
    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            if instance.get("PublicIpAddress") == None:
                continue
            else:    
                return instance.get("PublicIpAddress")
            
def extract_values(host,CC_MinHistory,CC_shots):
    proxy = None
    CC_MinHistory=int(CC_MinHistory)
    CC_shots=int(CC_shots)
    
    print("What is ------>  ",host)
    user="ubuntu"
    key=paramiko.RSAKey.from_private_key_file("./cc_cw_1.pem")
    
    client = SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   
    client.connect(host, username=user,pkey=key)
    print('I am hereeeeeeeee')
    stdin, stdout, stderr = client.exec_command(f'cd /home/ubuntu/ && cd Data-Science/ && python3 EC2.py {CC_MinHistory} {CC_shots} {1}')
    # print('stdout',(stdout.readlines()))
    results = stdout.readlines()[1]
    return results

def stop_EC2_instance(instanceid):
    try:
        print ("Stopping and deleting EC2 instance")
        
        resource_ec2 = boto3.client("ec2")
        resource_ec2.stop_instances(InstanceIds=[instanceid])
        print(f"{instanceid} STOPPED")
    except Exception as e:
        print(e)

# def EC2_instace(CC_resources,CC_MinHistory,CC_shots):
#     for i in range(CC_resources):
#         creatingEC2Instance()
#     time.sleep(120)
#     instanceId = ec2_details()
#     print(instanceId)
    
#     instanceIPaddress = []
    
#     for ins in instanceId:
        
#         ip_address = getting_instance_public_ipAddress(ins)
#         print("IP_Address",ip_address)
#         instanceIPaddress.append(ip_address)
#     for i in instanceId:
#         stop_EC2_instance(i)
        
#     for i in instanceIPaddress:
#         print(i)
#         if i is not None:
#             print(i)
#             my_values = extract_values(i,CC_MinHistory,CC_shots)
#             print("my_values valto count",my_values)
#             for i in my_values:
#                 k=ast.literal_eval(i)
#                 for key, value in k.items():
#                     for i in k['val_risk']:
#                         ec2_date.append(i[0])
#                         ec2_95.append(i[1])
#                         ec2_99.append(i[2])
#                     elapsed.append((k['Elp_time']))
#             values_from_EC2.append([my_values,i])
#             Finalval.append(my_values)
    
#     return  values_from_EC2,Finalval 

# resources=2
# for i in range(resources):
#     creatingEC2Instance()
# time.sleep(120)
his='200'
shots='20000'
# instanceIPaddress=['i-0118171174f34f88d','i-0a5ad59db0b4ec8b2']
# ec2_details()
# for i in instanceIPaddress:
#         print(i)
#         if i is not None:
#             the_ip = getting_instance_public_ipAddress(i)
            
#             my_values = extract_values(the_ip,CC_MinHistory,CC_shots)
            
#             Finalval.append(my_values)
# print(Finalval)
# his=200
# shots=20000
# res=2
def aws_ec2(res,his,shots,user_data):
    # for i in range(res):
    #      creatingEC2Instance(user_data)
    # time.sleep(120)
    
    ip_addr=[]
    details=ec2_details()
    
    for i in details:
        print('teststsbvsaofor i',i)
        ip_address = getting_instance_public_ipAddress(i)
        ip_addr.append(ip_address)
    
    for i in ip_addr:  
        if i is not None:
            val = extract_values(ip_address,his,shots)
            final_values.append(val)
            print('iam final values',final_values)
    return final_values
    
# li=aws_ec2(res,his,shots)
# for i in li:
#     k=ast.literal_eval(i)
#     for key, value in k.items():
#         for i in k['val_risk']:
#             date.append(i[0])
#             val95.append(i[1])
#             val99.append(i[2])
#         elapsed.append((k['Elp_time']))
# print(val95)
    


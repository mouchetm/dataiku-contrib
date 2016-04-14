import os
import dataiku
import json
import pandas as pd, numpy as np
import socket
from dataikuapi.dssclient import DSSClient
from dataiku.customrecipe import *

input_folder = dataiku.Folder(get_input_names_for_role('folder_to_parse')[0])
api_key = get_recipe_config()['api_key']
project_name = dataiku.get_custom_variables()["projectKey"]
dip_home = dataiku.get_custom_variables()["dip.home"]
port_file = dip_home + '/bin/env-default.sh'

with open(port_file, 'r') as f:
    read_data = f.read()
    port = 11200
    for line in read_data.split('\n'):
        if 'DKU_BASE_PORT' in line :
            port = int(line.replace('"','').split('=')[1])

host = socket.getfqdn()
host = 'http://' + host + ':' + str(port)

#create the client to use the rest api
client = DSSClient(host, api_key)

#define the current project
project = client.get_project(project_name)

source_folder_path = input_folder.get_path()

#Let s create the datasets corresponding to thefiles in the folder
files = os.listdir(source_folder_path)

#Extraction loop
dat = []
success = []
succes_reason = []
for file in files :
    try:
        dataset = project.create_dataset(file.encode('ascii', 'ignore').decode('ascii').split('.')[0]  # dot is not allowed in dataset names
            	,'Filesystem'
            	, params={
                	'connection': 'filesystem_root'
                	,'path': source_folder_path+"/" + file
            	}, formatType='csv'
            	, formatParams={
                	'separator': ','
               	 	,'style': 'excel'  # excel-style quoting
                	,'parseHeaderRow': True
            	})
    	dat.append(file.encode('ascii', 'ignore').decode('ascii').split('.')[0])
    	success.append(True)
        succes_reason.append('')
    except Exception as exception:
        dat.append(file.encode('ascii', 'ignore').decode('ascii').split('.')[0])
        success.append(False)
        succes_reason.append(str(exception))


#Save the logs of the extraction
df = pd.DataFrame()
df['output_ds'] = dat
df['success'] = success
df['reason'] = succes_reason

output_dataset = dataiku.Dataset(get_output_names_for_role('verification_dataset')[0])
output_dataset.write_with_schema(df)

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:33:27 2020

@author: Alex
"""


from __future__ import print_function

import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import re
import time


"""
#################
La variable source_drive_id indispensable. Si no se rellena destination_drive_id se tendrá en cuenta source_drive como destination_drive_id 
Las variables source_folder_id y destination_folder_id no son indispensables. Si se encuentran vacias se harán las operaciones en la raiz. Si no, se hará la operacion en la carpeta existente con ese nombre. 
#################

### flag = 0 // Se ordena por décadas // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
### flag = 1 // Se ordena cada pelicula en carpetas // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
### flag = 2 // Se ordena alfabéticamente // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
### flag = 3 // Mueve todo el contenido de una carpeta a otra // Tiene en cuenta variable source_drive_id y destination_drive_id
"""
creds = None

flag = 3

source_drive_id = ''
source_folder_id = ''

destination_drive_id = ''
destination_folder_id = ''

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']


if not destination_drive_id:
    destination_drive_id = source_drive_id
    
if not destination_folder_id:
    destination_folder_id = destination_drive_id
    

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)

#Para coger todos los team drives
'''
shared_drives_response = service.drives().list().execute()

shared_drives_list = shared_drives_response.get('drives', [])
'''

parent_id = ''


page_token = None
total_files = 0

def update_folders():#Arreglar esto diferencia entre destino y origen
    
    global parent_id
    
    folders = {}
    
    q_query =  'mimeType = \'application/vnd.google-apps.folder\' and trashed = false'
    
    if destination_folder_id:
        parent_id = destination_folder_id
        q_query += ' and \'' + destination_folder_id + '\' in parents' 
    else:
        parent_id = destination_drive_id
        
    folders_response = service.files().list(includeItemsFromAllDrives = 'true', supportsAllDrives = 'true', 
                                driveId = destination_drive_id, corpora = 'drive', 
                                q = q_query, fields = 'files(id, name, parents)').execute()
    folders_list = folders_response.get('files', [])
        
        
    for f in folders_list:
        folders[f['name']] = f
        
    return folders

def create_folder(name, destination_id):
    
    global folders, service
    
    body = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents':[destination_id]
            }
    
            
    folder_created = service.files().create(supportsAllDrives = 'true', body=body).execute()
    new_parent = folder_created.get('id')
    
    folders[name] = {'id':new_parent, 'name':name, 'parents':[destination_id]} 
    
    return new_parent
    
    
def decade_mode(name):
    
    p = re.compile(r'\(\d{4}\)')

    year = p.search(name).group(0)
    year = int(year[1:-1])
    
    min_year = year - int(str(year)[-1])
    max_year = min_year + 9
        
    return str(min_year) + ' - ' + str(max_year)
    
def letter_mode(name):
    
    letter = name[0].upper()
    
    if not letter.isalpha():
        return '#'
    
    return letter
    
def file_mode(name):
    
    p = re.compile(r'.*\(\d{4}\)')
    return p.search(name).group(0)


def get_children(items_list, parent_id): #Cambiar retornando valores. Muy chapucero
    global children_tree
    
    for index, item in enumerate(items_list):
        if parent_id == item['parents'][0]:
            children_tree.append(item)
            new_items_list = items_list[:]
            new_items_list.pop(index)
            get_children(new_items_list, item['id'])
    
    
    
start_time = time.time()
items_list = []
while True:
    if flag <0 or flag > 3:
        print("Pon un flag válido")
        break
    
    folders = update_folders()
    
    #q='mimeType=\'video/x-matroska\''
    q_query =  'mimeType != \'application/vnd.google-apps.folder\' and trashed = false'
    
    if source_folder_id:
        q_query = 'trashed = false'
        if flag == 3:
            q_query = 'trashed = false and \'' + source_folder_id + '\' in parents'
    elif flag == 3:
        q_query = 'trashed = false and \'' + source_drive_id + '\' in parents'
 
    items_response = service.files().list(includeItemsFromAllDrives = 'true', supportsAllDrives = 'true', q = q_query,
                                   corpora = 'drive', pageSize=100, driveId = source_drive_id, pageToken=page_token, fields = 'nextPageToken, files(id, name, parents, mimeType)').execute()
    
    items_list = items_response.get('files', [])
    children_tree = []

    if source_folder_id:
        get_children(items_list, source_folder_id)
        
        if flag != 3:
            items_list = [item for item in items_list if item['mimeType'] != 'application/vnd.google-apps.folder']
        else:
            items_list = [item for item in items_list if item['parents'][0] == source_folder_id]
    else:
        if flag == 3:
            items_list = [item for item in items_list if item['parents'][0] == source_drive_id]
    
    for item in items_list:
        try:   
            if flag == 0:
                folder_name = decade_mode(item['name'])
            elif flag == 1:
                folder_name = file_mode(item['name'])
            elif flag == 2:
                folder_name = letter_mode(item['name'])           

            if flag != 3:   
                if folder_name not in list(folders.keys()):
                    new_parent = create_folder(folder_name, destination_folder_id)

                if folders[folder_name]['id'] != item['parents'][0]:
                    # Retrieve the existing parents to remove
                    file_to_move = service.files().get(fileId=item['id'],
                                               supportsAllDrives = 'true',
                                                     fields='parents').execute()
                    previous_parents = ",".join(file_to_move.get('parents'))
                    # Move the file to the new folder
                    file_moved = service.files().update(fileId=item['id'],
                                                        supportsAllDrives = 'true',
                                                        addParents=folders[folder_name]['id'],
                                                        removeParents=previous_parents,
                                                        fields='id, parents').execute()

            else:
                service.files().update(fileId=item['id'],
                                       supportsAllDrives = 'true',
                                       removeParents=item['parents'][0],
                                       addParents=destination_folder_id).execute()
        except:
            print(item['name'] + ' skipped')
        total_files += 1
    
    print('Files moved: ' + str(total_files))
    
    page_token = items_response.get('nextPageToken', None)
    if page_token is None:
        break
    
elapsed_time = time.time() - start_time

print('Total files moved: ' + str(total_files))
print('Elapsed time: ' + str(elapsed_time) + ' seconds.')





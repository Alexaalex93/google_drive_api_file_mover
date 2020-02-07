# google_drive_api_file_mover
Proof of concept about how google drive api works moving files, creating folders...

### How it works:
### 1. It needs a certificated taken from here:
https://developers.google.com/drive/api/v3/quickstart/python   (Enable the Drive API)

### 2. Put the creds.json in the script's folder 

### 3. Modify the flag's number according:
  - flag = 0 // Se ordena por décadas // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
  - flag = 0 // Sort by decade // If the variable destination_drive_id is empty, source_drive_id will be destination_drive_id
  - flag = 1 // Se ordena cada pelicula en carpetas // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
  - flag = 1 // Sort by name in folders // If the variable destination_drive_id is empty, source_drive_id will be destination_drive_id
  - flag = 2 // Se ordena alfabéticamente // Si la variable destination_drive_id está vacía se tendrá en cuenta source_drive_id como destination_drive_id
  - flag = 2 // Sort alphabetically // If the variable destination_drive_id is empty, source_drive_id will be destination_drive_id
  - flag = 3 // Mueve todo el contenido de una carpeta a otra // Tiene en cuenta variable source_drive_id y destination_drive_id
  - flag = 3 // Move the whole content from source to destination // It needs source_drive_id and destination_drive_id
  
### 4. Modify variables source_drive_id, source_folder_id, destination_drive_id and destination_folder_id with the folder's id.
  https://drive.google.com/drive/u/3/folders/1w1pucaGH_example_id_fds_Fhytgzmz8AoTr8s
  - La variable source_drive_id indispensable. Si no se rellena destination_drive_id se tendrá en cuenta source_drive como destination_drive_id 
  - The variable source_drive_id is mandatory. If destination_drive_id is empty will be source_drive_id
  - Las variables source_folder_id y destination_folder_id no son indispensables. Si se encuentran vacias se harán las operaciones en la raiz. Si no, se hará la operacion en la carpeta existente con ese nombre. 
  - The variables source_folder_id y destination_folder_id are optionals. If they are empty the operations will be in the root
### 5. Run the script with python google_api_files_mover.py

If you need to log in with another account, delete token.pickle file.

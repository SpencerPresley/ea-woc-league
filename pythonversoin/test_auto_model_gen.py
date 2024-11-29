import os
import json
import subprocess

cwd = os.getcwd()
response_json_path = os.path.join(cwd, 'response.json')

with open(response_json_path, 'r') as file:
    response_json = json.load(file)
    
first_element = response_json[0]
print(first_element)
input()
with open('first_element.json', 'w') as file:
    json.dump(first_element, file)

command = f"datamodel-codegen --input first_element.json --input-file-type jsonschema --output result_model.py"
subprocess.run(command, shell=True)
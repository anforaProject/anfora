import os
import yaml
from jsonschema import validate

def load_config(filename='settings.yaml'):
    try:
        with open(filename) as f:
    
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data
    except FileNotFoundError:
        data = {
            "base_url": 'localhost:8000',
            "domain": 'localhost',
            "schema": "https",
            "media_folder": ".",
            "salt_code": "salty"
        }

        return data
        
        
def validate_user_creation(data:dict) -> bool:

    schema = {
        "type": "object",
        "properties": {
            "username": "string",
            "password": "string",
            "password_confirmation": "string",
            "email": "string"
        },
        'required':["username", "password", "password_confirmation", "email"]
    }

    try:
        validate(instance=data, schema=schema)
        password_condition = data['password'] == data['password_confirmation']
        return password_condition 
    except:
        return False

import yaml
from jsonschema import validate

def load_config(filename='settings.yaml'):
    with open(filename) as f:
    
        data = yaml.load(f, Loader=yaml.FullLoader)
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

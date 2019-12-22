import hashlib
import base64
import yaml
from jsonschema import validate

def load_config(filename='../settings.yaml'):
    with open(filename) as f:
    
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

async def validate_status_creation(data:dict) -> bool:

    schema = {
        "type": "object",
        "properties": {
            "caption": "string",
            "spoiler_test": "string",
            "is_public": "boolean",
            "sensitive": "boolean",
            "in_reply_to": "string",
            "media_ids": {
                "type": "string",
                "minItems": 1,
                "maxItems": 10
            }
        },
        'required':["media_ids"]
    }

    try:
        # Validate the schema
        validate(instance=data, schema=schema)
        return True
    except:
        return False

### Compute ids
def generate_id(num):
    return base64.urlsafe_b64encode(
        hashlib.md5(str(num).encode()).digest()
    )[:11].decode()

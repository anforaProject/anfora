import toml
from box import Box

settings = {}

with open('settings.toml', 'r') as f:
    settings = Box(toml.loads(f.read()))


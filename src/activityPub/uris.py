URLS = {
    "notes": "/notes"
}

def reverse_uri(name):
    try:
        return URLS[name]
    else:
        return ""

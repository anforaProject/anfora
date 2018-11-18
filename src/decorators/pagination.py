from settings import DOMAIN, SCHEME

def ap_pagination(obj):
    pagination = {
        'default_pagination': 10,
        'id': f'{SCHEME}://{DOMAIN}{obj.request.path}',
        'partOf': f'{SCHEME}://{DOMAIN}{obj.request.path}',
    }

    if obj.request.query_arguments:
        pagination['id'] += f"?{''.join([f'{x}={str(obj.request.query_arguments[x][0].decode())}' for x in obj.request.query_arguments])}"
     
    
    pagination['page'] = int(obj.get_argument('page', 0))
    pagination['next'] = f'{SCHEME}://{DOMAIN}{obj.request.path}?page={pagination["page"]+1}'
    return pagination
    

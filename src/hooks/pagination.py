import falcon
from settings import DOMAIN, SCHEME

def ap_pagination(req, resp, resource, params):
    pagination = {
        'default_pagination': 10,
        'id': f'{SCHEME}://{DOMAIN}{req.path}',
        'partOf': f'{SCHEME}://{DOMAIN}{req.path}',
    }

    if req.query_string:
        pagination['id'] += f"?{req.query_string}"
     
    
    pagination['page'] = req.get_param_as_int('page') or 0
    pagination['next'] = f'{SCHEME}://{DOMAIN}{req.path}?page={pagination["page"]+1}'
    req.context['pagination'] = pagination
    

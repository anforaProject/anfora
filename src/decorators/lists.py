import re

"""
The objetive of this decorator is to provide a sintax 
like the one for mastodon in order to get lists of arguments.

From the mastodon documentation

An array parameter must encoded using bracket notation, e.g. array[0]=foo&array[1]=bar would be translated into:

array = [
  'foo',
  'bar',
]
"""

# This regular expresion creates to groups.
# One with the number of the list and the second with the index 
rex = re.compile(r'([a-zA-Z]*)\[([0-9])\]')

def group_lists(model):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            #Dictionary mapping list names to their lists
            dic = dict()
            # A list of pairs with name and length
            analisis = {}
            for key, value in self.request.argumnets:
              match = p.match(key)
              if match != None:
                name = match.group(1)
                max = match.group(2)
                
                if name in analisis.keys() and max > analisis[name]:
                  analisis[name] = max

            for name in analisis:
              for i in range(analisis+1):
                dic[name].append(self.request.arguments.get(f'{name}[{i}]'))

            self.kwargs = {**self.kwargs, **dic}
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
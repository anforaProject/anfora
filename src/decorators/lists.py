import re
import functools
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
# One with the name of the list and the second with the index 
reg = re.compile(r'([a-zA-Z0-9\_]+)\[([0-9]+)\]')

def group_lists(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        #Dictionary mapping list names to their lists
        dic = dict()
        # A list of pairs with name and length
        analisis = dict()
        for key, value in self.request.arguments.items():
          match = reg.match(key)
          if match != None:
            name = match.group(1)
            maxi = match.group(2)
            if name in analisis.keys() and maxi > analisis[name]:
              analisis[name] = maxi
            elif name not in analisis.keys():
              analisis[name] = maxi 

        for name in analisis.keys():
          dic[name] = []
          for i in range(int(analisis.get(name))+1):
            dic[name].append(self.request.arguments.get(f'{name}[{i}]')[0].decode('utf-8'))

        self.kwargs = {**kwargs, **dic}
        return method(self,*args, **kwargs)
    return wrapper
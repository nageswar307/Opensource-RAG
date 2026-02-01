import sys

dict1 = {'a': 100, 'b': 62, 'c': 400}


dict2 = {k:v for k,v in dict1.items() if k!='b'}

print(dict2)






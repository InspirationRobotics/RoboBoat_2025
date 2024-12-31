"""
Sandbox file to make it convenient to see how code works/experiment with syntax.
Can be deleted whenever someone feels like cleaning up.
"""
# create a python dictionary 
d = {"name": "Geeks", "topic": "dict", "task": "iterate"}

# default loooping gives keys
for keys in d:
    print(keys)
    
# looping through keys    
for keys in d.keys():
  print(keys)


# create a python dictionary 
d = {"name": "Geeks", "topic": "dict", "task": "iterate"}

# iterating both key and values
for key, value in d.items():
    print(f"{key}: {value}")
import json

with open("pydantic_schema_file.json", "r") as f:
    file = f.read()

file_json = json.loads(file)


print(file_json.keys())
print()
links: dict()
for definition in file_json["definitions"]: 
    print(definition)
    try:
        print(file_json["definitions"][definition]["properties"]["grammar"]["default"])
        grammar = str(file_json["definitions"][definition]["properties"]["grammar"]["default"])
        print()
        if grammar == 'registration':
            links[file_json["definitions"][definition]] = []
            if grammar == 'selection':
                links[file_json["definitions"][definition]] = [grammar]
                #print(links)
    except: KeyError
    

import json
import pydantic
from typing import List, Optional
from pydantic import BaseModel
from pydantic.schema import schema

# generates just defintions and stores in dictionary

class Dataset(BaseModel):
    dataset_name: str
    data_file: str

class ytCreateModel(BaseModel):
    data_out: Optional[bool]
    var_name: Optional[str]
    Data: List[Dataset]

top_level_schema = schema([ytCreateModel], title = "top level test")

print(top_level_schema)
print()
print(json.dumps(top_level_schema, indent=2))

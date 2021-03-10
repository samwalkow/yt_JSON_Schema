from pydantic import BaseModel, Field, constr
from typing import Generic, List, Union, Dict, Optional, Any
import pydantic
from pydantic.main import create_model
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum
import json

some_data = list()

@dataclass
class Dataset:
    filename: str
    name: str

@dataclass
class DataOutput:
    name: str
    data_location: Any
    create_output: bool = False
    create_hdf5: bool = False
    create_export: bool = False

    def get_output(self, data_list):
        if self.create_output == True:
            save_data = create_model(self.name, data=self.data_location)
            print(save_data)
            data_list.append(save_data)
            return save_data

# print()    
# data_resuse = DataOutput(data_location="somedata", create_output=True)
# test_reuse = data_resuse.get_output("more_data")
# print(test_reuse.schema_json(indent=2))
# print()

class Data_Model(BaseModel):
    data_source: Union[Dataset, DataOutput]

get_that_data = Data_Model(data_source = {"name": "Org DataSet", 
                                        "data_location": "Average Density", 
                                        "create_output": True})

test_data = DataOutput("Dataset", "Density", True)
print()
print(test_data)
print()
test_json = test_data.get_output(some_data)
#print(test_json.json(indent=2))
print()
print(test_json.schema_json(indent=2))
# print()
# print(get_that_data.json())
# print(get_that_data.schema_json(indent=2))
# print(i for i in some_data)






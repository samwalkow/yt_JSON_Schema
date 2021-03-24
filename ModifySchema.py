import pydantic
from pydantic import BaseModel
from typing import List, Optional, Dict, Type, Any

class Dataset(BaseModel):
    dataset_name: str = "Density"
    data_file: str = "sam.txt"

class ytCreateModel(BaseModel):
    data_out: Optional[bool]
    var_name: Optional[str]
    Data: List[Dataset]

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model:Type['ytCreateModel'])->    None:
                for prop in schema.get('definitions', {}).values():
                    prop.pop('title', None)

print(ytCreateModel.schema_json(indent=2))

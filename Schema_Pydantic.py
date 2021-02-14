from enum import Enum
from pydantic import BaseModel, Field, constr
from typing import List

import pydantic

class Comments(BaseModel):
    comment: str

class Dataset(BaseModel):
    filename: str
    name: str = "DataforScience"

class Field(BaseModel):
    field_one: str
    weighted_field: str = None

class AxisPlot(BaseModel):
    axis: str

class Center(BaseModel):
    center: str

class Widths(BaseModel):
    width: str

class ytModel(BaseModel):
    '''
    An example for a yt analysis schema using Pydantic
    '''
    CommentsUser: List[Comments]
    Data: Dataset
    FieldList: List[Field]
    AxisPlot: List[AxisPlot]
    CenterPlot: Center
    WidthPlot: List[Widths]

    class Config:
        title = 'yt example'


test = ytModel(CommentsUser = [{"comment": "Exploring Data!"}], Data = {"filename": "Sam.txt"}, FieldList = [{"field_one": "density"} ,{"field_one": "temp"}], AxisPlot = [{"axis": "x"}], CenterPlot = {"center": "z"}, WidthPlot = [{"width": "1"}])

print(test.json())
print(test.schema_json(indent=2))

# print(dir(pydantic))
# print(help(pydantic))
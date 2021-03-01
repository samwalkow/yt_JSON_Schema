from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field, constr
from typing import Generic, List, Union, Dict, Optional
import pydantic
from pydantic.main import create_model
from uuid import UUID, uuid4
from dataclasses import dataclass

class Dataset(BaseModel):
    output_id: UUID = uuid4()
    filename: str = ...
    name: str = "Data for Science"
    comments: Optional[str] 
    grammar: str = "registration"

class Fields(BaseModel):
    output_id: UUID = uuid4()
    field: str = ...
    # unit - domain specific
    unit: str
    comments: Optional[str]
    grammar: str = "selection"

class AxisPlot(BaseModel):
    output_id: UUID = uuid4()
    axis: str
    comments: Optional[str]

class Center(BaseModel):
    output_id: UUID = uuid4()
    center: str
    comments: Optional[str]

class Widths(BaseModel):
    output_id: UUID = uuid4()
    width: str
    comments: Optional[str]

class Average(BaseModel):
    output_id: UUID = uuid4()
    average_field: Fields
    comments: Optional[str]
    grammar: str = "reduction"

class Sum(BaseModel):
    output_id: UUID = uuid4()
    sum_field: Fields
    comments: Optional[str]
    grammar: str = "reduction"

class Operations(BaseModel):
    operation: Union[Sum, Average]

class _PlotAttributes(BaseModel):
    # necessary and private plotting functions for all plots
    PlottingWindow: str = "1.0"

class SlicePlot(BaseModel):
    output_id: UUID = uuid4()
    Data: Dataset
    PlotFields: Union[Operations, Fields]
    AxisPlot: List[AxisPlot]
    CenterPlot: Optional[Center]
    WidthPlot: Optional[List[Widths]]
    Comments: Optional[str]
    Annotation : bool = False
    # color map - domain specific
    ColorMap: str = None
    _PlotFunctions: _PlotAttributes

class ytModel(BaseModel):
    '''
    An example for a yt analysis schema using Pydantic
    '''
    Plot: List[SlicePlot]
    #Analysis: [List[Operations]

    class Config:
        title = 'yt example'
        underscore_attrs_are_private = True

# file_path = Path("Data.json")
# print(file_path)

test = ytModel(Plot = [{"Data": {"filename": "Sam.txt"}, "PlotFields": {"field": "density", "unit": "kpc"}, "AxisPlot": [{"axis": "x"}], "CenterPlot": {"center": "z"}, "WidthPlot": [{"width": "1"}]}])

print("Instance Example:")
print(test.json(indent=2))
print()
print("Schema Example:")
print(test.schema_json(indent=2))
print()

# yt_dynamic = create_model("Dynamic_yt_model", dataset=(str, "file.txt"), FieldList = (list, ["density", "temperature"]), axis=(str, "x"))

# #print(yt_dynamic.schema_json(indent=2))

# # print(dir(pydantic))
# # print(help(pydantic))

with open("pydantic_schema_file.json", "w") as file:
    file.write(test.schema_json(indent=2))

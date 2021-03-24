from Schema_Pydantic import Operations
from enum import Enum
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field, constr
from typing import Generic, List, Union, Dict, Optional
import pydantic
from pydantic.main import create_model
from uuid import UUID, uuid4
from dataclasses import dataclass

#from pydantic.types import ModelOrDc


class Dataset(BaseModel):
    """ 
    The dataset model to load and that will be drawn from for other classes. Filename is the only required field. 
    """
    output_id: UUID = uuid4()
    filename: str
    name: str = "Data for Science"
    comments: Optional[str]
    grammar: str = "registration"


class DataFields(BaseModel):
    output_id: UUID = uuid4()
    data_field: str
    # unit - domain specific
    unit: str
    comments: Optional[str]
    grammar: str = "selection"

@dataclass
class DataSource:
    data_selection: Dataset = None
    field_selection: Union[DataFields, Operations] = None
    data_name: str = "density1"

    # def create_variable(self, data_out):
    #     if data_out:
    #         data_model = create_model(self.data_name, data_selection=(self.data_selection), field_selection=(self.field_selection))
    #         #print(data_model)
    #         with open(str(self.data_name)+"_schema_file.json", "w") as file:
    #             file.write(data_model.schema_json(indent=2))

# @dataclass
# class DataOutput(DataSource):
#     data_create: DataSource
#     data_out: bool = True
#     output_format: str = None
    

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
    average_field: DataFields
    comments: Optional[str]
    grammar: str = "reduction"


class Sum(BaseModel):
    output_id: UUID = uuid4()
    sum_field: DataFields
    comments: Optional[str]
    grammar: str = "reduction"


class Operations(BaseModel):
    operation: Union[Sum, Average]


class _PlotAttributes(BaseModel):
    # necessary and private plotting functions for all plots
    PlottingWindow: str = "1.0"



class SlicePlot(BaseModel):
    output_id: UUID = uuid4()
    DataSources: DataSource
    # DataOutput: DataOutput
    AxisPlot: Optional[List[AxisPlot]]
    CenterPlot: Optional[Center]
    WidthPlot: Optional[List[Widths]]
    Comments: Optional[str]
    Annotation: bool = False
    # color map - domain specific
    ColorMap: str = None
   # _PlotFunctions: _PlotAttributes


class ytModel(BaseModel):
    '''
    An example for a yt analysis schema using Pydantic
    '''
    Plot: List[SlicePlot]
    #Analysis: [List[Operations]

    class Config:
        title = 'yt example'
        underscore_attrs_are_private = True


test = ytModel(Plot=[{"DataSources": {"data_selection": {"filename": "Sam.txt"}, "field_selection": {"data_field": "density", "unit": "kpc"}},
                    "AxisPlot": [{"axis": "x"}], 
                    "CenterPlot": {"center": "z"}, 
                    "WidthPlot": [{"width": "1"}]}])

print("Instance Example:")
print(test.json(indent=2))
print()
print("Schema Example:")
print(test.schema_json(indent=2))
print()

with open("datafirst_schema_file.json", "w") as file:
    file.write(test.schema_json(indent=2))

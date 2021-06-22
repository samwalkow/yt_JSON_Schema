

#%%

from BaseModelFunctions import ytDataObjectAbstract
from enum import Enum
from types import new_class
from numba.core.decorators import jit
from numpy import place
from pydantic import BaseModel, Field, constr
from typing import Generic, List, Union, Dict, Optional, Sequence, Tuple, Any
import pydantic
from pydantic.main import create_model
from inspect import getfullargspec, getmembers
import yt
import json
from numba.experimental import jitclass


# %%
def show_plots(schema):
    """This function accepts the schema model and runs it using yt code which returns a list. This function iterates through the list and displays each output. 

    Args:
        schema ([dict]): the analysis schema filled out with yt specificaions
    """
    result = schema._run()
    print(result)
    for output in range(len(tuple(result))):
        print("each output:", result[output])
        result[output].show()

#%%

class ytBaseModel(BaseModel):
    """A class to connect attributes and their values to yt operations and their keywork arguements. 

    Args:
        BaseModel ([type]): A pydantic basemodel in the form of a json schema

    Raises:
        AttributeError: [description]

    Returns:
        [list]: A list of yt classes to be run and then displayed
    """
    _arg_mapping: dict = {}  # mapping from internal yt name to schema name
    _yt_operation: Optional[str]
    # the list to store the data after it has been instaniated
    _data_source = {}
    _main_args = []
    print("arg attribute:", _main_args)
    
    def _run(self):

         # the list that we'll use to eventually call our function
        the_args = []
        # this method actually executes the yt code
        # first make sure yt is imported and then get our function handle. This assumes
        # that our class name exists in yt's top level api.
        import yt

        print(self._yt_operation)
        funcname = getattr(self, "_yt_operation", type(self).__name__)
        print("found name:", funcname)

        # if the function is not readily available in yt, move to the except block
        # try:
        func = getattr(yt, funcname)
        print(f"pulled func {func}", type(func))
                    

        # now we get the arguments for the function:
        # func_spec.args, which lists the named arguments and keyword arguments.
        # ignoring vargs and kw-only args for now...
        # see https://docs.python.org/3/library/inspect.html#inspect.getfullargspec
        func_spec = getfullargspec(func)
        print("spec", func_spec)

        # the argument position number at which we have default values (a little hacky, should
        # be a better way to do this, and not sure how to scale it to include *args and **kwargs)
        n_args = len(func_spec.args)  # number of arguments
        print("number of args:", n_args)
        if func_spec.defaults is None:
            # no default args, make sure we never get there...
            named_kw_start_at = n_args + 1
            print(named_kw_start_at)
        else:
            # the position at which named keyword args start
            named_kw_start_at = n_args - len(func_spec.defaults)
        print(f"keywords start at {named_kw_start_at}")

        # loop over the call signature arguments and pull out values from our pydantic class .
        # this is recursive! will call _run() if a given argument value is also a ytBaseModel.
        for arg_i, arg in enumerate(func_spec.args):
            # check if we've remapped the yt internal argument name for the schema
            if arg == 'self':
                continue

            # get the value for this argument. If it's not there, attempt to set default values
            # for arguments needed for yt but not exposed in our pydantic class
            print("the arguemnt:", arg)
            try:
                arg_value = getattr(self, arg)
                print("the arg value:", arg_value)
                if arg_value == None:
                    default_index = arg_i - named_kw_start_at
                    arg_value = func_spec.defaults[default_index]
                    print('defaults:', default_index, arg_value)
            except AttributeError:
                if arg_i >= named_kw_start_at:
                    # we are in the named keyword arguments, grab the default
                    # the func_spec.defaults tuple 0 index is the first named
                    # argument, so need to offset the arg_i counter
                    default_index = arg_i - named_kw_start_at
                    arg_value = func_spec.defaults[default_index]
                    print('defaults:', default_index, arg_value)
                else:
                    raise AttributeError

            # check if this argument is itself a ytBaseModel for which we need to run
            # this should make this a fully recursive function?
            if isinstance(arg_value, ytBaseModel) or isinstance(arg_value, ytParameter):
                print(
                    f"{arg_value} is a {type(arg_value)}, calling {arg_value}._run() now...")
                arg_value = arg_value._run()

            the_args.append(arg_value)
            print("the args list:", the_args)
        self._main_args.append(the_args)


        # this saves the data from yt.load, so it can be used to instaniate the data object items
        if funcname == 'load':
            self._data_source[funcname] = func(*the_args)
        return func(*the_args)

class ytParameter(BaseModel):
    _skip_these = ['comments', 'data_source']

    def _run(self):
        p = [getattr(self, key) for key in self.schema()[
            'properties'].keys() if key not in self._skip_these]
        if len(p) > 1:
            print("some error", p)
            raise ValueError(
                "whoops. ytParameter instances can only have single values")
        return p[0]

# %%

class ytDataObjectAbstract(ytBaseModel):
    # abstract class for all the data selectors to inherit from

    def _run(self):
        from yt.data_objects.data_containers import data_object_registry

        the_args = []
        funcname = getattr(self, "_yt_operation", type(self).__name__)
        print("function name:", funcname)

        val = data_object_registry[funcname]
        
        # get the function from the data object registry
        val = data_object_registry[funcname]
        print("function:", val)
             
        # iterate through the arguments for the found data object
        for arguments in val._con_args:
            print("the args:", arguments)
            con_value = getattr(self, arguments)
            print(con_value)

            # check that the argument is the correct instance
            if isinstance(con_value, ytDataObjectAbstract):
                # call the _run() function on the agrument
                con_value = con_value._run()

            the_args.append(con_value)

        func_spec = getfullargspec(val)
        print('full spec:', func_spec)
        spec_value = getattr(self, 'data_source')
        if isinstance(spec_value, ytDataObjectAbstract) or isinstance(spec_value, ytBaseModel) or isinstance(spec_value, ytParameter):
            spec_value._run()
        ds = spec_value
  
        print("the argument list:", the_args)
        # if there is a dataset sitting in _data_source, add it to the args and call as a keyword argument
        if len(self._data_source) > 0:
            ds = list(self._data_source.values())[0]
            return val(*the_args, ds=ds)
        else:
            return val(*the_args, ds=ds)



class Dataset(ytBaseModel):
    """ 
    The dataset to load. Filen name must be a string.
    
    Required fields: Filename 
    """
    fn: str = Field(alias="FileName", description='Must be string containing the (path to the file and the) file name')
    name: str = "Data for Science"
    comments: Optional[str] 
    _yt_operation: str = "load"
    #_arg_mapping: dict = {'fn' : 'filename'}
    

class FieldNames(ytParameter):
    """
    Specify a field name and optionally, a unit
    """
    # can't seeem to alias 'field' - maybe because the pydantic name 'Field' is called to do the alias?
    field: str 
    # unit - domain specific
    # getting an error with unit enabled
    _unit: Optional[str]
    comments: Optional[str]

class Sphere(ytDataObjectAbstract):
    """A sphere of points defined by a *center* and a *radius*.

    Args:
        ytBaseModel ([type]): [description]
    """
    # found in the 'selection_data_containers.py' 
    center: List[float] = Field(alias='Center')
    radius: Union[float, Tuple[float, str]] = Field(alias='Radius')
    data_source: Optional[Dataset] = Field(alias="Dataset")
    _yt_operation: str = "sphere"

class Region(ytDataObjectAbstract):
    center: List[float]
    left_edge: List[float]
    right_edge: List[float]
    _yt_operation: str = "region"

class Slice(ytDataObjectAbstract):
    axis: Union[int, str]
    coord: float
    _yt_operation: "slice"

class SlicePlot(ytBaseModel):
    ds: Dataset = Field(alias='Dataset')
    fields: FieldNames = Field(alias='FieldNames')
    axis: str = Field(alias='Axis')
    center: Optional[Union[str, List[float]]] = Field(alias='Center')
    width: Optional[Union[List[str], tuple[int, str]]] = Field(alias='Width')
    data_source: Optional[Sphere]
    Comments: Optional[str]
    _yt_operation: str = "SlicePlot"
    #_arg_mapping: dict = {'ds': 'Dataset', 'fields': 'Field',
    #                     'axis': 'Axis', 'center': 'CenterPlot', 'width': 'WidthPlot'}
  

class ProjectionPlot(ytBaseModel):
    ds: Optional[Dataset] = Field(alias='Dataset')
    fields: FieldNames = Field(alias='FieldNames')
    axis: Union[str, int] = Field(alias='Axis')
    # domain stuff here. Can we simplify? Contains operations stuff too
    center: Optional[str] = Field(alias='Center')
    # more confusing design. Can we simplify? This contain field names, units, and widths
    width: Optional[Union[tuple, float]] = Field(alias='Width')
    axes_unit: Optional[str] = Field(alias='AxesUnit')
    weight_field: Optional[FieldNames] = Field(alias='WeightFieldName')
    max_level: Optional[int] = Field(alias='MaxLevel')
    # need to sort this design out
    # might need to be a seperate class since we need to limit the length
    origin: Optional[Union[str, List[str]]] = Field(alias='Origin')
    #right handed? what does this mean?
    right_handed: Optional[bool] = Field(alias='RightHanded')
    fontsize: Optional[int] = Field(alias='FontSize')
    # TODO: a dict for dervied fields - can imporve
    field_parameters: Optional[dict] = Field(alias='FieldParameters')
    # better name?
    method: Optional[str] = Field(alias='Method')
    data_source: Optional[Union[Sphere, Slice]] = Field(alias="DataSource", description="Select a subset of the dataset to visualize from the overall dataset")
    Comments: Optional[str]
    _yt_operation: str = "ProjectionPlot"
    # #_arg_mapping: dict = {'ds': 'Dataset', 'fields': 'Field',
    #                         'axis': 'Axis', 'center': 'CenterPlot',
    #                       'weight_field': 'WeightedField', 'axes_unit': 'AxesUnit', 
    #                       'max_level': 'MaxLevel',
    #                       'right_handed': 'RightHanded',
    #                       'font_size': 'FontSize',
    #                       'Method': 'method',
    #                       'data_source': 'DataSource'}

class PhasePlot(ytBaseModel):
    data_source: Union[Dataset, Any] = Field(alias='Dataset')
    x_field: FieldNames = Field(alias='xField')
    y_field: FieldNames = Field(alias='yField')
    z_fields: Union[FieldNames, List[FieldNames]] = Field(alias='zField(s)')
    weight_field: Optional[FieldNames]= Field(alias='WegihtFieldName')
    x_bins: Optional[int] = Field(alias='xBins')
    y_bins: Optional[int] = Field(alias='yBins')
    # different names and explaintions for accumulation and fractional and shading
    accumulation: Optional[Union[bool, List[bool]]] = Field(alias='Accumulation')
    fractional: Optional[bool] = Field(alias='Fractional')
    figure_size: Optional[int] = Field(alias='FigureSize')
    fontsize: Optional[int] = Field(alias='FontSize')
    # different name? Maybe should be an enum?
    shading: Optional[str] = Field(alias='Shading')
    Comments: Optional[str]
    _yt_operation: str = "PhasePlot"
    #_arg_mapping: dict = {'data_source': 'Dataset', 'x_field': 'xField', 'y_field': 'yField', 'z_fields': 'zField', 'weight_field': 'WeightedField', 'x_bins': 'xBins', 'y_bins': 'yBins', 'accumulation': 'Accumulation', 'fractional': 'Fractional', 'figure_size': 'FigureSize', 'fontsize': 'FontSize',
    #'shading': 'Shading'}

class Visualizations(BaseModel):
    # use pydantic basemodel
    SlicePlot: Optional[SlicePlot]
    ProjectionPlot: Optional[ProjectionPlot]
    PhasePlot: Optional[PhasePlot]
    #_yt_operation: str = None



# %%

class ytModel(ytBaseModel):
    '''
    An example for a yt analysis schema using Pydantic
    '''
    #Plot: List[Union[ProjectionPlot, PhasePlot, SlicePlot]]
    #Data: Dataset
    Plot: List[Visualizations]

    class Config:
        title = 'yt example'
        underscore_attrs_are_private = True
    
    def _run(self):
        # for the top level model, we override this. Nested objects will still be recursive!
        output_list = list()
        att = getattr(self, "Plot")
        for p in att:
            for attribute in dir(p):
                if attribute.endswith('Plot'):
                    new_att = getattr(p, attribute)
                    if new_att is not None:
                        output_list.append(new_att._run())
            return output_list

# %%

# json_slice = {"Dataset": {
#     "FileName": "IsolatedGalaxy/galaxy0030/galaxy0030"},
#     "FieldNames": {"field": "density"},
#     "Axis": "x",
#     "data_source": {"center":[0.5, 0.5, 0.5], "radius": 0.1}}

json_projection = {"Dataset": {
    "FileName": "IsolatedGalaxy/galaxy0030/galaxy0030"},
    "FieldNames": {"field": "temperature"},
    "Axis": "x",
    "Center": "max",
    # "DataSource": {"axis": "x", "coord": 0.5}}
    "DataSource": {"Center": [0.5, 0.5, 0.5], "Radius": 0.1}}
    # "weight_field": {"field": "velocity_magnitude"},
    # "axes_unit": "cm"}
    #"DataSource": {"Center": [0.75, 0.5, 0.5], "Radius": 2.0}}

# json_phase = {"Dataset": {
#     "FileName": "IsolatedGalaxy/galaxy0030/galaxy0030"},
#     "xField": {"field": "density"},
#     "yField": {"field" : "temperature"},
#     "zField(s)": {"field": "velocity_magnitude"}}
    # "weight_field": {"field": "density"},
    # "x_bins": 100,
    # "y_bins": 100,
    # "accumulation": False,
    # "fractional": True,
    # "figure_size": 8,
    # "fontsize": 16,
    # "shading": "nearest"}

analysis_model = ytModel(Plot = [
    {
        #"SlicePlot": json_slice
        "ProjectionPlot": json_projection,
        #"PhasePlot": json_phase
        }
    ]
)

print("the model:", analysis_model)
print(type(analysis_model))

# %%

print(show_plots(analysis_model))


# %%

live_json = open("pydantic_instance.json")
live_schema = json.load(live_json)
live_schema.pop('$schema')
print(live_schema)

analysis_model = ytModel(Plot = 
    live_schema['Plot']
)


print("the model:", analysis_model)
print(type(analysis_model))

# print("Instance Example:")
# print(analysis_model.json(indent=2))
# print()
# print("Schema Example:")
# print(analysis_model.schema_json(indent=2))
# print()

# %%
print(show_plots(analysis_model))


# result = analysis_model._run()
# print(result, type(result))
# print(result[0].show())
# print(result[1].show())

# %%

with open("pydantic_schema_file.json", "w") as file:
    file.write(analysis_model.schema_json(indent=2))


# %%
import yt
import inspect
from yt.data_objects.data_containers import data_object_registry
import textwrap

replacement_dict = {
    "Activedimensions": "Active Dimensions",
    "Op": "Operation",
    " norm vec": "Normal vector",
    "Dobj1": "Data object 1",
    "Dobj2": "Data object 2",
    " obj list": "Object List",
    "N ref": "Particle count refinement criteria"
}
tw = textwrap.TextWrapper(drop_whitespace = True, replace_whitespace = True, fix_sentence_endings=True)
def extract_description(docstring):
    description = docstring[:docstring.find("Parameters")]
    return tw.fill(" ".join([_.strip() for _ in description.splitlines()]))
for n, obj in sorted(data_object_registry.items()):
    print("#### {} {{#sec:dobj-{}}}".format(n.replace("_", " ").capitalize(), n))
    obj._con_args?
    print("\n*Arguments*: \n")
    for arg in obj._con_args:
        
        aname = arg.replace("_"," ").capitalize()
        print(" * {}".format(replacement_dict.get(aname, aname)))
    print("\n{}\n".format(extract_description(obj.__doc__).strip()))


#func = getattr(yt, "Region")

#yt.ProjectionPlot?

# ds = yt.load("IsolatedGalaxy/galaxy0030/galaxy0030")
# sp = ds.sphere([0.5, 0.5, 0.5], 0.1)

# sp?



# %%
import yt

ds = yt.load("IsolatedGalaxy/galaxy0030/galaxy0030")
slc = yt.SlicePlot(ds=ds, fields='density', axis='x')
slc.save?

# %%
import yt

ds = yt.load("IsolatedGalaxy/galaxy0030/galaxy0030")
ds.sphere?
# %%

import matplotlib as plt

plt.savefig?
# %%

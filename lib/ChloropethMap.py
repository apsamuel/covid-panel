from math import pi
import os
import sys
from copy import copy
from operator import ge
from . import datasources
from datetime import date, datetime, timedelta
from bokeh.tile_providers import get_provider, WIKIMEDIA, CARTODBPOSITRON, STAMEN_TERRAIN, STAMEN_TONER, ESRI_IMAGERY, OSM


from bokeh.transform import cumsum, factor_cmap
from bokeh.palettes import *
#from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c
from bokeh.layouts import widgetbox, layout, column, row
from bokeh.models import LinearColorMapper, LogColorMapper
from bokeh.models import ColumnDataSource, GeoJSONDataSource, TableColumn, DataTable
from bokeh.models.widgets.markups import Div 
from bokeh.models.widgets import DateSlider, DateRangeSlider
from bokeh.models import CustomJS, Spinner
from bokeh.models import DateFormatter, NumberFormatter, HTMLTemplateFormatter, DatetimeTickFormatter, NumeralTickFormatter, MonthsTicker, YearsTicker
from bokeh.plotting import figure

from bokeh.models.widgets import Panel, Tabs, TableColumn
from bokeh.models import CustomJS, Select
#from bokeh.themes import built_in_themes
import warnings
warnings.filterwarnings('ignore')
from operator import ge
import sys, os
from copy import copy
from datetime import datetime


sys.path.append(".")

# gdf_full = geodb(df_full, shapesdb(), codedb())
# gdf_full_grouped = geodb(groupdb(df_full), shapesdb(), codedb())
class ChloropethMap():

    def __init__(self):
       self.db = datasources.geodb(
           datasources.groupdb(
               datasources.fixtures(
                   datasources.fulldb()[0]
                   )
           ),
           datasources.shapesdb(),
           datasources.codedb()
       )

    def layout(self):

        def make_div():
            return Div(
                text="Testing a Div"
            )

        return layout(
            name="chloropeth_map",
            children=[
                [ make_div(), ], 
                [ make_div(), ]       
            ]
        )
    #    self.source = GeoJSONDataSource(
    #        geojson=self.db.to_json(cls=datasources.PandasTimeStampEncoder)
    #    )
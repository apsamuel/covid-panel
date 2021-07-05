from lib.loginator import Loginator
from math import pi
import os
import sys
from copy import copy
from operator import ge
from bokeh.models.annotations import ColorBar

from bokeh.models.tools import HoverTool
from . import datasources
from datetime import date, datetime, timedelta
from bokeh.tile_providers import get_provider, WIKIMEDIA, CARTODBPOSITRON, STAMEN_TERRAIN, STAMEN_TONER, ESRI_IMAGERY, OSM


from bokeh.transform import cumsum, factor_cmap
from bokeh.palettes import *
#from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c
from bokeh.layouts import widgetbox, layout, Column, Row, LayoutDOM
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
import pandas as pd
import bokeh 

log = logging.getLogger(__name__)
logger = Loginator(
    logger=log,
    lvl='DEBUG'
).logger

sys.path.append(".")


class ChoroplethMap():

    def __init__(self, db: pd.core.frame.DataFrame):
        self.db = db

    def layout(self) -> bokeh.models.layouts.Column:
        """
        Returns a Bokeh Layout Column containing widgets (slider & select) and a chloropleth plot
        """
        slider = DateRangeSlider(
            title='map_slider',
            name='map_slider',
            start=self.db.Date.min().date(),
            end=self.db.Date.max().date(),
            value=(
                    self.db.Date.min().date(),
                    self.db.Date.max().date(),
            ),
            format="%Y %m %d"
        )
        self.slider = slider 
        #select drop down for stats
        select = Select(
            name='select_stat',
            title='Select Statistic',
            value='Active',
            options=[
                'Active',
                'Confirmed',
                'Deaths',
                'Recovered'
            ]
        )
        self.select = select 

        def make_plot():
            db = self.db.copy(deep=True)
            mask = (db['Date'] > datetime.fromtimestamp(slider.value[0]/1000)
                    ) & (db['Date'] <= datetime.fromtimestamp(slider.value[1]/1000))
            db = db.loc[mask]
            src = GeoJSONDataSource(geojson=db.to_json(cls=datasources.PandasTimeStampEncoder))
            palette = Reds256[::-1]
            color_mapper = LinearColorMapper(
                palette=palette,
                low=db[select.value].min(),
                high=db[select.value].max()
            )
            hover = HoverTool(
                tooltips = [
                    ('Date', '@Date'),
                    ('Country', '@alpha_3'),
                    ('Stat', f"@{select.value}")
                ]
            )
            tooltips = """
            <div style="display:flex">
                <div>
                    <img
                    src='https://static.dwcdn.net/css/flag-icons/flags/4x3/@{alpha_2}.svg'
                    height='42'
                    width='42'>
                    </img>
                </div>
                <div>
                        <h4>Date: </h4> @{Date}
                        <h4>Country: </h4> @{Country/Region}
                        <h4>Population: </h4> @{POPULATION}
                        <h4>Covid 19 Confirmed Cases: </h4> @{Confirmed}
                        <h4>Covid 19 Active Cases: </h4> @{Active}
                        <h4>Covid 19 Deaths: </h4> @{Deaths}
                        <h4>Covid 19 Recovered: </h4> @{Recovered}
                <div>
            </div
            """

            color_bar = ColorBar(
                color_mapper=color_mapper,
                label_standoff=10,
                border_line_color=None,
                location=(0,0),
                orientation='horizontal'
            )
            p = figure(
                name="basic_map",
                title="basic chloropeth map testing 123..",
                toolbar_location=None,
                tooltips=tooltips,
                y_axis_type='mercator',
                x_axis_type='mercator'
            )
            p.xgrid.grid_line_color = None
            p.ygrid.grid_line_color = None
            p.patches(
                'xs',
                'ys',
                source=src,
                fill_color={
                    'field': select.value,
                    'transform': color_mapper
                },
                line_color='black',
                line_width=1,
                fill_alpha=1
            )
            p.add_layout(color_bar, 'below')
            self.plot = p 

            return p

        def make_div():
            return Div(
                text="Testing a Div"
            )

        return layout(
            name="chloropeth_map",
            children=[
                [ slider, select ], 
                [ make_plot(), ]       
            ]
        )


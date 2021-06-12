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
import pandas as pd 

sys.path.append(".")

class DataOverview():
    def __init__(self, db: pd.core.frame.DataFrame):
        self.dayrange = 100
        self.db = db
        # self.db = datasources.daywisedb(
        #     datasources.groupdb(
        #         datasources.fixtures(
        #             datasources.fulldb()[0]
        #         )
        #     )   
        # )
        self.describe = self.db.describe().reset_index()
        self.source = ColumnDataSource(self.describe)
        self.original = self.db.copy(deep=True)
        self.db = self.db[['Date', 'Deaths', 'Recovered', 'Active']] \
            .tail(self.dayrange) \
            .melt(id_vars='Date', value_vars=['Active', 'Deaths', 'Recovered']) \
            .groupby(['variable']) \
            .sum() \
            .reset_index()
        self.db['angle'] = self.db['value'] / self.db['value'].sum() * 2*pi
        self.db['color'] = Category20c[len(self.db)]
        self.numrows = 100
        self.column_names = self.db.columns

    def update(self, attr, prev, val):
        print(
            f"received update request from {attr} from {datetime.fromtimestamp(prev[0]/1000)} and {datetime.fromtimestamp(prev[1]/1000)} to {datetime.fromtimestamp(val[0]/1000)} and {datetime.fromtimestamp(val[1]/1000)}")
        df = self.original.copy(deep=True)
        start_date, end_date = val
        print(f"debug values: {start_date} {end_date}")
        #update df based on dates 
        # awkward workaround https://github.com/bokeh/bokeh/issues/6895
        mask = (df['Date'] > datetime.fromtimestamp(start_date/1000) ) & (df['Date'] <= datetime.fromtimestamp(end_date/1000) )
        df = df.loc[mask]
        db = df 
        describe = db.describe().reset_index()
        self.source = ColumnDataSource(describe)
        self.data_table.source = ColumnDataSource(describe)
        print('ok, made it to the end with no error')
        print(self.source.data['Deaths'])


    def layout(self, title):
        print(self.source.data)
        div = Div(
            text="""
            <h1>This can be a dynamic value, but it is it properly aligned?</h1>
            """
        )
        slider = DateRangeSlider(
            title='test_slider',
            name='test_slider',
            start=self.original.Date.min().date(),
            end=self.original.Date.max().date(),
            value=(
                self.original.Date.min().date(),
                self.original.Date.max().date(),
            ),
            format="%Y %m %d"
        )

        def make_div():
            data = self.original
            print('making initial DIV')
            return Div(
                text=f"""
                Global Covid-19 Stats for all time
                """
            )

        def update_div(attr, old, new):
            print('making DIV')
            div = Div(
                text=f"""
                Global Covid-19 Stats between {datetime.fromtimestamp(new[0]/1000)} and {datetime.fromtimestamp(new[1]/1000)}
                """
            )
            self.layout.children[0].children[1] = div


        def make_plot():
            print("render initial plot..")
            db = self.original.copy(deep=True)
            mask = (db['Date'] > datetime.fromtimestamp(slider.value[0]/1000)
                    ) & (db['Date'] <= datetime.fromtimestamp(slider.value[1]/1000))
            db = db.loc[mask]
            db = db[['Date', 'Deaths', 'Recovered', 'Active']] \
                .tail(self.dayrange) \
                .melt(id_vars='Date', value_vars=['Active', 'Deaths', 'Recovered']) \
                .groupby(['variable']) \
                .sum() \
                .reset_index()
            db['angle'] = db['value'] / db['value'].sum() * 2*pi
            db['color'] = Category20c[len(db)]

            plot = figure(
                name='overview_plot',
                title=title,
                toolbar_location=None,
                tools="hover",
                tooltips=f"@variable: @value",
            )
            plot.annular_wedge(
                x=0,
                y=1,
                inner_radius=0.15,
                outer_radius=0.25,
                direction='anticlock',
                start_angle=cumsum(
                    'angle', 
                    include_zero=True
                ),
                end_angle=cumsum('angle'),
                line_color='white',
                fill_color='color',
                legend='variable',
                source=db
            )
            return plot 

        def update_plot(attr, old, new):
            print(f"updating plot due to change in {attr} from old vals {old} to new vals {new}")
            db = self.original.copy(deep=True)
            mask = (db['Date'] > datetime.fromtimestamp(new[0]/1000)
                    ) & (db['Date'] <= datetime.fromtimestamp(new[1]/1000))
            db = db.loc[mask]
            db = db[['Date', 'Deaths', 'Recovered', 'Active']] \
                .tail(self.dayrange) \
                .melt(id_vars='Date', value_vars=['Active', 'Deaths', 'Recovered']) \
                .groupby(['variable']) \
                .sum() \
                .reset_index()
            db['angle'] = db['value'] / db['value'].sum() * 2*pi
            db['color'] = Category20c[len(db)]

            plot = figure(
                name='overview_plot',
                title=title,
                toolbar_location=None,
                tools="hover",
                tooltips=f"@variable: @value",
            )
            plot.annular_wedge(
                x=0,
                y=1,
                inner_radius=0.15,
                outer_radius=0.25,
                direction='anticlock',
                start_angle=cumsum(
                    'angle', 
                    include_zero=True
                ),
                end_angle=cumsum('angle'),
                line_color='black',
                fill_color='color',
                legend='variable',
                source=db
            )
            self.layout.children[0].children[0] = plot
            return plot 

        num_format = NumberFormatter(format='0.0a')
        cols = [ TableColumn(field=i, name=i, formatter=num_format) for i in self.describe.columns if i != 'index' ]
        cols.insert(
            0,
            TableColumn(field='index', name='index')
        )
        data_table = DataTable(
            name="overview_table_description",
            # autosize_mode="fit_viewport",
            #columns=self.columns,
            columns=cols,
            source=self.source,
            index_header="Statistic",
            #sizing_mode="scale_both",
            #fit_columns=True,
            sortable=True,
            # css_classes=[
            #     'table',
            # ]
        )



        self.data_table = data_table 
        print(type(self.source))
        slider.on_change("value", self.update)
        slider.js_on_change("value", CustomJS( args=dict(source=self.source, data_table=self.data_table) , code="""
        var data = source.data;
        var selection = cb_obj.value;
        console.log(data);
        console.log(selection);
        for (var key in data) {
            console.log('found key: ' + key);
            console.log('key entries: ' + data[key])
        }
        """))
        slider.on_change("value", update_plot)
        slider.on_change("value", update_div)
        #data_table.source.on_change('data')
        

        page_layout = layout(
            name="overview_panel",
            spacing=10,
            sizing_mode='scale_both',
            background='#1E2C2EEE',
            margin=(5,5,5,5),
            # css_classes=[
            #     'table'
            # ],
            children=[
                [make_plot(), make_div(), slider],
                [data_table,],
            ]
        )
        self.layout = page_layout
        return page_layout


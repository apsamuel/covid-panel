from . import datasources
from datetime import date, datetime, timedelta
from bokeh.tile_providers import get_provider, WIKIMEDIA, CARTODBPOSITRON, STAMEN_TERRAIN, STAMEN_TONER, ESRI_IMAGERY, OSM


from bokeh.transform import cumsum, factor_cmap
from bokeh.palettes import *
#from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c
from bokeh.layouts import widgetbox, layout, column, row
from bokeh.models import LinearColorMapper, LogColorMapper
from bokeh.models import ColumnDataSource, GeoJSONDataSource, TableColumn, DataTable
from bokeh.models import CustomJS, Spinner
from bokeh.models import DateFormatter, HTMLTemplateFormatter, DatetimeTickFormatter, NumeralTickFormatter, MonthsTicker, YearsTicker
from bokeh.plotting import figure

from bokeh.models.widgets import Panel, Tabs, TableColumn
from bokeh.models import CustomJS, Select
#from bokeh.themes import built_in_themes
import warnings
warnings.filterwarnings('ignore')
from operator import ge
import sys, os
from copy import copy
import pandas as pd 

sys.path.append(".")

class FullDataTable():
    def __init__(self, db: pd.core.frame.DataFrame):
        self.db = db
        self.numrows = 100
        self.source = ColumnDataSource(self.db)
        self.original = ColumnDataSource(self.db)
        self.countries = list(self.db['Country/Region'].unique()) + ["all"]
        self.columns = [ TableColumn(field=i, name=i) for i in list(self.db.columns) ]

    
    def update_source(self, attr, prev, val):
        print(f"updating column data source to reflect change in {attr} previous: {prev} current: {val}")

    def refresh_source(self, attr, prev, val):
        print(f"refreshing sources after change in {attr} previous: {prev} current: {val}")
        self.db = datasources.fixtures(
            datasources.fulldb()[0]
        )
        self.source = ColumnDataSource(self.db)



    def layout(self):

        def debug_select(attr, old, new):
            print("Attribute: " + attr)
            print("Previous label: " + old)
            print("Updated label: " + new)
        date_format = DateFormatter(format='RFC-1123')
        count_format = HTMLTemplateFormatter(template="""
        <div 
            style="background:<%=
            (function setBackground(){
                if(value >= 0 && value <= 2500) {
                    return("green");
                }; 
                if(value >= 2500 && value <= 50000) {
                    return("yellow");
                }
                if(value >=50001) {
                    return("red");
                }
            }()) 
            %>;
            color: black">
            <%= value %>
        </div>
        """)
        cols = [
            TableColumn(field='Province/State', name='Province/State'),
            TableColumn(field='Country/Region', name='Country/Region'), 
            TableColumn(field='Lat', name='Lat'),
            TableColumn(field='Long', name='Long'),
            TableColumn(field='Date', name='Date', formatter=date_format),
            TableColumn(field='Confirmed', name='Confirmed', formatter=count_format),
            TableColumn(field='Deaths', name='Deaths', formatter=count_format),
            TableColumn(field='Recovered', name='Recovered'),
            TableColumn(field='Active', name='Active', formatter=count_format),
            TableColumn(field='WHO Region', name='WHO Region')
        ]
        
        data_table = DataTable(
            name="full_table_data",
            autosize_mode="fit_viewport",
            columns=cols,
            source=self.source,
            index_header="Record No.",
            sizing_mode="stretch_both",
            sortable=True,
            css_classes=[
                'table_data'
            ]

        )
        self.data_table = data_table
        #select drop down for countries
        select = Select(
            name="full_table_select",
            title="Select Country:",
            value="Cuba",
            options=self.countries
        )

        select.js_on_change("value", CustomJS(args=dict(source=self.source, test='hello world', orig = self.original,obj=self.data_table),code="""
        var data = source.data;
        var idx = data['index'].length;
        var selection = cb_obj.value ;
        var obj = obj;

        console.log('selected country: ' + selection);
        //var orig = JSON.parse(JSON.stringify(source.data));

        console.log('used data');
        console.log(source.data);
        console.log('original data:');
        console.log(orig.data);

        var filtered = {};
        for (var key in data) {
            filtered[key] = []
        }


        var {  
            'Province/State': states , 
            'Country/Region' : countries, 
            'Lat': lats, 
            'Long': lons, 
            'Date' : dates, 
            'Confirmed': confirmeds, 
            'Deaths': deaths, 
            'Recovered': recovereds, 
            'Active': actives, 
            'WHO Region': whos  
        } = data; 
        for (var i=0; i < idx; i++) {
            // validate country if all is selected show original data source
            if (selection=='all') {
                //source.data = orig;
                break;
            }
            if (countries[i]==selection ) {
                //console.log('located selection at row index ' + i + ' with value ' + countries[i]);
                // for each key in original array
                for (var key in data) {
                    //push original values to new key arrays 
                    filtered[key].push(data[key][i]);
                }
            }
        }
        
        //try updating source with filtered data, check if selection is all
        if (selection != 'all') {
            source.data = filtered;
        } else {
            source.data = orig.data;
        }
        
        console.log(source.data);
        console.log('original after changes');
        console.log(orig.data)
        source.change.emit()
        obj.change.emit()
        """))
        select.on_change("value", self.refresh_source)

        page_layout = layout(
            children=[
                [select, ],
                [data_table, ],
            ],
            #sizing_mode='scale_both',
            name='full_table',

        )
        #select = "Testing"
        
        return page_layout



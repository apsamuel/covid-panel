from bokeh.models.filters import GroupFilter
from bokeh.models.widgets.inputs import MultiChoice, MultiSelect
from numpy import source
from . import datasources
from datetime import date, datetime, timedelta
from bokeh.tile_providers import get_provider, WIKIMEDIA, CARTODBPOSITRON, STAMEN_TERRAIN, STAMEN_TONER, ESRI_IMAGERY, OSM


from bokeh.transform import cumsum, factor_cmap
from bokeh.palettes import *
#from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c
from bokeh.layouts import widgetbox, layout, column, row
from bokeh.models import LinearColorMapper, LogColorMapper
from bokeh.models import ColumnDataSource, GeoJSONDataSource, TableColumn, DataTable, BooleanFilter, CDSView
from bokeh.models import CustomJS, Spinner
from bokeh.models import DateFormatter, HTMLTemplateFormatter, DatetimeTickFormatter, NumeralTickFormatter, MonthsTicker, YearsTicker
from bokeh.models.widgets import DateSlider, DateRangeSlider
from bokeh.plotting import figure

from bokeh.models.widgets import Panel, Tabs, TableColumn
from bokeh.models import CustomJS, Select
#from bokeh.themes import built_in_themes
import warnings
warnings.filterwarnings('ignore')
from operator import ge, mul
import sys, os
from copy import copy
import pandas as pd 

from .loginator import Loginator 





#logging
log = logging.getLogger(__name__)
logger = Loginator(
    logger=log,
    lvl='DEBUG'
).logger

sys.path.append(".")

class FullDataTable():
    def __init__(self, db: pd.core.frame.DataFrame):
        self.db = db
        self.numrows = 100
        self.source = ColumnDataSource(self.db)
        self.original = ColumnDataSource(self.db)
        self.countries = list(self.db['Country/Region'].unique()) + ["all"]
        self.columns = [ TableColumn(field=i, name=i) for i in list(self.db.columns) ]
        self.country = ['United States']
        self.date_start = self.db.Date.min().date() + timedelta(days=300)
        self.date_end = self.db.Date.max().date()
        logger.debug("[FullDataTable] Initialized an instance..")

    
    def update_source(self, attr, prev, val):
        logger.debug(f"[FullDataTable] updating column data source to reflect change in {attr} previous: {prev} current: {val}")

    def refresh_source(self, attr, prev, val):
        logger.debug(
            f"[FullDataTable] refreshing CDS sources after a change in {attr} from previous: {prev} to current: {val}")
        db = self.db.copy(deep=True)
        source = ColumnDataSource(db)
        self.data_table.source = source



    def layout(self):
        """
        Generates page layout object for JHU Global Full Data Table COVID-19 data
        """

        slider = DateRangeSlider(
            title='Select Date Range:',
            name='full_table_slider',
            step=100,
            start=self.db.Date.min().date(),
            end=self.db.Date.max().date(),
            value=(
                self.db.Date.min().date() + timedelta(days=300),
                self.db.Date.max().date(),
            ),
            format="%Y %m %d"
        )
        self.slider = slider 

        select = Select(
            name="full_table_select",
            title="Select Country:",
            value="United States",
            options=self.countries + ['all']
        )
        self.select = select 

        multiselect = MultiChoice(
            name='full_table_multiselect',
            title='Select Countries: ',
            value=[
                'United States'
            ],
            options=self.countries + ['all']
        )

        def make_plot():
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
            db = self.db.copy(deep=True)
            logger.debug(f"[FullDataTable] full DB is {db.shape[0]} rows")
            # try using multiselect
            if 'all' in multiselect.value: 
                logger.debug('[FullDataTable] "all" is present in the multiselect, providing all Country/Region values')
                source = ColumnDataSource(db)
            else:
                logger.debug(f"[FullDataTable] selecting db values with Country/Region contained in {multiselect.value}")
                db = db[
                    db['Country/Region'].isin(
                        multiselect.value
                    )
                ]
                source = ColumnDataSource(db)

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
            logger.debug('[FullDataTable] Creating a default CDS View for full data table ...')
            view = CDSView(
                source=source, 
                filters=[
                    BooleanFilter([
                        True if (date.to_pydatetime() > datetime.fromtimestamp(slider.value[0]/1000)) & (date.to_pydatetime() < datetime.fromtimestamp(slider.value[1]/1000)) else False for date in db.Date
                    ]),
                ]
            )
            logger.debug('[FullDataTable] updating class variable view with new value view for full data table')
            self.view = view 
            
            data_table = DataTable(
                name="full_table_data",
                autosize_mode="fit_viewport",
                columns=cols,
                source=source,
                view=view,
                index_header="Record No.",
                sizing_mode="stretch_both",
                sortable=True,
                css_classes=[
                    'table_data'
                ]
            )
            self.data_table = data_table
            return data_table 


        def update_country(attr, old, new):
            country = new
            start_date = self.date_start 
            end_date = self.date_end
            logger.debug(f"[FullDataTable] class variable value for current date_start and date_end are: {self.date_start} {type(self.date_start)} to {self.date_end} {type(self.date_end)}")
            print('ok')
            logger.debug(
                f"[FullDataTable] updating {attr} because of change in multiselect values from {old} to {new}")
            db = self.db.copy(deep=True)

            # filter countries if all is not in list
            if 'all' not in country: 
                db = db[
                    db['Country/Region'].isin(
                        country
                    )
                ]
            # if country != 'all':
            #     cntmask = db['Country/Region'] == country
            #     db = db.loc[cntmask]

            # date mask
            # apply date mask per current date selection
            datemask = (db.Date.dt.date > start_date) & (
                db.Date.dt.date < end_date)
            db = db.loc[datemask]
            source = ColumnDataSource(db)
            logger.debug(f"[FullDataTable] sliced DB is {db.shape[0]} rows")
            logger.debug(
                '[FullDataTable] finished creating the updated CDS View for table in response to slider event')
            #self.data_table.view = view
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
                TableColumn(field='Confirmed', name='Confirmed',
                            formatter=count_format),
                TableColumn(field='Deaths', name='Deaths',
                            formatter=count_format),
                TableColumn(field='Recovered', name='Recovered'),
                TableColumn(field='Active', name='Active',
                            formatter=count_format),
                TableColumn(field='WHO Region', name='WHO Region')
            ]

            data_table = DataTable(
                name="full_table_data",
                autosize_mode="fit_viewport",
                columns=cols,
                source=source,
                #view=view,
                index_header="Record No.",
                sizing_mode="stretch_both",
                sortable=True,
                css_classes=[
                    'table_data'
                ]
            )
            self.layout.children[1].children[0] = data_table
            self.data_table = data_table 
            self.country = new
            return data_table




        def update_date2(attr, old, new):
            logger.debug("update date redux")
            logger.debug(
                f"[FullDataTable] updating {attr} because of change in slider values from {datetime.fromtimestamp(old[0]/1000)} - {datetime.fromtimestamp(old[1]/1000)} to {datetime.fromtimestamp(new[0]/1000)} - {datetime.fromtimestamp(new[1]/1000)}")
            date_start = datetime.fromtimestamp(new[0]/1000)
            date_end = datetime.fromtimestamp(new[1]/1000)
            filter = BooleanFilter([
                True if (date.to_pydatetime() > date_start) & (date.to_pydatetime() < date_end) else False for date in self.db.Date
            ])
            #self.layout.children[1].children[0].view.filters = [] 
            self.layout.children[1].children[0].view.filters = [filter]

        def update_date(attr, old, new):
            old_start_date = datetime.fromtimestamp(old[0]/1000).date()
            old_end_date = datetime.fromtimestamp(old[1]/1000).date()
            start_date = datetime.fromtimestamp(new[0]/1000).date()
            end_date = datetime.fromtimestamp(new[1]/1000).date()
            country = self.country
            print(f"[FullDataTable] OLD VALUES: {old_start_date} - {old_end_date} NEW VALUES: {start_date} - {end_date} {country}")

            logger.debug(f"[FullDataTable] testing class value for country {self.country}")
            logger.debug(f"[FullDataTable] updating {attr} because of change in slider values from {datetime.fromtimestamp(old[0]/1000)} - {datetime.fromtimestamp(old[1]/1000)} to {datetime.fromtimestamp(new[0]/1000)} - {datetime.fromtimestamp(new[1]/1000)}")
            db = self.db.copy(deep=True)

            # country mask
            if 'all' not in country:
                db = db[
                    db['Country/Region'].isin(
                        country
                    )
                ]
            # if country != 'all': 
            #     cntmask = db['Country/Region'] == country
            #     db = db.loc[cntmask]

            # date mask
            datemask = (db.Date.dt.date > start_date) & (db.Date.dt.date < end_date)
            db = db.loc[datemask]
            # if self.country == None or self.country == 'all':
            #     logger.debug(
            #         f"Setting datasource to full DB as all or None is selected {self.country} ")
            #     #source = ColumnDataSource(db)
            # else:
            #     logger.debug(f"Slicing Data based on selection {self.country}")
            #     db = db[db['Country/Region'] ==
            #             self.country].reset_index(drop=True)
            #     logger.debug(f"Sliced DB is {db.shape[0]} rows")
                #logger.debug(db)
            source = ColumnDataSource(db)
            
            #source = ColumnDataSource(db)
            logger.debug('[FullDataTable] creating the updated CDS View for table in response to slider event')
            if self.country != None:
                logger.debug('[FullDataTable] creating view in not None branch')
                view = CDSView(
                    source=source,
                    filters=[
                        BooleanFilter([
                            True if (date.to_pydatetime().date() > start_date) & (date.to_pydatetime().date() < end_date) else False for date in self.db.Date
                        ]),
                        #GroupFilter(column_name='Country/Region', group=self.country)
                    ]
                )
            else:
                logger.debug('[FullDataTable] creating view in None branch')
                view = CDSView(
                    source=source,
                    filters=[
                        BooleanFilter([
                            True if (date.to_pydatetime().date() > datetime.fromtimestamp(new[0]/1000).date()) & (date.to_pydatetime().date() < datetime.fromtimestamp(new[1]/1000).date()) else False for date in self.db.Date
                        ]),
                    ]
                )
            logger.debug(
                '[FullDataTable] finished creating the updated CDS View for table in response to slider event')
            self.data_table.view = view  
            #logger.debug(f"child is: {self.layout.children[1].children[0]}"  )
            logger.debug('[FullDataTable] Updating view in UI...')
            self.layout.children[1].children[0].source = source
            self.layout.children[1].children[0].view = view 
            logger.debug('[FullDataTable] done..')


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
                TableColumn(field='Confirmed', name='Confirmed',
                            formatter=count_format),
                TableColumn(field='Deaths', name='Deaths',
                            formatter=count_format),
                TableColumn(field='Recovered', name='Recovered'),
                TableColumn(field='Active', name='Active',
                            formatter=count_format),
                TableColumn(field='WHO Region', name='WHO Region')
            ]

            data_table = DataTable(
                name="full_table_data",
                autosize_mode="fit_viewport",
                columns=cols,
                source=source,
                #view=view,
                index_header="Record No.",
                sizing_mode="stretch_both",
                sortable=True,
                css_classes=[
                    'table_data'
                ]
            )
            self.layout.children[1].children[0] = data_table
            self.data_table = data_table
            self.date_start = datetime.fromtimestamp(new[0]/1000).date()
            self.date_end = datetime.fromtimestamp(new[1]/1000).date()
            return view

        slider.on_change('value', update_date)





        #select drop down for countries


        # select.js_on_change("value", CustomJS(args=dict(source=self.source, test='hello world', orig = self.original,obj=make_plot()),code="""
        # var data = source.data;
        # var idx = data['index'].length;
        # var selection = cb_obj.value ;
        # var obj = obj;

        # console.log('selected country: ' + selection);
        # //var orig = JSON.parse(JSON.stringify(source.data));

        # console.log('used data');
        # console.log(source.data);
        # console.log('original data:');
        # console.log(orig.data);

        # var filtered = {};
        # for (var key in data) {
        #     filtered[key] = []
        # }


        # var {  
        #     'Province/State': states , 
        #     'Country/Region' : countries, 
        #     'Lat': lats, 
        #     'Long': lons, 
        #     'Date' : dates, 
        #     'Confirmed': confirmeds, 
        #     'Deaths': deaths, 
        #     'Recovered': recovereds, 
        #     'Active': actives, 
        #     'WHO Region': whos  
        # } = data; 
        # for (var i=0; i < idx; i++) {
        #     // validate country if all is selected show original data source
        #     if (selection=='all') {
        #         //source.data = orig;
        #         break;
        #     }
        #     if (countries[i]==selection ) {
        #         //console.log('located selection at row index ' + i + ' with value ' + countries[i]);
        #         // for each key in original array
        #         for (var key in data) {
        #             //push original values to new key arrays 
        #             filtered[key].push(data[key][i]);
        #         }
        #     }
        # }
        
        # //try updating source with filtered data, check if selection is all
        # if (selection != 'all') {
        #     source.data = filtered;
        # } else {
        #     source.data = orig.data;
        # }
        
        # console.log(source.data);
        # console.log('original after changes');
        # console.log(orig.data)
        # source.change.emit()
        # obj.change.emit()
        # """))
        #select.on_change("value",update_country)
        multiselect.on_change("value", update_country)

        page_layout = layout(
            children=[
                [multiselect, slider],
                [make_plot(), ],
            ],
            #sizing_mode='scale_both',
            name='full_table',

        )
        self.layout = page_layout
        #select = "Testing"
        
        return page_layout



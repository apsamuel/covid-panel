
# import .datasources
#import datasources as datasources
from operator import ge
import sys
import os
sys.path.append(".")
import warnings
import pandas as pd
from ipysheet import sheet, cell, cell_range #column, row
import ipywidgets as widgets
from ipywidgets import Button, Layout, interact
from IPython.core.display import display, HTML
import panel as pn

# need to replace panels with bokeh widgets 
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import column, row
import param
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.io import output_file, push_notebook, output_notebook, show, export_png
from bokeh.models import CustomJS, DateFormatter, DatetimeTickFormatter, MonthsTicker, YearsTicker, ColorBar, NumeralTickFormatter, HoverTool
from bokeh.models import ColumnDataSource, GeoJSONDataSource, TableColumn, DataTable
from bokeh.models import LinearColorMapper, LogColorMapper
from bokeh.layouts import widgetbox
from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c
from bokeh.palettes import *
from bokeh.transform import cumsum, factor_cmap
from bokeh.models.tools import HoverTool
from bokeh.tile_providers import get_provider, WIKIMEDIA, CARTODBPOSITRON, STAMEN_TERRAIN, STAMEN_TONER, ESRI_IMAGERY, OSM
from geopy.geocoders import Nominatim
from pyproj import Proj, transform
from datetime import date, datetime, timedelta

from . import datasources
#from lib import genericCountry
# lib directory such that other libs can use each other
#
#mapping and cartography
# for date and time functions


#display(HTML("<style>div.output_scroll { height: 100em; }</style>"))


#df_full = pd.read_csv('data/fulldb.csv')
#df_full.head(10)
class genericCountry(param.Parameterized):


    df_full = datasources.fixtures(
        datasources.fulldb()[0]
    )
    #df_full = datasources.fulldb()[0]
    #title = param.String(default="General Data")
    #country = param.String(default=country_widget.value)
    #df_full = df_in
    countries = df_full['Country/Region'].unique()
    country = param.Selector(default='Cuba', objects=countries)
    #country = param.ObjectSelector(default='Cuba', objects=['Cuba','China', 'Iraq', 'France'])
    dataset = param.DataFrame(default=df_full)
    rows = param.Integer(default=100, bounds=(1, 1000))
    height = param.Integer(default=300)
    width = param.Integer(default=1500)
    x_axis_type = param.String(default="datetime")
    datapoints = param.Array(default=np.asarray(
        ['Confirmed', 'Deaths', 'Recovered', 'Active']))

    @param.depends('dataset', 'country', watch=True)
    def data(self):
        # return self.dataset[self.dataset['Country/Region']==country_widget.value]
        return self.dataset[self.dataset['Country/Region'] == self.country]

    @param.depends('data', watch=False)
    def summary(self):
        # return self.data().drop(['Lat','Long'], axis=1).describe()
        df_widget = pn.widgets.DataFrame(self.data().drop(
            ['Lat', 'Long'], axis=1).describe(), name='DataFrame')
        return df_widget

    @param.depends('country', watch=False)
    def header(self):
        return f"## Country Card: {self.country}"

    @param.depends('data', 'rows', watch=False)
    def table(self):
        return self.data().iloc[:self.rows]

    @param.depends('data', 'height', 'width', watch=False)
    def plot(self):
        s = ColumnDataSource(self.data())
        p = figure(
            x_axis_type=self.x_axis_type,
            plot_width=self.width,
            plot_height=self.height,
        )
        for idx, datapoint in enumerate(self.datapoints):

            l = str(self.datapoints[idx])

            p.line(
                x=self.data()['Date'],
                y=self.data()[self.datapoints[idx]],
                legend=l,

                line_width=2,
                line_color=Viridis256[idx*50]
            )
        p.xaxis.formatter = DatetimeTickFormatter(
            years="%Y/%m/%d"
        )
        return p

    @param.depends('country')
    def view(self):
        iframe = """
        <iframe width="800" height="400" src="https://maps.google.com/maps?q={country}&z=6&output=embed"
        frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe>
        """.format(country=self.country)
        return pn.pane.HTML(iframe, height=400, sizing_mode='stretch_width')

    @param.depends('data', 'country')
    def panel(self):

        ntabs = Tabs()
        sumcol = column(
            children = [
                row(
                    children = [
                        self.param.country,
                        self.header,
                        self.summary
                    ],
                    sizing_mode = 'stretch_both'
                )
            ],
            sizing_mode = 'stretch_both'
        )
        plotcol = column(
            children=[
                row(
                    children=[
                        self.param.country,
                        self.header,
                        self.plot
                    ],
                    sizing_mode='stretch_both'
                )
            ],
            sizing_mode='stretch_both'
        )
        mapcol = column(
            children=[
                row(
                    children=[
                        self.view
                    ],
                    sizing_mode='stretch_both'
                )
            ],
            sizing_mode='stretch_both'
        )
        ntabs.tabs = [
            Panel(child=sumcol),
            Panel(child=plotcol),
            Panel(child=mapcol)
        ]
        # tabs = pn.Tabs(
        #     css_classes=['panel-widget-box'],
        #     sizing_mode='stretch_both'
        # )
        # tabs.append(
        #     ('Summary', pn.Column(
        #         pn.Row(self.param.country, sizing_mode='stretch_both'),
        #         pn.Row(self.header, margin=(25, 50, 75, 100), css_classes=[
        #                'panel-widget-box'], sizing_mode='stretch_both'),
        #         pn.Row(self.summary, margin=(25, 50, 75, 100), css_classes=[
        #                'panel-widget-box'], sizing_mode='stretch_both'),
        #     ))
        # )
        # tabs.append(
        #     ('Plot', pn.Column(
        #         pn.Row(self.param.country, sizing_mode='stretch_both'),
        #         pn.Row(self.header, margin=(25, 50, 75, 100), css_classes=[
        #                'panel-widget-box'], sizing_mode='stretch_both'),
        #         pn.Row(self.plot, margin=(25, 50, 75, 100)),
        #         css_classes=['panel-widget-box'],
        #         sizing_mode='stretch_both'
        #     ))
        # )
        # tabs.append(
        #     ('Google Map', pn.Column(
        #         pn.Row(self.view)
        #     ))
        # )

        return ntabs


#r = genericCountry(dataset=df_full, )
# r.panel().servable()

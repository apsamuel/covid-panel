"""choroplethMap Placeholder
- name should be chloropeth_map
"""
#from re import I
import sys
import logging
import warnings

#from datetime import (
#    #date,
#    datetime,
#    #timedelta
#)
import datetime as dt
import bokeh
import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure

from bokeh.models import (
    #CustomJS,
    Select, )
from bokeh.models.tools import HoverTool
from bokeh.models.annotations import ColorBar
from bokeh.transform import (
    cumsum,
    factor_cmap,
)
from bokeh.palettes import (
    Reds256,
    Blues256,
)
from bokeh.layouts import (
    gridplot,
    widgetbox,
    layout,
    #Column,
    #Row,
    #LayoutDOM,
)
from bokeh.models import (
    LinearColorMapper,
    #LogColorMapper
)
from bokeh.models import (
    #ColumnDataSource,
    #DataTable,
    GeoJSONDataSource,
    #TableColumn,
)
#from bokeh.models.widgets.markups import (Div)
from bokeh.models.widgets import (
    DateSlider,
    #DateRangeSlider,
)
from lib.loginator import Loginator
from . import datasources

#from math import pi

#from bokeh.palettes import Spectral3, Spectral5, Viridis256, Category20c

# from bokeh.models import (
#     CustomJS,
#     Spinner
# )
from bokeh.models import (
    DateFormatter,
    NumberFormatter,
    HTMLTemplateFormatter,
    DatetimeTickFormatter,
    NumeralTickFormatter,
    MonthsTicker,
    YearsTicker
)

#from bokeh.themes import built_in_themes

warnings.filterwarnings('ignore')
#from operator import ge
#import sys #, os
#from copy import copy

log = logging.getLogger(__name__)
logger = Loginator(logger=log).logger
logger.info("This is an INFO message...")

sys.path.append(".")


class ChoroplethMapOptions():
    """Choropleth Map Options"""
    def __init__(self,
                 day: dt.datetime = None,
                 default_palette: tuple = None,
                 default_nan_color: str = None,
                 columns: list = None,
                 default_statistic: str = None,
                 data_type: str = None,
                 admin_level: str = None) -> None:
        """
        Parameters
        ----------
        day: geopandas..
            the base URL for the request
        default_palette: tuple
            blah
        columns: list
            blah blah blah
        default_statistic: str
            blah
        data_type: str
            blah
        admin_level: str
            blah

        Returns
        ----------
        ChoroplethMapOptions
        """
        self.day = day
        if default_palette is None:
            self.default_palette = Reds256[::-1]
        else:
            self.default_palette = default_palette[::-1]

        if data_type is None:
            self.data_type = 'stringency'
        else:
            self.data_type = data_type

        if self.data_type == 'stringency' and columns is None:
            self.columns = [
                'alpha_2',
                'alpha_3',
                'AREA KM2',
                'ConfirmedCases',
                'ConfirmedDeaths',
                'ContainmentHealthIndex',
                'Country/Region',
                'CountryName',
                'Date',
                'ECONOMY',
                'GDP $USD',
                'GovernmentResponseIndex',
                'INCOME_GRP',
                'Jurisdiction',
                'Official Name',
                'POPULATION',
                'RegionName',
                'StringencyIndex',
                'SUBREGION',
            ]
        else:
            self.columns = columns
        if admin_level is None:
            self.admin_level = 'admin_0'
        else:
            self.admin_level = admin_level
        #self.default_statistic = default_statistic
        if default_statistic is None:
            self.default_statistic = 'ConfirmedCases'
        if default_nan_color is None:
            self.default_nan_color = '#363636'
        else:
            self.default_nan_color = default_nan_color

    def set_day(self, day: dt.datetime = None):
        """Sets Day"""
        self.day = day

    def set_columns(self, value: list = None):
        """Sets Columns"""
        self.columns = value

    def set_default_statistic(self, value: str = None):
        """Sets Default Statistic"""
        self.default_statistic = value

    def set_default_nan_color(self, value: str = None):
        """Sets Nan Color"""
        self.default_nan_color = value

    def set_data_type(self, value: str = None):
        """Sets Data Type"""
        self.data_type = value


class ChoroplethMap():
    """A choropleth map
    χῶρος - choros 'area/region'
    πλῆθος - plethos 'multitude'
    thematic map in which a set of pre-defined areas is colored
    or patterned in proportion to a statistical variable
    """
    def __init__(self,
                 data_frame: pd.core.frame.DataFrame,
                 plot_options: ChoroplethMapOptions = None):
        """
        Parameters
        ----------
        base: pd.core.frame.DataFrame
            the base URL for the request
        plot_options: ChoroplethMapOptions
            the path to the timeseries file

        Returns
        ----------
        pd.DataFrame - A pandas DataFrame
        """
        self.plot_options = plot_options
        # parse out rows with NaN-like Date
        self.data_frame = data_frame[~(data_frame.Date.isna())]
        if self.plot_options.day is None:
            self.day = self.data_frame.Date.max().date()
        else:
            self.day = self.plot_options.day

        self.data_type = self.plot_options.data_type

        self.columns = self.plot_options.columns

        if plot_options.default_statistic is None and plot_options.data_type == 'stringency':
            self.statistic = 'Active'
        else:
            self.statistic = self.plot_options.default_statistic

        self.select = Select(
            name='choro_select_widget',
            title='Select a collected statistic to visualize:',
            options=[
                'Active',
                'Confirmed',
                'Deaths',
                'Recovered',
            ],
            value='Active',
        )

        self.slider = DateSlider(
            name='choro_slider_widget',
            title='Select a day within the statistical time range:',
            #unpack timetuple as args for dt.datetime
            start=dt.datetime(
                *self.data_frame.Date.min().date().timetuple()[:6]),
            value=dt.datetime(
                *self.data_frame.Date.mean().date().timetuple()[:6]),
            end=dt.datetime(
                *self.data_frame.Date.max().date().timetuple()[:6]),
            step=1,
        )

    # def controls(self,
    #              ):
    #     """Return controls for plot(s)"""
    #     return layout(
    #         children=[
    #             [self.select, self.slider]
    #         ]
    #     )

    def plot(self,
             selected_day: dt.datetime = None,
             columns: list = None,
             stat: str = None):
        """Placeholder
        """

        # set data and plot options
        data = self.data_frame.copy(deep=True)  # work on a copy of the data
        opts = self.plot_options
        # setup elected day
        if selected_day is None:
            selected_day = self.day

        # setup plotted statistic
        if stat is None:
            stat = opts.default_statistic

        # slice admin_0 data copy by date
        if opts.data_type == 'stringency' and opts.admin_level == 'admin_0':
            # filter by selected_day and general country level data

            title = f"Global Covid-19 Reported {stat} for {selected_day}"
            data = data[(data.Date == pd.Timestamp(selected_day))
                        & (data.RegionName == '')]
            tooltips = [
                ("Date", "@Date"),
                ("Country Name", "@CountryName"),
                ("Region Name", "@RegionName"),
                ("ISO3", "@alpha_3"),
                ("Confirmed Cases", "@ConfirmedCases"),
                ("Confirmed Deaths", "@ConfirmedDeaths"),
                ("Population", "@POPULATION"),
                ("Economy", "@ECONOMY"),
                ("Subregion", "@SUBREGION"),
                ("type", "@type_en"),
            ]
            

        # slice admin_1 data by date
        if opts.data_type == 'stringency' and opts.admin_level == 'admin_1':
            # filter by selected_day and general country level data
            country_name = data['Country/Region'].iloc[0]
            title = f"{country_name} Covid-19 Reported {stat} for {selected_day}"
            data = data[(data.Date == pd.Timestamp(selected_day))
                        & (data.name != '')]

            tooltips = [
                ("Date", "@Date"),
                ("Country Name", "@CountryName"),
                ("Region Name", "@name"),
                ("ISO3", "@alpha_3"),
                ("Confirmed Cases", "@ConfirmedCases"),
                ("Confirmed Deaths", "@ConfirmedDeaths"),
                ("Population", "@POPULATION"),
                ("Economy", "@ECONOMY"),
                ("Subregion", "@SUBREGION"),
                ("type", "@type_en"),
            ]
        # set CDS
        source = GeoJSONDataSource(geojson=data.to_json(
            cls=datasources.PandasTimeStampEncoder))

        # setup tools and annotations
        hover_tool = HoverTool(mode='mouse',
                               point_policy='follow_mouse',
                               tooltips=tooltips,
                               formatters={'Date': 'datetime'})

        color_mapper = LinearColorMapper(
            palette=self.plot_options.default_palette,
            nan_color=self.plot_options.default_nan_color
        )
        color_bar = ColorBar(
            color_mapper=color_mapper,
            label_standoff=10,
            width=500,
            height=20,
            border_line_color=None,
            location=(0, 0),
            orientation='horizontal',
            formatter=NumeralTickFormatter(
                #num_of_ticks=grouped.Recovered.max(),
                format='0.0a'))
        #plot
        fig = figure(
            title=title,
            name='choro_plot',
            x_axis_type='mercator',
            y_axis_type='mercator',
        )
        fig.patches(
            xs='xs',
            ys='ys',
            source=source,
            fill_color={
                'field': self.statistic,
                'transform': color_mapper
            },
            line_color='black',
            line_width=1,
            fill_alpha=1,
        )
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.xaxis.visible = False
        fig.yaxis.visible = False
        fig.add_layout(color_bar, place='below')
        fig.add_tools(hover_tool)
        return fig

    # def layout(self) -> bokeh.models.layouts.Column:
    #     """
    #     Returns a Bokeh Layout Column containing widgets (slider & select) and a chloropleth plot
    #     """
    #     slider = DateRangeSlider(title='map_slider',
    #                             name='map_slider',
    #                             start=self.db.Date.min().date(),
    #                             end=self.db.Date.max().date(),
    #                             value=(
    #                                 self.db.Date.min().date(),
    #                                 self.db.Date.max().date(),
    #                             ),
    #                             format="%Y %m %d")
    #     self.slider = slider
    #     #select drop down for stats
    #     select = Select(name='select_stat',
    #                     title='Select Statistic',
    #                     value='Active',
    #                     options=['Active', 'Confirmed', 'Deaths', 'Recovered'])
    #self.select = select

    # def make_plot():
    #     db = self.db.copy(deep=True)
    #     mask = (db['Date'] > datetime.fromtimestamp(slider.value[0] / 1000)
    #             ) & (db['Date'] <= datetime.fromtimestamp(
    #                 slider.value[1] / 1000))
    #     db = db.loc[mask]
    #     src = GeoJSONDataSource(geojson=db.to_json(
    #         cls=datasources.PandasTimeStampEncoder))
    #     palette = Reds256[::-1]
    #     color_mapper = LinearColorMapper(palette=palette,
    #                                      low=db[select.value].min(),
    #                                      high=db[select.value].max())
    #     hover = HoverTool(
    #         tooltips=[('Date',
    #                    '@Date'), ('Country',
    #                               '@alpha_3'), ('Stat',
    #                                             f"@{select.value}")])
    #     tooltips = """
    #     <div style="display:flex">
    #         <div>
    #             <img
    #             src='https://static.dwcdn.net/css/flag-icons/flags/4x3/@{alpha_2}.svg'
    #             height='42'
    #             width='42'>
    #             </img>
    #         </div>
    #         <div>
    #                 <h4>Date: </h4> @{Date}
    #                 <h4>Country: </h4> @{Country/Region}
    #                 <h4>Population: </h4> @{POPULATION}
    #                 <h4>Covid 19 Confirmed Cases: </h4> @{Confirmed}
    #                 <h4>Covid 19 Active Cases: </h4> @{Active}
    #                 <h4>Covid 19 Deaths: </h4> @{Deaths}
    #                 <h4>Covid 19 Recovered: </h4> @{Recovered}
    #         <div>
    #     </div
    #     """

    #     color_bar = ColorBar(color_mapper=color_mapper,
    #                          label_standoff=10,
    #                          border_line_color=None,
    #                          location=(0, 0),
    #                          orientation='horizontal')
    #     p = figure(name="basic_map",
    #                title="basic chloropeth map testing 123..",
    #                toolbar_location=None,
    #                tooltips=tooltips,
    #                y_axis_type='mercator',
    #                x_axis_type='mercator')
    #     p.xgrid.grid_line_color = None
    #     p.ygrid.grid_line_color = None
    #     p.patches('xs',
    #               'ys',
    #               source=src,
    #               fill_color={
    #                   'field': select.value,
    #                   'transform': color_mapper
    #               },
    #               line_color='black',
    #               line_width=1,
    #               fill_alpha=1)
    #     p.add_layout(color_bar, 'below')
    #     self.plot = p

    #     return p

    # def make_div():
    #     return Div(text="Testing a Div")

    # return layout(name="chloropeth_map",
    #               children=[[slider, select], [
    #                   make_plot(),
    #               ]])

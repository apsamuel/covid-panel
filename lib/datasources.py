"""The datasources module provides methods for acquiring statistical & geometric data
pertaining to the COVID-19 pandemic
"""
#import sys
import os
import io
#import glob
import zipfile
import warnings
import json
from urllib.parse import (
    urljoin)
import datetime as dt
from datetime import (
    timedelta)
import requests as curl
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import geopandas as gpd
from .who import (
    whomembers
)
#import pycountry as country
#from pyproj import (
#    Proj,
#    transform)
# for date and time functions

#import pytest
#import timeit

warnings.filterwarnings('ignore')

class PandasTimeStampEncoder(json.JSONEncoder):
    """
    Used when calling "to_json" on dataframes to properly convert the datetime type column(s)
    """
    def default(self, o):
        if isinstance(o, pd.Timestamp):
            return o.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, o)

#@pytest.fixture
def srcbase() -> dict:
    """Creates dict object containing Host & URLs for data acquisition

    Parameters
    ----------
    None

    Returns
    ----------
    dict - A dict containing data source Base URLs & full URIs
    """
    shape_base_url = 'https://naciscdn.org/naturalearth'
    jhu_base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'

    s_base = {
        'base': f'{jhu_base_url}/csse_covid_19_data/',
        'countrycodes': {
            'base': "https://countrycode.org/"
        },
        'countryshapes': {
            'base':
            'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip',
            'admin_0': {
                'countries': {
                    10:
                    f'{shape_base_url}/10m/cultural/ne_10m_admin_0_countries.zip',
                    50:
                    f'{shape_base_url}/50m/cultural/ne_50m_admin_0_countries.zip',
                    110:
                    f'{shape_base_url}/110m/cultural/ne_110m_admin_0_countries.zip'
                },
                'sovereignty': {
                    10:
                    f'{shape_base_url}/10m/cultural/ne_10m_admin_0_sovereignty.zip',
                    50:
                    f'{shape_base_url}/10m/cultural/ne_50m_admin_0_sovereignty.zip',
                    110:
                    f'{shape_base_url}/10m/cultural/ne_110m_admin_0_sovereignty.zip',
                },
                'boundary_lines_land': {
                    10:
                    f'{shape_base_url}/10m/cultural/ne_10m_admin_0_boundary_lines_land.zip',
                    50:
                    f'{shape_base_url}/10m/cultural/ne_50m_admin_0_boundary_lines_land.zip',
                    110:
                    f'{shape_base_url}/10m/cultural/ne_110m_admin_0_boundary_lines_land.zip',
                },
            },
            'admin_1': {
                'states_provinces': {
                    10:
                    f'{shape_base_url}/10m/cultural/ne_10m_admin_1_states_provinces.zip',
                    50:
                    f'{shape_base_url}/50m/cultural/ne_50m_admin_1_states_provinces.zip',
                    110:
                    f'{shape_base_url}/110m/cultural/ne_110m_admin_1_states_provinces.zip'
                },
            },
            'none': {
                'populated_places': {
                    110:
                    f'{shape_base_url}/110m/cultural/ne_110m_populated_places.zip'
                }
            }
        },
        'timeseries': {
            'base':
            f'{jhu_base_url}/csse_covid_19_data/',
            'global_confirmed':
            'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
            'global_deaths':
            'csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
            'global_recovered':
            'csse_covid_19_time_series/time_series_covid19_recovered_global.csv',
            'us_confirmed':
            'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv',
            'us_deaths':
            'csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
        },
        'stringency': {
            'base': 'https://raw.githubusercontent.com/OxCGRT/',
            'data': 'covid-policy-tracker/master/data/OxCGRT_latest.csv'
        }
    }
    return s_base

srcbase = srcbase()

def dfget(base: str, uri: str) -> pd.core.frame.DataFrame:
    """Fetch a csv format file on the internet, return it as a pandas DataFrame

    Parameters
    ----------
    base: str
        the base URL for the request
    uri: str
        the path to the timeseries file

    Returns
    ----------
    pd.DataFrame - A pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    data_frame = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return data_frame


def dfget_csv(base: str, uri: str) -> pd.core.frame.DataFrame:
    """Fetch a csv format file on the internet, return it as a pandas DataFrame

    Parameters
    ----------
    base: str
        the base URL for the request
    uri: str
        the path to the timeseries file

    Returns
    ----------
    pd.DataFrame - A pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    data_frame = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return data_frame


def dfget_timeseries(base: str, uri: str) -> pd.core.frame.DataFrame:
    """Fetch a csv format file on the internet, return it as a pandas DataFrame

    Parameters
    ----------
    base: str
        the base URL for the request
    uri: str
        the path to the timeseries file

    Returns
    ----------
    pd.DataFrame - A pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    data_frame = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return data_frame


def dfelongate(data_frame: pd.core.frame.DataFrame,
               dateidx: int = 4,
               ids: list = None,
               name: str = 'Date',
               value: str = 'Confirmed') -> pd.core.frame.DataFrame:
    """Unpivot a DataFrame from wide to long format, optionally leaving identifiers set

    Parameters
    ----------
    data_frame: DataFrame
        A Pandas dataframe containing Dates a series of columns with values
    dateidx: int
        the column header index where Date columns begin eg. data_frame.columns[idx:]
    ids: list
        a list of column names which will be preserved as ID columns
    name: str
        the name to provide the Date column values are melted into
    value: str
        the column name to melt on

    Returns
    ----------
    pd.DataFrame - A pandas DataFrame
    """
    if ids is None:
        ids = ['Province/State', 'Country/Region', 'Lat', 'Long']

    dates = data_frame.columns[dateidx:]
    return data_frame.melt(
        id_vars=ids,
        value_vars=dates,
        var_name=name,
        value_name=value
    )


def dfmerge(left=None, right=None, how='left', on_columns=None):
    """
    Merge two pandas dataframes

    Parameters
    ----------
    left: DataFrame
        Pandas dataframe, left side of merge
    right: DataFrame
        Pandas dataframe, right side of merge
    on_columns: list
        a list of column names which will be used to compare for merging

    Returns
    ----------
    pd.DataFrame - A pandas DataFrame
    """
    if on_columns is None:
        on_columns = [
            'Province/State', 'Country/Region', 'Date', 'Lat', 'Long'
        ]

    return pd.merge(left=left, right=right, how=how, on=on_columns,)


def codedb():
    """Shamelessly scrapes the countrycodes base source website to generate
    a pandas DataFrame. This is unwise and may break but is used to
    map Countries to their official ISO codes! =)

    Parameters
    -----------
    None

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    req = curl.get(srcbase['countrycodes']['base'])
    soup = BeautifulSoup(req.content, "html.parser")
    header_raw = soup.table.thead.tr.find_all('th')
    data_raw = soup.table.tbody.find_all('tr')
    header_raw[0].text.strip()
    headers = [i.text.strip() for i in header_raw]

    dataz = []
    for i in data_raw:
        rows = i.find_all('td')
        dataz.append([i.text.strip() for i in rows])

    data_frame = pd.DataFrame(dataz, columns=headers)
    # country_codes_df['alpha_2'] =
    data_frame[['alpha_2',
                'alpha_3']] = data_frame['ISO CODES'].str.split('/',
                                                                1).tolist()
    data_frame['alpha_3'] = data_frame.alpha_3.str.strip()
    data_frame['alpha_2'] = data_frame.alpha_2.str.strip()
    data_frame = data_frame.drop('ISO CODES', axis=1)
    data_frame = data_frame.rename(columns={'COUNTRY': 'Country/Region'})
    #df_country_codes = country_codes_df
    return data_frame

def shapesdb(shape_key,shape_type,scale):
    """Fetch respective binary shape files from natural earth

    Parameters
    -----------
    shape_key: str
        - admin_0: administrative level 0 detail
        - admin_1: administrative level 1 detail
    shape_type: str
        - countries: Country Level Boundaries
        - states_and_provinces: State & Province level Boundaries
        - sovereignty: Sovereign level Boundaries
        - boundary_lines_land: Land line Boundaryies
    Placeholder
    """
    #url = 'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
    req = curl.get(srcbase['countryshapes'][shape_key][shape_type][scale], allow_redirects=True)
    open(os.path.basename(req.url), 'wb').write(req.content)

    with zipfile.ZipFile(os.path.basename(req.url), "r") as zip_file:
        #zf.extractall(path='data')
        # only extract the needed file into data dir
        zip_file.extract(f"ne_{scale}m_{shape_key}_{shape_type}.shp",
                         path='./data')
        zip_file.extract(f"ne_{scale}m_{shape_key}_{shape_type}.shx",
                         path='./data')
        zip_file.extract(f"ne_{scale}m_{shape_key}_{shape_type}.prj",
                         path='./data')
        zip_file.extract(f"ne_{scale}m_{shape_key}_{shape_type}.cpg",
                         path='./data')
        zip_file.extract(f"ne_{scale}m_{shape_key}_{shape_type}.dbf",
                         path='./data')

    if os.path.exists(os.path.basename(req.url)):
        os.remove(os.path.basename(req.url))

    gdf = gpd.read_file(
        os.path.join(
            "data",
            f"ne_{scale}m_{shape_key}_{shape_type}.shp"
        )
    )
    gdf = gdf.rename(columns={
        'ADMIN': 'Official Name',
        'ADM0_A3': 'alpha_3'
    })
    #gdf = gdf.to_crs(3857)
    return gdf


# generate full database from latest upload
def fulldb():
    """Creates DataFrame from full JHU dataset from GitHub
    - Confirmed, Deaths, Recovered COVID-19 cases globally

    Parameters
    -----------
    None

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    df_global_confirmed = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['global_confirmed'])
    df_global_deaths = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['global_deaths'])
    df_global_recovered = dfget_timeseries(
        srcbase['base'], srcbase['timeseries']['global_recovered'])
    # df_us_confirmed = dfget_timeseries(
    #     srcbase['timeseries']['base'], srcbase['timeseries']['us_confirmed'])
    # df_us_deaths = dfget_timeseries(
    #     srcbase['timeseries']['base'], srcbase['timeseries']['us_deaths'])
    df_deaths_long = dfelongate(df_global_deaths, value='Deaths')
    df_conf_long = dfelongate(df_global_confirmed, value='Confirmed')
    df_recovered_long = dfelongate(df_global_recovered, value='Recovered')
    df_tmp = dfmerge(left=df_conf_long, right=df_deaths_long)
    df_full = dfmerge(left=df_tmp, right=df_recovered_long)
    # use datetime type for Date column
    df_full['Date'] = pd.to_datetime(df_full['Date'])

    # fill with 0 where not applicable
    df_full['Recovered'] = df_full['Recovered'].fillna(0)

    # use int data type for Recovered
    df_full['Recovered'] = df_full['Recovered'].astype(int)

    # rename countries, regions, provinces
    df_full['Country/Region'] = df_full['Country/Region'].replace(
        'Mainland China', 'China')

    df_full.loc[df_full['Province/State'] ==
                'Greenland', 'Country/Region'] = 'Greenland'

    df_full['Country/Region'] = df_full['Country/Region'].replace(
        'Korea, South', 'South Korea')

    # experimental, fills Province/State NaN values with blank strings
    df_full['Province/State'] = df_full['Province/State'].fillna('')
    # removing canadas improperly placed "recovered" values
    # df_full = df_full[df_full['Province/State']
    #                   .str.contains('Recovered') != True]
    # use a more classy filter..
    df_full = df_full[~( df_full['Province/State'].str.contains('Recovered') ) ]

    # removing country-wise data to avoid double count
    #df_full = df_full[df_full['Province/State'].str.contains(',') != True]
    df_full = df_full[~( df_full['Province/State'].str.contains(',') )]
    # add 'active' cases column, derived from (confirmed - deaths - recovered)
    df_full['Active'] = df_full['Confirmed'] - \
        df_full['Deaths'] - df_full['Recovered']

    df_full[['Province/State']] = df_full[['Province/State']].fillna(' ')
    cols = ['Confirmed', 'Deaths', 'Recovered', 'Active']
    df_full[cols] = df_full[cols].fillna(0)
    df_full[cols] = df_full[cols].astype(int)

    # partition out Diamond Princess, Grand Princess and MS Zaandam cruise ships
    ship_rows = df_full['Province/State'].str.contains('Diamond Princess') | \
        df_full['Country/Region'].str.contains('Diamond Princess') | \
        df_full['Province/State'].str.contains('Grand Princess') | \
        df_full['Country/Region'].str.contains('MS Zaandam')
    df_ship = df_full[ship_rows]

    #df_ship_latest = df_ship[df_ship['Date'] == max(df_ship['Date'])]
    df_full = df_full[~(ship_rows)]

    # Clean up Bad Data
    hubei_fix = {'Hubei': 34874}
    def change_val(df_in, date, ref_col, val_col, dtnry):
        """
        Shamelessly operates on `df_full`
        """
        for key, val in dtnry.items():
            df_in.loc[(df_in['Date'] == date) & (df_in[ref_col] == key), val_col] = val

    change_val(df_full, '2/12/20', 'Province/State',
               'Confirmed', hubei_fix)

    #df_full['WHO Region'] = df_full['Country/Region'].map(who(variation=False))
    # use whomembers (validate it still works as expected)
    df_full['WHO Region'] = df_full['Country/Region'].map(whomembers(variation=False))
    return df_full.reset_index(drop=True), df_ship.reset_index(drop=True)

# pass in the full db here
def groupdb(df_full: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """Groups full JHU data set by Date & Country/Region
    - sums Confirmed, Deaths, Recovered, and Active columns
    - resets index
    - calculates and adds columns for
      - 'New Recovered'
      - 'New deaths'
      - 'New cases'
    - adds 'WHO Region' column

    Parameters
    -----------
    df_full: pd.core.frame.DataFrame
        The Full JHU dataframe

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    # group by Date and Country/Region
    df_grouped = df_full.groupby(['Date', 'Country/Region'
                                  ])['Confirmed', 'Deaths', 'Recovered',
                                     'Active'].sum().reset_index()
    tmp = df_grouped.groupby(
        ['Country/Region', 'Date', ])['Confirmed', 'Deaths', 'Recovered']
    tmp = tmp.sum().diff().reset_index()
    # ... ?
    mask = tmp['Country/Region'] != tmp['Country/Region'].shift(1)
    tmp.loc[mask, 'Confirmed'] = np.nan
    tmp.loc[mask, 'Deaths'] = np.nan
    tmp.loc[mask, 'Recovered'] = np.nan

    # rename tmp columns
    tmp.columns = ['Country/Region', 'Date',
                   'New cases', 'New deaths', 'New recovered']

    df_grouped = pd.merge(df_grouped, tmp, on=['Country/Region', 'Date'])

    df_grouped = df_grouped.fillna(0)

    cols = ['New cases', 'New deaths', 'New recovered']
    df_grouped[cols] = df_grouped[cols].astype('int')

    df_grouped['New cases'] = df_grouped['New cases'].apply(
        lambda x: 0 if x < 0 else x)
    df_grouped['WHO Region'] = df_grouped['Country/Region'].map(
        whomembers(variation=False))
    return df_grouped

# pass in the fulldbgrouped() here


def daywisedb(df_full: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """Groups full JHU data set by Date
    - sums the following columns:
        - Confirmed
        - Deaths
        - Recovered
        - Active
        - New cases
        - New deaths
        - New recovered
    - resets index
    - adds following columns:
        - Deaths / 100 Cases
        - Recovered / 100 Cases
        - Deaths / 100 Recovered
    - adds column for 'No. of Countries'
    - calculates and adds columns for
      - 'New Recovered'
      - 'New deaths'
      - 'New cases'
    - sets numeric values to 0 where NaN

    Parameters
    -----------
    df_full: pd.core.frame.DataFrame
        The Full JHU dataframe acquired from a call to `datasources.fulldb()`

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    df_daywise = df_full.groupby('Date')['Confirmed', 'Deaths', 'Recovered',
                                         'Active', 'New cases', 'New deaths',
                                         'New recovered'].sum().reset_index()
    df_daywise['Deaths / 100 Cases'] = round(
        (df_daywise['Deaths']/df_daywise['Confirmed'])*100, 2)
    df_daywise['Recovered / 100 Cases'] = round(
        (df_daywise['Recovered']/df_daywise['Confirmed'])*100, 2)
    df_daywise['Deaths / 100 Recovered'] = round(
        (df_daywise['Deaths']/df_daywise['Recovered'])*100, 2)
    df_daywise['No. of countries'] = df_full[df_full['Confirmed'] != 0] \
        .groupby('Date')['Country/Region'] \
        .unique() \
        .apply(len)\
        .values
    cols = ['Deaths / 100 Cases',
            'Recovered / 100 Cases', 'Deaths / 100 Recovered']
    df_daywise[cols] = df_daywise[cols].fillna(0)
    #df_daywise.to_csv('covid19-daywise.csv', index=False)
    return df_daywise
    #df.to_csv('covid19-daywise.csv', index=False)


def countrywisedb(df_full: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """Slices JHU full dataset by date
    - latest - 7 days back
        - Adds columns
            - Deaths / 100 Cases (percentage)
            - Recovered / 100 Cases (percentage)
            - Deaths / 100 Recovered (percentage)
    - merges "recent" data into one dataframe
    - sorts data by Country/Region

    Parameters
    -----------
    df_full: pd.core.frame.DataFrame
        The Full JHU dataframe

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    country_wise = df_full[df_full['Date'] == max(df_full['Date'])] \
        .reset_index(drop=True) \
        .drop('Date', axis=1)
    country_wise['Deaths / 100 Cases'] = round(
        (country_wise['Deaths']/country_wise['Confirmed'])*100, 2)
    country_wise['Recovered / 100 Cases'] = round(
        (country_wise['Recovered']/country_wise['Confirmed'])*100, 2)
    country_wise['Deaths / 100 Recovered'] = round(
        (country_wise['Deaths']/country_wise['Recovered'])*100, 2)

    cols = ['Deaths / 100 Cases',
            'Recovered / 100 Cases', 'Deaths / 100 Recovered']
    country_wise[cols] = country_wise[cols].fillna(0)
    # country_wise

    today = df_full[df_full['Date'] == max(df_full['Date'])] \
        .reset_index(drop=True) \
        .drop('Date', axis=1)[['Country/Region', 'Confirmed']]

    last_week = df_full[df_full['Date'] == max(df_full['Date'])-timedelta(days=7)] \
        .reset_index(drop=True) \
        .drop('Date', axis=1)[['Country/Region', 'Confirmed']]

    tmp = pd.merge(today, last_week, on='Country/Region',
                 suffixes=(' today', ' last week'))
    tmp['1 week change'] = tmp['Confirmed today'] - tmp['Confirmed last week']
    tmp = tmp[['Country/Region', 'Confirmed last week', '1 week change']]

    country_wise = pd.merge(country_wise, tmp, on='Country/Region')
    country_wise['1 week % increase'] = round(
        tmp['1 week change']/tmp['Confirmed last week']*100, 2)
    country_wise['WHO Region'] = country_wise['Country/Region'].map(
        whomembers(variation=False))
    country_wise[country_wise['WHO Region'].isna()]['Country/Region'].unique()
    return country_wise


def fixtures(df_full: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """Applies several ad-hoc fixes JHU full dataset

    Parameters
    -----------
    df_full: pd.core.frame.DataFrame
        The Full JHU dataframe

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    df_full.loc[df_full['Country/Region'] == 'US',
                'Country/Region'] = 'United States'
    df_full.loc[df_full['Country/Region'] ==
           'Congo (Brazzaville)', 'Country/Region'] = 'Republic of the Congo'
    df_full.loc[df_full['Country/Region'] ==
           'Congo (Kinshasa)', 'Country/Region'] = 'Democratic Republic of the Congo'
    df_full.loc[df_full['Country/Region'] == 'Cabo Verde',
           'Country/Region'] = 'Cape Verde'
    df_full.loc[df_full['Country/Region'] == 'Czechia',
           'Country/Region'] = 'Czech Republic'
    df_full.loc[df_full['Country/Region'] == 'Holy See', 'Country/Region'] = 'Vatican'
    df_full.loc[df_full['Country/Region'] == 'North Macedonia',
           'Country/Region'] = 'Macedonia'
    df_full.loc[df_full['Country/Region'] == 'Timor-Leste',
           'Country/Region'] = 'East Timor'
    df_full.loc[df_full['Country/Region'] == 'Burma', 'Country/Region'] = 'Myanmar'
    df_full.loc[df_full['Country/Region'] == 'Eswatini', 'Country/Region'] = 'Swaziland'
    df_full.loc[df_full['Country/Region'] == "Cote d'Ivoire",
           'Country/Region'] = 'Ivory Coast'
    df_full.loc[df_full['Country/Region'] == "West Bank and Gaza",
           'Country/Region'] = 'Palestine'
    df_full['Country/Region'] = df_full['Country/Region'].replace('Taiwan*', 'Taiwan')
    return df_full


def attachmercatorcols(geo_df: gpd.geodataframe.GeoDataFrame,
                       latitude_col: str,
                       longitude_col: str) -> gpd.geodataframe.GeoDataFrame:
    """Converts latitude/longitude cols to mercator values
    - adds 'x' and 'y' columns respectively

    Parameters
    -----------
    geo_df: pd.core.frame.DataFrame
        The Full JHU dataframe
    latitude_col: str
        The latitude column name
    longitude_col: str
        The longitude column name
    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    k = 6378137
    geo_df['x'] = geo_df[longitude_col] * (k * np.pi / 180.0)
    geo_df['y'] = np.log(np.tan(
        (90 + geo_df[latitude_col]) * np.pi / 360.0)) * k
    return geo_df

def usdb():
    """Parses USA from data sets from JHU dataset

    Parameters
    -----------
    None

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    df_us_confirmed = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_confirmed'])
    df_us_deaths = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_deaths'])
    id_vars = df_us_confirmed.columns[0:11]
    us_dates = df_us_confirmed.columns[11:]
    df_us_confirmed_long = df_us_confirmed.melt(
        id_vars=id_vars, value_vars=us_dates, var_name='Date', value_name='Confirmed')
    df_us_deaths_long = df_us_deaths.melt(
        id_vars=id_vars, value_vars=us_dates, var_name='Date', value_name='Deaths')
    #df_us_confirmed_long
    return pd.concat(
        [df_us_confirmed_long, df_us_deaths_long[['Deaths']]], axis=1)
    #return df


# ['Timor-Leste', - East Timor
#  'Bermuda', - not in JHU dataset drop from stringency
#  'United States Virgin Islands', - "British Virgin Islands"
#  'Tonga', - constitutional monarchy, drop
#  'Turkmenistan', - drop
#  'Hong Kong', - ""
#  'Eswatini', - Swaziland
#  "Cote d'Ivoire", Ivory Coast
#  'Democratic Republic of Congo', -> 'Democratic Republic of the Congo'
#  'Aruba', - "" -> drop
#  'Faeroe Islands', - ""
#  'Kyrgyz Republic', - ""
#  'Puerto Rico', - check if it is in the csv
#  'Congo', -> 'Republic of the Congo'
#  'Guam', - ""
#  'Macao', - ??
#  'Slovak Republic']

def strigencydb(df_codes: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """Creates DataFrame from full Oxford dataset on GitHub

    Parameters
    -----------
    None

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    data_frame = dfget(srcbase['stringency']['base'], srcbase['stringency']['data'])
    cols = data_frame.columns[6:]

    data_frame[cols] = data_frame[cols].fillna(0)
    cols = ['CountryName', 'CountryCode', 'RegionName', 'RegionCode']
    data_frame[cols] = data_frame[cols].fillna('')

    rgx = r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})+"
    def replace(matcher):
        return f"{matcher.group('year')}-{matcher.group('month')}-{matcher.group('day')}"
    # fix date str format and convert to datetime type
    data_frame['Date'] = data_frame['Date'].astype(str)
    data_frame['Date'] = data_frame['Date'].str.replace(rgx, replace)
    data_frame['Date'] = pd.to_datetime(data_frame['Date'])


    # prepare data frame for merge on the `alpha_3` column
    data_frame = data_frame.rename(columns={'CountryCode': 'alpha_3'})
    # merge code db
    data_frame = pd.merge(data_frame, df_codes, how='left', on=['alpha_3'])

    # clean up some of the data frame
    data_frame.loc[data_frame['CountryName'] == 'Congo',
                   'CountryName'] = 'Republic of the Congo'
    data_frame.loc[data_frame['CountryName'] == 'Democratic Republic of Congo',
                   'CountryName'] = 'Democratic Republic of the Congo'
    data_frame.loc[data_frame['CountryName'] == 'Timor-Leste',
                   'CountryName'] = 'East Timor'
    data_frame.loc[data_frame['CountryName'] == 'Eswatini', 
                   'CountryName'] = 'Swaziland'
    data_frame.loc[data_frame['CountryName'] == 'Cote d\'Ivoire', 
                   'CountryName'] = 'Ivory Coast'
    data_frame.loc[data_frame['CountryName'] == 'United States Virgin Islands',
                   'CountryName'] = 'British Virgin Islands'
    return data_frame


def worldometersdb():
    """Creates DataFrame from full world-o-meters dataset for COVID-19
    DEFUCT: This function no longer works as expected
    """
    req = curl.get('https://www.worldometers.info/coronavirus/')
    soup = BeautifulSoup(req.content, "html.parser")
    thead = soup.find_all('thead')[-1]
    head = thead.find_all('tr')
    tbody = soup.find_all('tbody')[0]
    body = tbody.find_all('tr')

    head_rows = []
    body_rows = []

    for table_row in head:
        table_data = table_row.find_all(['th', 'td'])
        row = [i.text for i in table_data]
        head_rows.append(row)

    for table_row in body:
        table_data = table_data.find_all(['th', 'td'])
        row = [i.text for i in table_data]
        body_rows.append(row)

    data_frame = pd.DataFrame(body_rows[:len(body_rows)-6], columns=head_rows[0])
    data_frame = data_frame.iloc[8:, :-3].reset_index(drop=True)
    data_frame = data_frame.drop('#', axis=1)
    data_frame.columns = [
        'Country/Region',
        'TotalCases',
        'NewCases',
        'TotalDeaths',
        'NewDeaths',
        'TotalRecovered',
        'NewRecovered',
        'ActiveCases',
        'Serious,Critical',
        'Tot Cases/1M pop',
        'Deaths/1M pop',
        'TotalTests',
        'Tests/1M pop',
        'Population',
        'Continent',
    ]
    #reorder
    data_frame = data_frame[[
        'Country/Region',
        'Continent',
        'Population',
        'TotalCases',
        'NewCases',
        'TotalDeaths',
        'NewDeaths',
        'TotalRecovered',
        'NewRecovered',
        'ActiveCases',
        'Serious,Critical',
        'Tot Cases/1M pop',
        'Deaths/1M pop',
        'TotalTests',
        'Tests/1M pop',
    ]]

    data_frame['WHO Region'] = data_frame['Country/Region'].map(whomembers(variation=True))

    data_frame[data_frame['WHO Region'].isna()]['Country/Region'].unique()
    for col in data_frame.columns[2:]:
        # replace comma with empty string
        data_frame[col] = data_frame[col].str.replace('[,+ ]', '', regex=True)
        # replace 'N/A' with empty string
        data_frame[col] = data_frame[col].str.replace('N/A', '', regex=False)
    data_frame = data_frame.replace('', np.nan)
    return data_frame

def geostringencydb(
    df_stringency: pd.core.frame.DataFrame,
    df_shapes: gpd.geodataframe.GeoDataFrame,
    country_code: str = None) -> gpd.geodataframe.GeoDataFrame:
    """Creates GeoPandas DataFrame from Oxford Stringency DB source DataFrame
    This is accomplished by:
        - merging the shapesdb on '___' Column

    Parameters
    -----------
    df_stringency: pd.core.frame.DataFrame
        The stringency Database DataFrame
    df_shapes: gpd.geodataframe.GeoDataFrame
        A GeoPandas admin_0 or admin_1 level shape dataframe
    country_code: str
        The country code to drill down into, requires passing an 
        admin_1 df_stringency with state and province specificty

    Returns
    -----------
    pd.DataFrame = a geopandas DataFrame
    """

    if country_code is None:
        geo_data_frame = df_shapes.merge(
            df_stringency,
            left_on='alpha_3',
            right_on='alpha_3',
            how='left'
        )
        return geo_data_frame

    # return carved data
    df_shapes = df_shapes[(df_shapes.adm0_a3==country_code)]
    df_stringency = df_stringency[
        (df_stringency.alpha_3 == country_code) &
        (df_stringency.RegionName != '')
    ].reset_index(drop=False)
    df_stringency = df_stringency.rename(
        columns={
            'RegionName': 'name'
        }
    )
    # Great Britain must be merged on two columns, geonunit to name
    if country_code == 'GBR':
        geo_data_frame = df_shapes.merge(
            df_stringency,
            how='inner',
            left_on=['geonunit'],
            right_on=['name']
        )
        geo_data_frame = geo_data_frame.rename(
            columns={
                'name_x': 'name'
            }
        )


    else:
        geo_data_frame = df_shapes.merge(
            df_stringency,
            on=[
                'name'
            ]
        )
    return geo_data_frame

def geodb(df_grouped: pd.core.frame.DataFrame,
          df_shapes: gpd.geodataframe.GeoDataFrame,
          df_codes: pd.core.frame.DataFrame) -> gpd.geodataframe.GeoDataFrame:
    """Creates GeoPandas DataFrame from a grouped JHU source DataFrame
    This is accomplished by:
        - merging the codedb on 'Country/Region' Column
        - merging the shapesdb on 'alpha_3' Column

    Parameters
    -----------
    df_grouped: pd.core.frame.DataFrame
        A Grouped DataFrame
    df_shapes: gpd.geodataframe.GeoDataFrame
        A GeoPandas shape dataframe
    df_codes: pd.core.frame.DataFrame
        The country codes DataFrame, containing a column 'alpha_3' with ISO codes for countries

    Returns
    -----------
    pd.DataFrame = a pandas DataFrame
    """
    tmp = pd.merge(df_grouped, df_codes, how='left', on=['Country/Region'])
    tmp['alpha_3'] = tmp['alpha_3'].astype('str')
    tmp['alpha_2'] = tmp['alpha_2'].astype('str')
    tmp['alpha_3'] = tmp.alpha_3.str.strip()
    tmp['alpha_2'] = tmp.alpha_2.str.strip()
    tmp['alpha_2'] = tmp.alpha_2.str.lower()
    geo_data_frame = df_shapes.merge(tmp,

                          left_on='alpha_3',
                          right_on='alpha_3',
                          how='left')
    return geo_data_frame


def slice_on_day(data_frame: pd.core.frame.DataFrame,
                  date_column: str = None,
                  slice_date: tuple = None):
    """Placeholder"""
    if date_column is None:
        date_column = 'Date'

    if slice_date is None:
        slice_date: dt.datetime.now()

    return data_frame[
        data_frame[date_column] == pd.Timestamp(slice_date)
    ]

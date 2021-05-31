# for web requests
import requests as curl
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
# for file io, system & os functions
import sys
import os
import io
import glob
import zipfile
import warnings
import re
from random import randint
# for handling json
import json
# for handling iterables
import itertools
# for math and datascience
from math import pi
import numpy as np
import pandas as pd
import geopandas as gpd
import pycountry as country
from pyproj import Proj, transform
# for date and time functions
from datetime import date, datetime, timedelta


class PandasTimeStampEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, pd._libs.tslibs.timestamps.Timestamp):
            return o.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, o)


def srcbase():
    srcbase = {
        'base': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/',
        'countrycodes': {
            'base': "https://countrycode.org/"
        },
        'countryshapes': {
            'base': 'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
        },
        'timeseries': {
            'base': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/',
            'global_confirmed': 'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
            'global_deaths': 'csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
            'global_recovered': 'csse_covid_19_time_series/time_series_covid19_recovered_global.csv',
            'us_confirmed': 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv',
            'us_deaths': 'csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
        },
        'stringency': {
            'base': 'https://raw.githubusercontent.com/OxCGRT/',
            'data': 'covid-policy-tracker/master/data/OxCGRT_latest.csv'
        }
    }
    return srcbase


srcbase = srcbase()


def who(variation=False):
    who_region = {}
    if variation:
        afro = "Algeria, Angola, Cabo Verde, Congo, DRC, Eswatini, Sao Tome and Principe, Benin, South Sudan, Western Sahara, Congo (Brazzaville), Congo (Kinshasa), Cote d'Ivoire, Botswana, Burkina Faso, Burundi, Cameroon, Cape Verde, Central African Republic, Chad, Comoros, Ivory Coast, Democratic Republic of the Congo, Equatorial Guinea, Eritrea, Ethiopia, Gabon, Gambia, Ghana, Guinea, Guinea-Bissau, Kenya, Lesotho, Liberia, Madagascar, Malawi, Mali, Mauritania, Mauritius, Mozambique, Namibia, Niger, Nigeria, Republic of the Congo, Rwanda, São Tomé and Príncipe, Senegal, Seychelles, Sierra Leone, Somalia, South Africa, Swaziland, Togo, Uganda, Tanzania, Zambia, Zimbabwe"
        afro = [i.strip() for i in afro.split(',')]
        for i in afro:
            who_region[i] = 'Africa'

        # Region of the Americas PAHO
        paho = 'Antigua and Barbuda, Argentina, Bahamas, Barbados, Belize, Bermuda, Bolivia, Brazil, Canada, Chile, Colombia, Costa Rica, Cuba, Dominica, Dominican Republic, Ecuador, El Salvador, Grenada, Guatemala, Guyana, Haiti, Honduras, Jamaica, Mexico, Nicaragua, Panama, Paraguay, Peru, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Suriname, Trinidad and Tobago, United States, US, USA, Uruguay, Venezuela'
        paho = [i.strip() for i in paho.split(',')]
        for i in paho:
            who_region[i] = 'Americas'

        # South-East Asia Region SEARO
        searo = 'Bangladesh, Bhutan, North Korea, India, Indonesia, Maldives, Myanmar, Burma, Nepal, Sri Lanka, Thailand, Timor-Leste'
        searo = [i.strip() for i in searo.split(',')]
        for i in searo:
            who_region[i] = 'South-East Asia'

        # European Region EURO
        euro = 'Albania, Andorra, Greenland, Kosovo, Holy See, Vatican City, Liechtenstein, Armenia, Czechia, Austria, Azerbaijan, Belarus, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Georgia, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kazakhstan, Kyrgyzstan, Latvia, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Moldova, Romania, Russia, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Tajikistan, Turkey, Turkmenistan, Ukraine, United Kingdom, UK, Uzbekistan'
        euro = [i.strip() for i in euro.split(',')]
        for i in euro:
            who_region[i] = 'Europe'

        # Eastern Mediterranean Region EMRO
        emro = 'Afghanistan, Bahrain, Djibouti, Egypt, Iran, Iraq, Jordan, Kuwait, Lebanon, Libya, Morocco, Oman, Pakistan, Palestine, West Bank and Gaza, Qatar, Saudi Arabia, Somalia, Sudan, Syria, Tunisia, United Arab Emirates, UAE, Yemen'
        emro = [i.strip() for i in emro.split(',')]
        for i in emro:
            who_region[i] = 'Eastern Mediterranean'

        # Western Pacific Region WPRO
        wpro = 'Australia, Brunei, Cambodia, China, Cook Islands, Fiji, Japan, Hong Kong, Kiribati, Laos, Malaysia, Marshall Islands, Micronesia, Mongolia, Nauru, New Zealand, Niue, Palau, Papua New Guinea, Philippines, South Korea, S. Korea, Samoa, Singapore, Solomon Islands, Taiwan, Taiwan*, Tonga, Tuvalu, Vanuatu, Vietnam'
        wpro = [i.strip() for i in wpro.split(',')]
        for i in wpro:
            who_region[i] = 'Western Pacific'
    else:
        afro = "Algeria, Angola, Cabo Verde, Eswatini, Sao Tome and Principe, Benin, South Sudan, Western Sahara, Congo (Brazzaville), Congo (Kinshasa), Cote d'Ivoire, Botswana, Burkina Faso, Burundi, Cameroon, Cape Verde, Central African Republic, Chad, Comoros, Ivory Coast, Democratic Republic of the Congo, Equatorial Guinea, Eritrea, Ethiopia, Gabon, Gambia, Ghana, Guinea, Guinea-Bissau, Kenya, Lesotho, Liberia, Madagascar, Malawi, Mali, Mauritania, Mauritius, Mozambique, Namibia, Niger, Nigeria, Republic of the Congo, Rwanda, São Tomé and Príncipe, Senegal, Seychelles, Sierra Leone, Somalia, South Africa, Swaziland, Togo, Uganda, Tanzania, Zambia, Zimbabwe"
        afro = [i.strip() for i in afro.split(',')]
        for i in afro:
            who_region[i] = 'Africa'

        # Region of the Americas PAHO
        paho = 'Antigua and Barbuda, Argentina, Bahamas, Barbados, Belize, Bolivia, Brazil, Canada, Chile, Colombia, Costa Rica, Cuba, Dominica, Dominican Republic, Ecuador, El Salvador, Grenada, Guatemala, Guyana, Haiti, Honduras, Jamaica, Mexico, Nicaragua, Panama, Paraguay, Peru, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Suriname, Trinidad and Tobago, United States, US, Uruguay, Venezuela'
        paho = [i.strip() for i in paho.split(',')]
        for i in paho:
            who_region[i] = 'Americas'

        # South-East Asia Region SEARO
        searo = 'Bangladesh, Bhutan, North Korea, India, Indonesia, Maldives, Myanmar, Burma, Nepal, Sri Lanka, Thailand, Timor-Leste'
        searo = [i.strip() for i in searo.split(',')]
        for i in searo:
            who_region[i] = 'South-East Asia'

        # European Region EURO
        euro = 'Albania, Andorra, Greenland, Kosovo, Holy See, Liechtenstein, Armenia, Czechia, Austria, Azerbaijan, Belarus, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Georgia, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Kazakhstan, Kyrgyzstan, Latvia, Lithuania, Luxembourg, Malta, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Moldova, Romania, Russia, San Marino, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Tajikistan, Turkey, Turkmenistan, Ukraine, United Kingdom, Uzbekistan'
        euro = [i.strip() for i in euro.split(',')]
        for i in euro:
            who_region[i] = 'Europe'

        # Eastern Mediterranean Region EMRO
        emro = 'Afghanistan, Bahrain, Djibouti, Egypt, Iran, Iraq, Jordan, Kuwait, Lebanon, Libya, Morocco, Oman, Pakistan, Palestine, West Bank and Gaza, Qatar, Saudi Arabia, Somalia, Sudan, Syria, Tunisia, United Arab Emirates, Yemen'
        emro = [i.strip() for i in emro.split(',')]
        for i in emro:
            who_region[i] = 'Eastern Mediterranean'

        # Western Pacific Region WPRO
        wpro = 'Australia, Brunei, Cambodia, China, Cook Islands, Fiji, Japan, Kiribati, Laos, Malaysia, Marshall Islands, Micronesia, Mongolia, Nauru, New Zealand, Niue, Palau, Papua New Guinea, Philippines, South Korea, Samoa, Singapore, Solomon Islands, Taiwan, Taiwan*, Tonga, Tuvalu, Vanuatu, Vietnam'
        wpro = [i.strip() for i in wpro.split(',')]
        for i in wpro:
            who_region[i] = 'Western Pacific'

    return who_region


def dfget(base, uri):
    """
    Fetch a csv format file on the internet, return it as a pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    df = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return df


def dfget_csv(base, uri):
    """
    Fetch a csv format file on the internet, return it as a pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    df = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return df


def dfget_timeseries(base, uri):
    """
    Fetch a csv format file on the internet, return it as a pandas DataFrame
    """
    src = urljoin(base, uri)
    data = curl.get(src).content
    df = pd.read_csv(
        io.StringIO(
            data.decode('utf-8')
        )
    )
    return df


def dfelongate(d, dateidx=4, ids=['Province/State', 'Country/Region', 'Lat', 'Long'], name='Date', value='Confirmed'):
    """ 
    Changes a `time series` (row) to a long column, eg, elongates
    """
    dates = d.columns[dateidx:]
    return d.melt(
        id_vars=ids,
        value_vars=dates,
        var_name=name,
        value_name=value
    )


def dfmerge(l=None, r=None, how='left', on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']):
    """
    Merge two pandas dataframes
    """
    return pd.merge(
        left=l,
        right=r,
        how=how,
        on=on
    )


def codedb():
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

    df = pd.DataFrame(dataz, columns=headers)
    # country_codes_df['alpha_2'] =
    df[['alpha_2', 'alpha_3']] = df['ISO CODES'].str.split('/', 1).tolist()
    df['alpha_3'] = df.alpha_3.str.strip()
    df['alpha_2'] = df.alpha_2.str.strip()
    df = df.drop('ISO CODES', axis=1)
    df = df.rename(columns={'COUNTRY': 'Country/Region'})
    #df_country_codes = country_codes_df
    return df

# deprecated.. use shapesdb


def shapedb():
    gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    gdf = gdf.to_crs(3857)
    return gdf


def shapesdb():
    #url = 'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
    r = curl.get(srcbase['countryshapes']['base'], allow_redirects=True)
    open(os.path.basename(r.url), 'wb').write(r.content)

    with zipfile.ZipFile(os.path.basename(r.url), "r") as zf:
        zf.extractall(path='data')

    if os.path.exists(os.path.basename(r.url)):
        os.remove(os.path.basename(r.url))

    gdf = gpd.read_file(
        os.path.join(
            'data',
            'ne_110m_admin_0_countries.shp'
        )
    )
    gdf = gdf.rename(columns={
        'ADMIN': 'Official Name',
        'ADM0_A3': 'alpha_3'
    })
    gdf = gdf.to_crs(3857)
    return gdf


# generate full database from latest upload
def fulldb():
    df_global_confirmed = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['global_confirmed'])
    df_global_deaths = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['global_deaths'])
    df_global_recovered = dfget_timeseries(
        srcbase['base'], srcbase['timeseries']['global_recovered'])
    df_us_confirmed = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_confirmed'])
    df_us_deaths = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_deaths'])
    df_deaths_long = dfelongate(df_global_deaths, value='Deaths')
    df_conf_long = dfelongate(df_global_confirmed, value='Confirmed')
    df_recovered_long = dfelongate(df_global_recovered, value='Recovered')
    df_tmp = dfmerge(l=df_conf_long, r=df_deaths_long)
    df_full = dfmerge(l=df_tmp, r=df_recovered_long)
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

    # removing canadas recovered values
    df_full = df_full[df_full['Province/State']
                      .str.contains('Recovered') != True]

    # removing country-wise data to avoid double count
    df_full = df_full[df_full['Province/State'].str.contains(',') != True]
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

    df_ship_latest = df_ship[df_ship['Date'] == max(df_ship['Date'])]
    df_full = df_full[~(ship_rows)]

    # Clean up Bad Data
    hubeiFixEntry = {'Hubei': 34874}

    def change_val(df, date, ref_col, val_col, dtnry):
        """
        Shamelessly operates on `df_full`
        """
        for key, val in dtnry.items():
            df.loc[(df['Date'] == date) & (df[ref_col] == key), val_col] = val

    change_val(df_full, '2/12/20', 'Province/State',
               'Confirmed', hubeiFixEntry)

    df_full['WHO Region'] = df_full['Country/Region'].map(who(variation=False))
    return df_full, ship_rows


# pass in the full db here
def groupdb(df):
    # group by Date and Country/Region
    df_grouped = df.groupby(['Date', 'Country/Region'])['Confirmed',
                                                        'Deaths', 'Recovered', 'Active'].sum().reset_index()
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
        who(variation=False))
    return df_grouped

# pass in the fulldbgrouped() here


def daywisedb(df):
    # day-wise data
    # print(df.columns)
    df_daywise = df.groupby('Date')[
        'Confirmed',
        'Deaths',
        'Recovered',
        'Active',
        'New cases',
        'New deaths',
        'New recovered'].sum().reset_index()
    df_daywise['Deaths / 100 Cases'] = round(
        (df_daywise['Deaths']/df_daywise['Confirmed'])*100, 2)
    df_daywise['Recovered / 100 Cases'] = round(
        (df_daywise['Recovered']/df_daywise['Confirmed'])*100, 2)
    df_daywise['Deaths / 100 Recovered'] = round(
        (df_daywise['Deaths']/df_daywise['Recovered'])*100, 2)
    df_daywise['No. of countries'] = df[df['Confirmed'] != 0] \
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


def countrywisedb(df):
    country_wise = df[df['Date'] == max(df['Date'])] \
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

    today = df[df['Date'] == max(df['Date'])] \
        .reset_index(drop=True) \
        .drop('Date', axis=1)[['Country/Region', 'Confirmed']]

    last_week = df[df['Date'] == max(df['Date'])-timedelta(days=7)] \
        .reset_index(drop=True) \
        .drop('Date', axis=1)[['Country/Region', 'Confirmed']]

    t = pd.merge(today, last_week, on='Country/Region',
                 suffixes=(' today', ' last week'))
    t['1 week change'] = t['Confirmed today'] - t['Confirmed last week']
    t = t[['Country/Region', 'Confirmed last week', '1 week change']]

    country_wise = pd.merge(country_wise, t, on='Country/Region')
    country_wise['1 week % increase'] = round(
        t['1 week change']/t['Confirmed last week']*100, 2)
    country_wise['WHO Region'] = country_wise['Country/Region'].map(
        who(variation=False))
    country_wise[country_wise['WHO Region'].isna()]['Country/Region'].unique()
    return country_wise


def fixtures(df):
    df.loc[df['Country/Region'] == 'US', 'Country/Region'] = 'United States'
    df.loc[df['Country/Region'] ==
           'Congo (Brazzaville)', 'Country/Region'] = 'Republic of the Congo'
    df.loc[df['Country/Region'] ==
           'Congo (Kinshasa)', 'Country/Region'] = 'Democratic Republic of the Congo'
    df.loc[df['Country/Region'] == 'Cabo Verde',
           'Country/Region'] = 'Cape Verde'
    df.loc[df['Country/Region'] == 'Czechia',
           'Country/Region'] = 'Czech Republic'
    df.loc[df['Country/Region'] == 'Holy See', 'Country/Region'] = 'Vatican'
    df.loc[df['Country/Region'] == 'North Macedonia',
           'Country/Region'] = 'Macedonia'
    df.loc[df['Country/Region'] == 'Timor-Leste',
           'Country/Region'] = 'East Timor'
    df.loc[df['Country/Region'] == 'Burma', 'Country/Region'] = 'Myanmar'
    df.loc[df['Country/Region'] == 'Eswatini', 'Country/Region'] = 'Swaziland'
    df.loc[df['Country/Region'] == "Cote d'Ivoire",
           'Country/Region'] = 'Ivory Coast'
    df.loc[df['Country/Region'] == "West Bank and Gaza",
           'Country/Region'] = 'Palestine'
    df['Country/Region'] = df['Country/Region'].replace('Taiwan*', 'Taiwan')
    return df


def usdb():
    df_us_confirmed = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_confirmed'])
    df_us_deaths = dfget_timeseries(
        srcbase['timeseries']['base'], srcbase['timeseries']['us_deaths'])
    ids = df_us_confirmed.columns[0:11]
    us_dates = df_us_confirmed.columns[11:]
    df_us_confirmed_long = df_us_confirmed.melt(
        id_vars=ids, value_vars=us_dates, var_name='Date', value_name='Confirmed')
    df_us_deaths_long = df_us_deaths.melt(
        id_vars=ids, value_vars=us_dates, var_name='Date', value_name='Deaths')
    df_us_confirmed_long
    df = pd.concat(
        [df_us_confirmed_long, df_us_deaths_long[['Deaths']]], axis=1)
    return df


def strigencydb():
    df = dfget(srcbase['stringency']['base'], srcbase['stringency']['data'])

    cols = df.columns[6:]

    df[cols] = df[cols].fillna(0)
    cols = ['CountryName', 'CountryCode', 'RegionName', 'RegionCode']
    df[cols] = df[cols].fillna('')

    rgx = r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})+"
    def replace(
        m): return f"{m.group('year')}-{m.group('month')}-{m.group('day')}"
    df['Date'] = df['Date'].astype(str)
    df['Date'] = df['Date'].str.replace(rgx, replace)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def worldometersdb():
    req = curl.get('https://www.worldometers.info/coronavirus/')
    soup = BeautifulSoup(req.content, "html.parser")
    thead = soup.find_all('thead')[-1]
    head = thead.find_all('tr')
    tbody = soup.find_all('tbody')[0]
    body = tbody.find_all('tr')

    head_rows = []
    body_rows = []

    for tr in head:
        td = tr.find_all(['th', 'td'])
        row = [i.text for i in td]
        head_rows.append(row)

    for tr in body:
        td = tr.find_all(['th', 'td'])
        row = [i.text for i in td]
        body_rows.append(row)

    df = pd.DataFrame(body_rows[:len(body_rows)-6], columns=head_rows[0])
    df = df.iloc[8:, :-3].reset_index(drop=True)
    df = df.drop('#', axis=1)
    df.columns = ['Country/Region', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths',
                  'TotalRecovered', 'NewRecovered', 'ActiveCases', 'Serious,Critical',
                  'Tot Cases/1M pop', 'Deaths/1M pop', 'TotalTests', 'Tests/1M pop',
                  'Population', 'Continent']
    df = df[['Country/Region', 'Continent', 'Population', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths',
             'TotalRecovered', 'NewRecovered', 'ActiveCases', 'Serious,Critical',
             'Tot Cases/1M pop', 'Deaths/1M pop', 'TotalTests', 'Tests/1M pop']]

    df['WHO Region'] = df['Country/Region'].map(who(variation=True))

    df[df['WHO Region'].isna()]['Country/Region'].unique()
    for col in df.columns[2:]:
        # replace comma with empty string
        df[col] = df[col].str.replace('[,+ ]', '', regex=True)
        # replace 'N/A' with empty string
        df[col] = df[col].str.replace('N/A', '', regex=False)
    df = df.replace('', np.nan)
    return df


def geodb(df_any, df_shapes, df_codes):
    df = pd.merge(df_any, df_codes, how='left', on=['Country/Region'])
    df['alpha_3'] = df['alpha_3'].astype('str')
    df['alpha_2'] = df['alpha_2'].astype('str')
    df['alpha_3'] = df.alpha_3.str.strip()
    df['alpha_2'] = df.alpha_2.str.strip()
    df['alpha_2'] = df.alpha_2.str.lower()
    gdf = df_shapes.merge(df, left_on='alpha_3',
                          right_on='alpha_3', how='left')
    return gdf

# pylint: disable=redefined-outer-name
"""Tests for datasource module
- Placeholder
"""
from numpy import isin
import pytest
import pandas as pd
import geopandas as gpd
from . import datasources
import os
import sys
import warnings
warnings.filterwarnings('ignore')


# General test suite for the datasources module

@pytest.fixture
def source_base():
    '''Returns srcbase dictionary'''
    return datasources.srcbase

@pytest.fixture
def jhu_global_recovered(source_base):
    '''Returns JHU global recovered DataFrame'''
    #print(f"source_base: {source_base}")
    return datasources.dfget_timeseries(
        source_base['timeseries']['base'],
        source_base['timeseries']['global_recovered']
    )

@pytest.fixture
def jhu_full_db():
    '''returns JHU Covid-19 global DataFrame'''
    return datasources.fulldb()[0]

@pytest.fixture
def jhu_ship_db():
    '''Returns JHU Covid-19 cruise ship DataFrame'''
    return datasources.fulldb()[1]

@pytest.fixture
def jhu_grouped_db(jhu_full_db):
    '''Returns JHU Covid-19 grouped DataFrame'''
    return datasources.groupdb(
        jhu_full_db
    )
@pytest.fixture
def country_codes_db():
    '''Returns Country Codes DataFrame'''
    return datasources.codedb()

@pytest.fixture
def country_shapes_db():
    '''Returns Admin level 0 Country borders geopandas DataFrame'''
    return datasources.shapesdb('admin_0', 'countries', 10)

@pytest.fixture
def states_and_provinces_shapes_db():
    '''Returns Admin level 1 states and provinces borders geopandas DataFrame'''
    return datasources.shapesdb('admin_1', 'states_provinces', 10)

@pytest.fixture
def country_level_geo_db(jhu_grouped_db, country_shapes_db, country_codes_db ):
    '''Returns a country level geo DataFrame merging JHU & geometry data'''
    return datasources.geodb(jhu_grouped_db, country_shapes_db, country_codes_db)

def test_sources(source_base):
    '''Validate Source'''
    assert isinstance(source_base, dict)

def test_dfget_timeseries(jhu_global_recovered):
    '''Validate dfget_timeseries functionality'''
    assert isinstance(jhu_global_recovered, pd.core.frame.DataFrame)


def test_jhu_full_dataframe(jhu_full_db):
    '''Validate full_db'''
    assert isinstance(jhu_full_db, pd.core.frame.DataFrame)

def test_jhu_grouped_dataframe(jhu_grouped_db):
    '''Validate full_db'''
    assert isinstance(jhu_grouped_db, pd.core.frame.DataFrame)

def test_jhu_ship_dataframe(jhu_ship_db):
    '''Validate full_db'''
    assert isinstance(jhu_ship_db, pd.core.frame.DataFrame)

def test_country_codes_dataframe(country_codes_db):
    '''Validate country codes dataframe'''
    assert isinstance(country_codes_db, pd.core.frame.DataFrame)

def test_country_shapes_geo_dataframe(country_shapes_db):
    '''Validate country shapes dataframe'''
    assert isinstance(country_shapes_db, gpd.geodataframe.GeoDataFrame)

def test_states_and_provinces_shapes_geo_dataframe(states_and_provinces_shapes_db):
    '''Validate country shapes dataframe'''
    assert isinstance(states_and_provinces_shapes_db, gpd.geodataframe.GeoDataFrame)


def test_country_level_geo_dataframe(country_level_geo_db):
    '''Validate merged JHU covid data & country shapes dataframe'''
    assert isinstance(country_level_geo_db, gpd.geodataframe.GeoDataFrame)
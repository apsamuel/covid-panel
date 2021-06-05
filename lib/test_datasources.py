import pytest
import os, sys, warnings
warnings.filterwarnings('ignore')
from . import datasources

# General test suite for the datasources module 

@pytest.fixture 
def srcbase():
    return datasources.srcbase

@pytest.fixture 
def fulldb():
    return datasources.fulldb()[0]

@pytest.fixture
def shipdb():
    return datasources.fulldb()[1]

@pytest.fixture 
def fixture(fulldb):
    return datasources.fixtures(fulldb)

@pytest.fixture
def groupdb(fixture):
    return datasources.groupdb(fixture)

@pytest.fixture 
def daywisedb(groupdb):
    return datasources.daywisedb(groupdb)

@pytest.fixture
def countrywisedb(groupdb):
    return datasources.countrywisedb(groupdb)

@pytest.fixture 
def usdb(): 
    return datasources.usdb()

@pytest.fixture 
def stringencydb():
    return datasources.strigencydb()

@pytest.fixture 
def shapesdb():
    return datasources.shapesdb()

@pytest.fixture 
def codedb():
    return datasources.codedb()

@pytest.fixture
def geodb(fulldb, shapesdb, codedb):
    return datasources.geodb(fulldb, shapesdb, codedb)

def test_srcbase(srcbase):
    assert type(srcbase)==dict

def test_fulldb(fulldb):
    assert type(fulldb)==datasources.pd.core.frame.DataFrame

def test_groupdb(groupdb):
    assert type(groupdb)==datasources.pd.core.frame.DataFrame

def test_fixture(fixture):
    assert type(fixture)==datasources.pd.core.frame.DataFrame

def test_daywisedb(daywisedb):
    assert type(daywisedb)==datasources.pd.core.frame.DataFrame

def test_dfget_timeseries(srcbase):
    assert type(datasources.dfget_timeseries(
        base=srcbase['timeseries']['base'],
        uri=srcbase['timeseries']['global_confirmed']
    ))==datasources.pd.core.frame.DataFrame

def test_dfget(srcbase):
    assert type(datasources.dfget(
        base=srcbase['stringency']['base'],
        uri=srcbase['stringency']['data']
    ))==datasources.pd.core.frame.DataFrame


def test_geodb(geodb):
    assert type(geodb)==datasources.gpd.geodataframe.GeoDataFrame


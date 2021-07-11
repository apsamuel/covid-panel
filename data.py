"""Provides tests for datasources module"""
import os
import sys
import warnings
from lib import datasources
warnings.filterwarnings('ignore')

OUT_DIR = './data'

def getmap():
    """not used..
    """
    return {
        "full": datasources.fulldb
    }


def main():
    """Main method of datasources tests
    """
    df_stringency = datasources.strigencydb()
    df_full, df_ship = datasources.fulldb()
    df_full = datasources.fixtures(df_full)
    df_grouped = datasources.groupdb(df_full)
    df_daywise = datasources.daywisedb(df_grouped)
    df_countrywise = datasources.countrywisedb(df_grouped)
    # gdf_countrywise = datasources.geodb(
    #     df_countrywise, datasources.shapesdb('admin_0', 'countries', 110),
    #     datasources.codedb())
    # gdf_full = datasources.geodb(
    #     df_full, datasources.shapesdb('admin_0', 'countries', 110),
    #     datasources.codedb())
    # gdf_full_grouped = datasources.geodb(
    #     datasources.groupdb(df_full),
    #     datasources.shapesdb('admin_0', 'countries', 110),
    #     datasources.codedb())


    df_stringency.to_csv(
        os.path.join(OUT_DIR, 'stringencydb.csv')
    )
    df_full.to_csv(
        os.path.join(OUT_DIR, 'fulldb.csv')
    )
    df_ship.to_csv(
        os.path.join(OUT_DIR, 'shipdb.csv')
    )
    df_grouped.to_csv(
        os.path.join(OUT_DIR, 'groupdb.csv')
    )
    df_daywise.to_csv(
        os.path.join(OUT_DIR, 'daywisedb.csv')
    )
    df_countrywise.to_csv(
        os.path.join(OUT_DIR, 'countrywisedb.csv')
    )

#print(getmap())
main()

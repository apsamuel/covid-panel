import os, sys, warnings
from lib import datasources
warnings.filterwarnings('ignore')

out_dir = './data'

def getmap():
    return {
        "full": datasources.fulldb
    }


def main():
    #initialize dbs
    #df_worldometers = datasources.worldometersdb()
    df_stringency = datasources.strigencydb() 
    df_full, df_ship = datasources.fulldb()
    df_full = datasources.fixtures(df_full)
    df_grouped = datasources.groupdb(df_full)
    df_daywise = datasources.daywisedb(df_grouped)
    df_countrywise = datasources.countrywisedb(df_grouped)
    gdf_countrywise = datasources.geodb(
        df_countrywise, 
        datasources.shapesdb(), 
        datasources.codedb()
    )
    gdf_full = datasources.geodb(
        df_full, 
        datasources.shapesdb(), 
        datasources.codedb()
    )
    gdf_full_grouped = datasources.geodb(
        datasources.groupdb(df_full), 
        datasources.shapesdb(), 
        datasources.codedb()
    )

    #refresh csv's

    # format changes for world-o-meters, need to update function.
    # df_worldometers.to_csv(
    #     os.path.join(out_dir, 'womdb.csv')
    # )
    df_stringency.to_csv(
        os.path.join(out_dir, 'stringencydb.csv')
    )
    df_full.to_csv(
        os.path.join(out_dir, 'fulldb.csv')
    )
    df_ship.to_csv(
        os.path.join(out_dir, 'shipdb.csv')
    )
    df_grouped.to_csv(
        os.path.join(out_dir, 'groupdb.csv') 
    )
    df_daywise.to_csv(
        os.path.join(out_dir, 'daywisedb.csv') 
    )
    df_countrywise.to_csv(
        os.path.join(out_dir, 'countrywisedb.csv')
    )

#print(getmap())
main()
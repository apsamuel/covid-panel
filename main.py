#from lib import datasources
# lib directory such that other libs can use each other
# from lib import genericCountry as genericCountry
# from lib import datasources as datasources

import bokeh
import pandas as pd
from operator import ge
import debugpy
import os
import sys
import logging
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme, built_in_themes
from lib.FullDataTable import FullDataTable
from lib.DataOverview import DataOverview
from lib.ChoroplethMap import ChoroplethMap
from lib import datasources
import lib.loginator 
log = logging.getLogger(__name__)
logger = lib.loginator.Loginator(
    logger=log,
    lvl='DEBUG'
).logger

# setup some things..


def main():
    bokeh_version = bokeh.__version__
    pandas_version = pd.__version__
    #debugpy.breakpoint()
    logger.debug("[main] starting main steps")
    logger.debug(f"[main] Pandas Version: {pandas_version}")
    logger.debug(f"[main] Bokeh Version: {bokeh_version}")

    # data records
    logger.debug("[main] beginning full_db data source init")
    full_db = datasources.fixtures(
                datasources.fulldb()[0]
                )
    daywise_db = datasources.daywisedb(
        datasources.groupdb(
            datasources.fixtures(
                datasources.fulldb()[0]
            )
        )
    )
    #debugpy.breakpoint()
    geo_db = datasources.geodb(
        datasources.groupdb(
            datasources.fixtures(
                datasources.fulldb()[0]
            )
        ),
        datasources.shapesdb(),
        datasources.codedb()
    )
    #debugpy.breakpoint()
    logger.debug("[main] data init complete")

    # optionally start debugging session
    # if os.environ.get('DEBUG_APP', 'false') == "true":
    #     logger.debug("debug mode has been enabled, please connect a client to port 5678")
    #     debugpy.listen(('127.0.0.1', 5678))
    #     debugpy.wait_for_client()


    # add main content to DOM
    logger.debug("[main] generating page layout objects")

    #debugpy.debug_this_thread()
    full_table = FullDataTable(db=full_db)
    overview = DataOverview(db=daywise_db)
    overview_layout = overview.layout(title='overview')
    choro = ChoroplethMap(db=geo_db)
    choro_layout = choro.layout()
    table_layout = full_table.layout()
    logger.debug("[main] layout object generation complete")

    # current document settings
    curdoc().template_variables["page_layout"] = table_layout
    curdoc().theme = Theme(filename='./theme.yaml')
    curdoc().add_root(
        table_layout
    )
    curdoc().add_root(
        overview_layout
    )
    curdoc().add_root(
        choro_layout
    )

    # fin... 
    logger.debug("[main] page has been rendered, please do validate the results in a browser")
    logger.debug('[main] starting debugging')
    #debugpy.listen(('127.0.0.1', 5678))  # testing a breakpoint
    
    if os.environ.get('DEBUG_APP', False) == 'true':
        logger.debug("[main] entering breakpoint")
        debugpy.breakpoint()
    logger.debug("[main] completed breakpoint")

main()


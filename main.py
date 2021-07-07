"""
Main
----

* Main module is executed when the CLI argument "bokeh serve <appDir>" is called.
* Primary function is to instantiate the:
    - `main` data source objects
    - content class objects added to the DOM within the jinja
* These objects produce the original "View" the user sees when visiting the dashboard
"""

#from operator import ge
import os
import sys
import logging
import bokeh
import pandas as pd
import debugpy
from bokeh.plotting import (
    curdoc,
)
from bokeh.themes import (
    Theme,
)
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
    """
    Main application module
    """
    #debugpy.debug_this_thread()
    sys_version = sys.version
    bokeh_version = bokeh.__version__
    pandas_version = pd.__version__
    logger.debug("[main] starting main steps")
    logger.debug(f"[main] Pandas Version: {pandas_version}")
    logger.debug(f"[main] Bokeh Version: {bokeh_version}")
    logger.debug(f"[main] Python Version: {sys_version}")
    # generate data records
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
    geo_db = datasources.geodb(
        datasources.groupdb(
            datasources.fixtures(
                datasources.fulldb()[0]
            )
        ),
        #datasources.shapesdb(),
        datasources.shapesdb('admin_0','countries',110),
        datasources.codedb()
    )

    logger.debug("[main] data init complete")
    logger.debug("[main] generating page layout objects")
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
        logger.debug("[main] debugging value is {os.environ.get('DEBUG_APP', False)}")
        logger.debug("[main] entering breakpoint")
        debugpy.breakpoint()
        logger.debug("[main] completed breakpoint")

main()

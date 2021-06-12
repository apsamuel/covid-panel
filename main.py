#from lib import datasources
# lib directory such that other libs can use each other
# from lib import genericCountry as genericCountry
# from lib import datasources as datasources

import bokeh
from operator import ge
from bokeh.plotting import figure, curdoc
from bokeh.themes import Theme, built_in_themes
#import lib.datasources as datasources
#import lib.genericCountry as genericCountry
# sys.path.append("./lib")
#from lib.genericCountry import genericCountry 
from lib.FullDataTable import FullDataTable
from lib.DataOverview import DataOverview
from lib.ChoroplethMap import ChoroplethMap
from lib import datasources
import debugpy 
import os, sys
import logging
logging.basicConfig(stream=sys.stdout, level=print)
bokeh_version=bokeh.__version__
# df_full = datasources.fixtures(
#     datasources.fulldb()[0]
#     )
#originally using 2.2.3 version of bokeh. 


def main():

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
        datasources.shapesdb(),
        datasources.codedb()
    )

    # start debugging session
    if os.environ.get('DEBUG_APP', 'false') == "true":
        debugpy.listen(('127.0.0.1', 5678))
        debugpy.wait_for_client()
    print("Starting main function...")


    # x = [1, 2, 3, 4, 5]
    # y = [6, 7, 6, 4, 5]
    # p = figure(title='contrast', name='simpleplot',sizing_mode='scale_both')
    # p.line(x, y)
    # p.css_classes = [
    #     'plot'
    # ]
    full_table = FullDataTable(db=full_db)
    overview = DataOverview(db=daywise_db)
    overview_layout = overview.layout(title='overview')
    choro = ChoroplethMap(db=geo_db)
    choro_layout = choro.layout()
    table_layout = full_table.layout()

    curdoc().template_variables["page_layout"] = table_layout
    curdoc().theme = Theme(filename='./theme.yaml')
    curdoc().add_root(
        table_layout
        #r.panel().servable()
    )
    curdoc().add_root(
        overview_layout
    )
    curdoc().add_root(
        choro_layout
    )
    print("page rendering complete, please validate results")

main()

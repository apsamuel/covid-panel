#from lib import datasources
# lib directory such that other libs can use each other
# from lib import genericCountry as genericCountry
# from lib import datasources as datasources

import bokeh
from operator import ge
from bokeh.plotting import figure, curdoc
from bokeh.themes import built_in_themes
#import lib.datasources as datasources
#import lib.genericCountry as genericCountry
# sys.path.append("./lib")
from lib.genericCountry import genericCountry 
from lib.genericCountryX import genericCountryX

from lib import datasources
import debugpy 
import os, sys
import logging
logging.basicConfig(stream=sys.stdout, level=print)
bokeh_version=bokeh.__version__
# df_full = datasources.fixtures(
#     datasources.fulldb()[0]
#     )

def main():
    if os.environ.get('DEBUG_APP', 'false') == "true":
        debugpy.listen(('127.0.0.1', 5678))
        debugpy.wait_for_client()
    print("Starting main function...")
    r = genericCountryX()
    #r.countries()

    #r = genericCountry(dataset=df_full, )

    layout = r.layout()
    #print(type(layout))
    #print(layout)
    curdoc().template_variables["page_layout"] = layout
    curdoc().theme = 'dark_minimal'
    curdoc().add_root(
        layout
        #r.panel().servable()
    )
    print("page rendering complete, please validate results")



main()

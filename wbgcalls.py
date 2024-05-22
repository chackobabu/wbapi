import pandas as pd
import numpy as np

import wbgapi as wb

class WbCall():
    def __init__(self, search_term = None):
        self.dbs = wb.source.list(q=search_term)
        
    def get_economies(self, sel_db=None):
        self.economies = pd.DataFrame()
        for i,e in enumerate(wb.economy.list(db=sel_db)):
            for key,item in e.items():
                self.economies.loc[i,key] = item
                
        self.economies = self.economies.fillna("-").set_index(['region'])['value'].sort_index()
        
    def get_series(self, sel_db=None, search_term=None):
        self.series = wb.series.info(db=sel_db, q=search_term)
        
wb_obj = WbCall()
# print(wb_obj.dbs)

wb_obj.get_economies(sel_db=32)
        
# print(wb_obj.economies['aggregate'].unique())
# print(wb_obj.economies)
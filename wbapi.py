import pandas as pd
import wbgapi as wb

class wbapi():
    # do not make it get topics as soon as its initialised. make it another method.
    def __init__(self, search_term=None):
        
        df = wb.topic.list(q=search_term)
        self.topics = self.resp2_df(df)
        self.search_term_ret = search_term
        
        if self.topics.shape[0] == 0:
            self.search_term_ret = "invalid"
            df = wb.topic.list()
            self.topics =  self.resp2_df(df)
                
    def get_series(self, sel_db=None, search_term=None):
        df = wb.series.list(topic=sel_db, q=search_term)
        self.series =  self.resp2_df(df)
    
    def get_economies(self, sel_db=None):
        self.economies = wb.economy.DataFrame(labels=True,skipAggs=True, db=sel_db)
    
    def get_metaData_series(self, param):
        self.meta_data_series = wb.series.metadata.get(param) 
        
    def get_metaData_economy(self, param):
        self.meta_data_economy = wb.economy.metadata.get(param)   
        
    def resp2_df(self, resp):
        df = pd.DataFrame()
        for i,each in enumerate(resp):
            for k in each.keys():
                df.loc[i,k] = each[k]      
                
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64','float','int']:
                df.fillna({col:0}, inplace=True)
            else:
                df.fillna({col:"-"}, inplace=True)
        return df
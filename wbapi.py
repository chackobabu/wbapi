import pandas as pd
import wbgapi as wb

class wbapi():
    
    def __init__(self):
        pass
    
    # do not make it get topics as soon as its initialised. make it another method.
    def search_topics(self, search_term=None):
        df = wb.topic.list(q=search_term)
        topics = self.resp2_df(df)
        self.search_term_ret = search_term
        
        if topics.shape[0] == 0:
            self.search_term_ret = "invalid"
            df = wb.topic.list()
            topics = self.resp2_df(df)
        
        return topics
    
    def search_databases(self, search_term=None):
        df = wb.source.list(q=search_term)
        databases = self.resp2_df(df)
        return databases
                
    def series(self, topic=None, db=None,search_term=None):
        df = wb.series.list(topic=topic, db=db, q=search_term)
        return self.resp2_df(df)
    
    def economies(self, sel_db=None):
        return wb.economy.DataFrame(labels=True,skipAggs=True, db=sel_db)
    
    def metaData_series(self, param):
        return wb.series.metadata.get(param) 
        
    def metaData_economy(self, param):
        return wb.economy.metadata.get(param)   
        
    def get_dataframe(self, series, economies, time):
        return wb.data.DataFrame(series=series, economy=economies,time=time, labels=True, skipBlanks=True)
        
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
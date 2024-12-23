import pandas as pd

##避免使用iloc賦值

class simple_backtest(object):
    def __init__(self , data , equity , commission = 0.0001):
        self.data = data.copy()
        self.equity = equity
        self.commission = commission
        self.position = 0
        self.data['equity'] = equity
        self.data['position'] = 0
        self.data['transaction'] = None
        self.data['Datetime'] = pd.to_datetime(self.data['Datetime'])
        self.trade = []
        
    def buy(self , row_index , amount):
        #做多時有空頭倉位先平掉
        price = self.data.loc[row_index , 'Close']
        
        if self.position < 0:
            self.equity -= abs(self.position) * price * (1 + self.commission)
            self.position = 0
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(minutes = 30) ,
                               'action':'close_short' , 'amount':self.position , 'price' : price , 
                               'equity' : self.equity})
        
        #開多倉
        self.position += amount
        self.equity -= amount * price * (1 + self.commission)
        
        self.data.loc[row_index , 'equity'] = self.equity
        self.data.loc[row_index , 'position'] = self.position
        self.data.loc[row_index , 'transaction'] = f'buy_{amount}_at_{price}'
        self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(minutes = 30) , 
                           'action':'long' , 'amount':amount , 'price' : price , 
                           'equity' : self.equity})
    
    def short(self , row_index , amount):
        #做空時有多頭倉位先平掉
        price = self.data.loc[row_index , 'Close']
        
        if self.position > 0 :
            self.equity += self.position * price * (1-self.commission)
            self.position = 0
            self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(minutes = 30) , 
                               'action':'close_long' , 'amount':self.position , 'price' : price , 
                               'equity' : self.equity})
        
        #開空倉
        self.position -= amount
        self.equity += amount * price * (1 - self.commission)
        
        self.data.loc[row_index , 'equity'] = self.equity
        self.data.loc[row_index , 'position'] = self.position
        self.data.loc[row_index , 'transaction'] = f'short_{amount}_at_{price}'
        self.trade.append({'time': self.data.loc[row_index , 'Datetime'] + pd.Timedelta(minutes = 30) , 
                           'action':'short' , 'amount':amount , 'price' : price , 
                           'equity' : self.equity})
    
    def close_position(self):
        final_price = self.data.loc[self.data.index[-1] , 'Close']

        if self.position > 0 :
            self.equity += self.position * final_price * (1-self.commission)
        elif self.position < 0 :
            self.equity -= abs(self.position) * final_price * (1+self.commission)
            
        self.position = 0
        self.data.loc[self.data.index[-1], 'position'] = self.position
        self.data.loc[self.data.index[-1], 'equity'] = self.equity
        self.data.loc[self.data.index[-1], 'transaction'] = f'close_position_at_{final_price}'
        self.trade.append({'time': self.data.loc[self.data.index[-1] , 'Datetime'] , 
                           'action':'close_position' , 'amount':self.position , 'price' : final_price , 
                           'equity' : self.equity})
        
            
    
    def run(self):
        #尋找交易訊號，1時做多，-1時多空
        for i in range(1 , len(self.data)):
            if self.data.loc[i , 'signal'] == 1 :
                self.buy(row_index=i , amount=1)
            elif self.data.loc[i , 'signal'] == -1:
                self.short(row_index=i ,amount=1)
            else:
                self.data.loc[i , 'equity'] = self.equity
                self.data.loc[i , 'position'] = self.position
        
        self.close_position()
        
        return self.data
    
    
    def trades(self):
        return pd.DataFrame(self.trade)
    
    
    



            
  
        
        
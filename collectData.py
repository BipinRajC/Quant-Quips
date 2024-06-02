# Import all the libraries needed

import yfinance as yf
import sys
import os
import pandas as pd

class dataScraper():
    def __init__():
        return
    
    def download_data(companyName:str, countryName:str,startDate:str = "2000-01-01",endDate:str = "2024-12-31") -> str:
        stock = yf.Ticker(companyName)
        data = stock.history(start = startDate, end = endDate)
        
        if(data.empty):
            return f"No data found for {companyName}"
        
        data.to_csv(f"data/scrapedData/{countryName}/{companyName}.csv")
        del data,stock
        return f"Downloaded data for {companyName}" 
        
        
    def bulk_download_data(countryName:str = None,tickerListPath:str = None,requiredNumber:int = None,startDate:str = "2000-01-01",endDate:str = "2024-12-31") -> str:
        if(countryName == None):
            return f"Please give country code\n"
        elif(tickerListPath == None):
            return f"Please give a path to ticker list\n"
        elif not os.path.exists(tickerListPath):
            return f"File does not exist at {tickerListPath}\n"
        
        ticker_symbols = pd.read_csv(tickerListPath)
        
        if(requiredNumber == None):
            ticker_symbols = ticker_symbols.head(5)
        else:
            ticker_symbols = ticker_symbols.head(requiredNumber)
        
        for ticker in ticker_symbols['Ticker']:
            stock = yf.Ticker(ticker)
            data = stock.history(start = startDate, end = endDate)
            
            if(data.empty):
                return f"No data found for {ticker}"
            
            data.to_csv(f"data/scrapedData/{countryName}/{ticker}.csv")
            del data,stock
            return f"Downloaded data for {ticker}"
        

def main():
    downloader = dataScraper
    downloader.download_data("AAPL","US")
    downloader.bulk_download_data(countryName = "IND",tickerListPath = "data/tickerList/indian_companies.csv")
    
main()
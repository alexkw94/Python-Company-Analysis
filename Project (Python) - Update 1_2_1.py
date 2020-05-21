#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import requests
import json
from tkinter import *
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')



#Intro text
print("Hello User! With this programm you will be able to choose between a variety of public stocks from different exchanges before easily analysing the underlying company.")
print("")

#Update: Since recently Financial Modelling Prep requires an individual API-Key. Therefore we first have to ask the user to enter his API-Key from Financial Modelling Prep in order to being able to access the required links
#On https://financialmodelingprep.com/developer/docs/ everyone can create an account for free and will immediately receive an individual API-Key
API_Key = input("Please enter your individual API-Key from Financial Modelling Prep in order to access the data (e.g. 4e20e35a9763edf292366927d58a3614):")

#show the user a list of the exchanges which are available to this programm, so that he can then choose one
#receive a list of all available stocks from the API financialmodelingprep
available_symbols = requests.get(f'https://financialmodelingprep.com/api/v3/company/stock/list?apikey={API_Key}')

#translate the data into json
available_symbols = available_symbols.json()

#receive the symbolList data in specific
available_symbols = available_symbols['symbolsList']

#translate the data into a dictionary in order to make it easily accessible
symbols = pd.DataFrame.from_dict(available_symbols)

#get rid of rows with no values or NaN values as names
symbols = symbols.dropna()
symbols = symbols[symbols.name != '']

#get rid of row with ETF's, Fund's and "%", since there we can't analyse financials (e.g. balance sheets)
symbols = symbols[~symbols.name.str.contains("ETF")]
symbols = symbols[~symbols.name.str.contains("Fund")]
symbols = symbols[~symbols.name.str.contains("%")]

#get rid of the column with prices and swap the column with names of and symbols
symbols = symbols[symbols.columns.drop('price')]
symbols = symbols[['name','symbol','exchange']]

#now we want to show to the user which exchanges are available that he can choose from
#therefore we select the column "exchange", put the values in an alphabetical order and remove duplicates. Then reset the index.
exchanges = symbols.iloc[:,2:3]
exchanges = exchanges.sort_values(by='exchange', ascending=True)
exchanges = exchanges.drop_duplicates(subset='exchange', keep="first")
exchanges.reset_index(inplace=True)
exchanges = exchanges.iloc[:,1:2]

#There are certain exchanges we will have to exclude, because they cause problems for this program (e.g. due to missing data). Then reset index again.
exchanges = exchanges.drop(exchanges.index[[0,1,2,3,4,5,6,8,9,10,11,12,16,18,19,20,21]])
exchanges.reset_index(inplace=True)
exchanges = exchanges.iloc[:,1:2]

print("")
print("These are the exchanges:")
print(exchanges)
print("")


#now the user can select an exchange by by entering the name in the list. The programm will then show him the available stocks from this exchange.
chosen_exchange = input("Enter the name of the exchange you want to see in detail (e.g. NYSE): ")

#select only the rows from our DataFrame "symbols" with the exchange which was chosen by the user
chosen_stocks = symbols.loc[symbols['exchange'] == chosen_exchange]

#remove the name of the exchange, sort the stocks in alphabetical order and reset the index
chosen_stocks = chosen_stocks.iloc[:,0:2]
chosen_stocks = chosen_stocks.sort_values(by='name', ascending=True)
chosen_stocks.reset_index(inplace=True)
chosen_stocks = chosen_stocks.iloc[:,1:3]

#we use to_string() to show the entire list and not just the values in the beginning and end
print("")
print("These are the available stocks in", chosen_exchange,":")
print("")
print(chosen_stocks.to_string())


#for the following step we use a loop with try/except in order to make sure that problems with a specific company/company symbol don't let the program crash.
while True:
    try:
        #now the user can choose a company he would like to analyse by entering the symbol
        company = input("Enter the symbol of the company you would like to analyse (e.g. AAPL): ")
        print("")

        
        #in order to being able to change the symbol of a company easily we will define functions which we will refer to when obtaining data of a specific data
        #receiving data which is relevant for calculating the enterprise value of the company
        def enterprisevalues(quote):

            #receive the balance sheet on an annual basis from the API financialmodelingprep
            enterprise_values = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-value/{quote}?apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            enterprise_values = enterprise_values.json()

            #receive the financials data in specific
            enterprise_values = enterprise_values['enterpriseValues']

            #translate the data into a pandas dictionary
            stock = pd.DataFrame.from_dict(enterprise_values)
            stock = stock.T

            #change the naming of the columns to the dates and reset the index
            stock.columns = stock.iloc[0]
            stock.reset_index(inplace=True)

            #select only data from the latest year
            stock = stock.iloc[:,0:2]
            stock = stock.rename(columns={stock.columns[1]:'in million $'})

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            cols = stock.columns.drop('index')
            stock[cols] = stock[cols].apply(pd.to_numeric, errors='coerce')

            #exclude the unnecessary second row which mainly includes NaN's
            stock = stock.iloc[1:,:]
            
            #show the values in million dollars
            stock["in million $"] = stock['in million $']/ 1000000

            return stock
        
        company_ev = enterprisevalues(company)
        
        
        #receiving data about key metrics of the company
        def keymetrics(quote):

            #receive the balance sheet on an annual basis from the API financialmodelingprep
            key_metrics = requests.get(f'https://financialmodelingprep.com/api/v3/company-key-metrics/{quote}?apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            key_metrics = key_metrics.json()

            #receive the financials data in specific
            key_metrics = key_metrics['metrics']

            #translate the data into a pandas dictionary
            stock = pd.DataFrame.from_dict(key_metrics)
            stock = stock.T

            #change the naming of the columns to the dates and reset the index
            stock.columns = stock.iloc[0]
            stock.reset_index(inplace=True)

            #select only data from the latest year
            stock = stock.iloc[:,0:2]
            stock = stock.rename(columns={stock.columns[1]:quote})

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            cols = stock.columns.drop('index')
            stock[cols] = stock[cols].apply(pd.to_numeric, errors='coerce')

            #exclude the unnecessary second row which mainly includes NaN's
            stock = stock.iloc[1:,:]
            
            return stock
        
        company_km = keymetrics(company)
        
        
        #receiving data from the balance sheet
        def balancesheet(quote):

            #receive the balance sheet on an annual basis from the API financialmodelingprep
            annual_balancesheet = requests.get(f'https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/{quote}?apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            annual_balancesheet = annual_balancesheet.json()

            #receive the financials data in specific
            annual_balancesheet = annual_balancesheet['financials']

            #translate the data into a pandas dictionary
            stock = pd.DataFrame.from_dict(annual_balancesheet)
            stock = stock.T

            #change the naming of the columns to the dates and reset the index
            stock.columns = stock.iloc[0]
            stock.reset_index(inplace=True)

            #select only data from the latest year and change the title to "in million $"
            stock = stock.iloc[:,0:2]
            stock = stock.rename(columns={stock.columns[1]:'in million $'})

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            cols = stock.columns.drop('index')
            stock[cols] = stock[cols].apply(pd.to_numeric, errors='coerce')

            #exclude the unnecessary second row which mainly includes NaN's
            stock = stock.iloc[1:,:]

            #show the values in million dollars
            stock["in million $"] = stock['in million $']/ 1000000

            #we want to receive the values as a percentage of total assets
            stock['% of Total Assets'] = stock["in million $"]/ stock.iloc[11,1]
            stock['% of Total Assets'] = pd.Series(["{0:.2f}%".format(val *100) for val in stock['% of Total Assets']], index = stock.index)

            return stock
        
        company_bs = balancesheet(company)
        
        
        #receiving data from the income statement
        def incomestatement(quote):
 
            #receive the income statement on an annual basis from the API financialmodelingprep
            annual_incomestatement = requests.get(f'https://financialmodelingprep.com/api/v3/financials/income-statement/{quote}?apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            annual_incomestatement = annual_incomestatement.json()

            #receive the financials data in specific
            annual_incomestatement = annual_incomestatement['financials']

            #translate the data into a pandas dictionary
            stock = pd.DataFrame.from_dict(annual_incomestatement)
            stock = stock.T

            #change the naming of the columns to the dates and reset the index
            stock.columns = stock.iloc[0]
            stock.reset_index(inplace=True)

            #select only data from the latest year and change the title to "in million $"
            stock = stock.iloc[:,0:2]
            stock = stock.rename(columns={stock.columns[1]:"in million $"})

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            cols = stock.columns.drop('index')
            stock[cols] = stock[cols].apply(pd.to_numeric, errors='coerce')

            #replace the unnecessary second row which mainly includes NaN's
            stock = stock.iloc[1:,:]

            #show the values in million dollars
            stock["in million $"] = stock["in million $"]/ 1000000

            #we want to receive the values as a percentage of total revenues
            stock['% of Total Revenues'] = stock["in million $"]/ stock.iloc[0,1]
            stock['% of Total Revenues'] = pd.Series(["{0:.2f}%".format(val *100) for val in stock['% of Total Revenues']], index = stock.index)

            return stock
        
        company_is = incomestatement(company)

        
        #receiving data from the cash flow statement
        def cashflowstatement(quote):
 
            #receive the cash flow statement on an annual basis from the API financialmodelingprep
            annual_cashflowstatement = requests.get(f'https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/{quote}?apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            annual_cashflowstatement = annual_cashflowstatement.json()

            #receive the financials data in specific
            annual_cashflowstatement = annual_cashflowstatement['financials']

            #translate the data into a pandas dictionary
            stock = pd.DataFrame.from_dict(annual_cashflowstatement)
            stock = stock.T

            #change the naming of the columns to the dates and reset the index
            stock.columns = stock.iloc[0]
            stock.reset_index(inplace=True)

            #select only data from the latest year and change the title to "in million $"
            stock = stock.iloc[:,0:2]
            stock = stock.rename(columns={stock.columns[1]:"in million $"})

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            cols = stock.columns.drop('index')
            stock[cols] = stock[cols].apply(pd.to_numeric, errors='coerce')

            #exclude the unnecessary second row which mainly includes NaN's
            stock = stock.iloc[1:,:]

            #show the values in million dollars
            stock["in million $"] = stock["in million $"]/ 1000000

            return stock
        
        company_cf = cashflowstatement(company)
        

        #receiving data about the historic price as well as the DCF value
        def historicprices(quote):
 
            #receive information about stock price and DCF value on a quarterly basis from the API financialmodelingprep. Also get today's values.
            annual_historicprices = requests.get(f'https://financialmodelingprep.com/api/v3/company/historical-discounted-cash-flow/{quote}?period=quarter&apikey={API_Key}')

            #translate the data into a dictionary in order to make it easily accessible
            annual_historicprices = annual_historicprices.json()

            #receive the historicalDCF data in specific
            annual_historicprices = annual_historicprices["historicalDCF"]

            #translate the data into pandas dictionaries
            stock = pd.DataFrame.from_dict(annual_historicprices)

            #as the index is from the most recent date we make the first entry the oldest date.
            stock = stock.sort_index(ascending = False)

            #reset the index
            stock.reset_index(inplace=True)

            #exclude the unnecessary first column
            stock = stock.iloc[:,1:]

            #in order to be able to make operations we select the columns which include numbers as values and then convert their type from objects to numbers
            stock[['Stock Price', 'DCF']] = stock[['Stock Price', 'DCF']].apply(pd.to_numeric, errors='coerce')

            # Plot the two prices to find potential differences between intrinsic value and market price.
            visual = stock.plot(x='date', figsize=(13.5, 9))
            visual = plt.plot('Stock Price', data=stock, marker='', color='skyblue', linewidth=2)
            visual = plt.plot('DCF', data=stock, marker='', color='orange', linewidth=2)

            return visual
        
        company_hp = historicprices(company)
        

        #receive the current stock price
        def stockprice(quote):

            r = requests.get(f'https://financialmodelingprep.com/api/v3/stock/real-time-price/{quote}?apikey={API_Key}')
            r = r.json()
            r = r['price']
            return r

        company_rsp = stockprice(company)

        #isolate the Market Capitalisation from 2019
        MarketCap = company_km.iat[9,1]
        MarketCap = MarketCap/1000000
        MarketCap = round(MarketCap, 1)
        MarketCap = (str(MarketCap) + " mil. $")
        
        #isolate the Price to Earnings Ratio from 2019
        PriceEarnings = company_km.iat[11,1]
        PriceEarnings = round(PriceEarnings, 2)
        PriceEarnings = (str(PriceEarnings) + "x")
        
        #isolate the Dividend Yield from 2019
        DividendYield = company_km.iat[29,1]
        DividendYield = DividendYield*100
        DividendYield = round(DividendYield, 2)
        DividendYield = (str(DividendYield) + "%")
        
        #isolate the Net Profit Margin from 2019
        NetProfitMargin = company_is.iat[30,1]
        NetProfitMargin = NetProfitMargin*1000000
        NetProfitMargin = NetProfitMargin*100
        NetProfitMargin = round(NetProfitMargin, 2)
        NetProfitMargin = (str(NetProfitMargin) + "%")
        
        #isolate the Current Ratio from 2019
        CurrentRatio = company_km.iat[26,1]
        CurrentRatio = round(CurrentRatio, 2)
        CurrentRatio = (str(CurrentRatio) + "x")
        
        #isolate Return on Equity from 2019
        ROE = company_km.iat[55,1]
        ROE = ROE*100
        ROE = round(ROE, 2)
        ROE = (str(ROE) + "%")


        #we want to first show the main information about the stock in a window. Therefore we show some values in a pop-up window.
        #creating the window
        my_window = Tk()
        frame_name = Frame(my_window)

        #defining which content is placed in the window
        company_text = Label(frame_name , text = "Company symbol:")
        company_name = Label(frame_name , text = company)
        
        
        stock_text = Label(frame_name , text = "Current price:")
        stock_name = Label(frame_name , text = company_rsp)
        
        MarketCap_text = Label(frame_name , text = "Market Capitalization (2019):")
        MarketCap_value = Label(frame_name , text = MarketCap)
        
        PriceEarnings_text = Label(frame_name , text = "Price Earnings (2019):")
        PriceEarnings_value = Label(frame_name , text = PriceEarnings)
        
        DividendYield_text = Label(frame_name , text = "Dividend Yield (2019):")
        DividendYield_value = Label(frame_name , text = DividendYield)
        
        NetProfitMargin_text = Label(frame_name , text = "Net Profit Margin (2019):")
        NetProfitMargin_value = Label(frame_name , text = NetProfitMargin)
        
        CurrentRatio_text = Label(frame_name , text = "Current Ratio (2019):")
        CurrentRatio_value = Label(frame_name , text = CurrentRatio)
        
        ROE_text = Label(frame_name , text = "ROE (2019):")
        ROE_value = Label(frame_name , text = ROE)
        
        next_button = Button(frame_name , text = "show more details", command = my_window.destroy)

        #defining where the content is shown in the window
        company_text.grid(row=0, column=0)
        company_name.grid(row=0, column=1)
        
        stock_text.grid(row=1, column=0)
        stock_name.grid(row=1, column=1)
        
        MarketCap_text.grid(row=2, column=0)
        MarketCap_value.grid(row=2, column=1)
        
        PriceEarnings_text.grid(row=3, column=0)
        PriceEarnings_value.grid(row=3, column=1)
        
        DividendYield_text.grid(row=4, column=0)
        DividendYield_value.grid(row=4, column=1)
        
        NetProfitMargin_text.grid(row=5, column=0)
        NetProfitMargin_value.grid(row=5, column=1)
        
        CurrentRatio_text.grid(row=6, column=0)
        CurrentRatio_value.grid(row=6, column=1)
        
        ROE_text.grid(row=7, column=0)
        ROE_value.grid(row=7, column=1)
        
        next_button.grid(row=8, columnspan=2)

        #showing the frame, and changing the title
        frame_name.grid(row=0, column=0)
        my_window.title('Company Overview')
        my_window.mainloop()



        #now we print all the predetermined output
        
        print("")
        print(company, "Balance Sheet 2019")
        print(company_bs)

        
        print("")
        print(company, "Income Statement 2019")
        print(company_is)

        
        print("")
        print(company, "Cash Flow Statement 2019")
        print(company_cf)

        
        print("")
        print(company, "Enterprise Values 2019")
        print(company_ev)
        
        
        print("")
        print(company, "Key Metrics 2019")
        print(company_km) 
        
        
        print("")
        print(company, "Historic Prices & DCF Values in $")

        break
    
    except:
        print("This symbol is not compatible with this program. Please try another symbol...")


# In[ ]:





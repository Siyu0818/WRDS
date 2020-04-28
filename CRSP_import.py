def PS1_Q1():
    crsp_stocks = pd.read_csv('Monthly_CRSP_Stocks.csv')
    # improve input data quality
    crsp_stocks['DLRET'].fillna(0, inplace=True)
    crsp_stocks['RET'].fillna(0, inplace=True)
    crsp_stocks = crsp_stocks[crsp_stocks['EXCHCD'].notna()]
    crsp_stocks['Year'] = (crsp_stocks['date']/10000).astype(int)
    crsp_stocks['Month'] = ((crsp_stocks['date'] - crsp_stocks['Year']*10000)/100).astype(int)
    crsp_stocks.drop(columns = ['date'], inplace=True)
    crsp_stocks = crsp_stocks[(crsp_stocks['EXCHCD'] == 1)|(crsp_stocks['EXCHCD'] == 2)|(crsp_stocks['EXCHCD'] == 3)]
    crsp_stocks = crsp_stocks[(crsp_stocks['SHRCD'] == 10)|(crsp_stocks['SHRCD'] == 11)]
    crsp_stocks['PRC'] = crsp_stocks['PRC'].abs()

    # replace the ipo day holding period return from 'C' to 0
    crsp_stocks.loc[(crsp_stocks.RET == 'C'),'RET'] = 0

    # fill delist price with the last price before delist
    crsp_stocks.ffill(inplace=True)

    # replace delist price 'A' to 0
    crsp_stocks.loc[(crsp_stocks.DLRET == 'A')|(crsp_stocks.DLRET == 'S')|(crsp_stocks.DLRET == 'T')\
                    |(crsp_stocks.DLRET == 'P'),'DLRET'] = 0

    crsp_stocks = crsp_stocks.set_index('PERMNO').reset_index()

    crsp_stocks = crsp_stocks.drop(columns=['PERMCO'])

    crsp_stocks['DLRET'] = crsp_stocks['DLRET'].astype(float)
    crsp_stocks['RET'] = crsp_stocks['RET'].astype(float)

    # cum_dividend total returns
    crsp_stocks['CUMRET'] = (crsp_stocks['DLRET']+1)*(crsp_stocks['RET']+1) - 1

    # market caps
    crsp_stocks['MKTCAP'] = crsp_stocks['PRC']*crsp_stocks['SHROUT']
    crsp_stocks['MKTCAP'] = crsp_stocks.groupby('PERMNO')['MKTCAP'].shift(1)
    crsp_stocks.dropna(inplace=True)

    # total market caps
    crsp_stocks.set_index(['Year', 'Month'], inplace = True)
    crsp_stocks['TMKTCAP'] = crsp_stocks.groupby(['Year', 'Month'])['MKTCAP'].sum()

    # market portfolio weights
    crsp_stocks['MPW'] = crsp_stocks['MKTCAP'] / crsp_stocks['TMKTCAP']

    # weight_return
    crsp_stocks['WRET'] = crsp_stocks['MPW'] * crsp_stocks['CUMRET']

    # crsp stocks output
    crsp_stocks_output = pd.DataFrame(crsp_stocks.groupby(level=['Year','Month'])['MKTCAP'].sum())
    crsp_stocks_output['Stock_Ew_Ret'] = crsp_stocks.groupby(level=['Year','Month'])['CUMRET'].mean()
    crsp_stocks_output['Stock_Vw_Ret'] = crsp_stocks.groupby(level=['Year','Month'])['WRET'].sum()
    crsp_stocks_output = crsp_stocks_output.rename(columns={'MKTCAP':'Stock_lag_MV'})

    return crsp_stocks_output

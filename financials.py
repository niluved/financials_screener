import yfinance as yf
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


# Lista dei ticker che vuoi analizzare
tickers = ['A2A.MI',
           'AMP.MI',
           'AZM.MI',
           'BGN.MI',
           'BMED.MI',
           'BAMI.MI',
           'BPE.MI',
           'BZU.MI',
           'CPR.MI',
           'DIA.MI',
           'ENEL.MI',
           'ENI.MI',
           'ERG.MI',
           'RACE.MI',
           'FBK.MI',
           'G.MI',
           'HER.MI',
           'IP.MI',
           'ISP.MI',
           'INW.MI',
           'IG.MI',
           'IVG.MI',
           'LDO.MI',
           'MB.MI',
           'MONC.MI',
           'NEXI.MI',
           'PIRC.MI',
           'PST.MI',
           'PRY.MI',
           'REC.MI',
           'SPM.MI',
           'SRG.MI',
           'STLAM.MI',
           'STMMI.MI',
           'TIT.MI',
           'TEN.MI',
           'TRN.MI',
           'UCG.MI',
           'UNI.MI',
           ]


def load_or_download_data(tickers, filename='financial_data.csv'):
    if os.path.exists(filename):
        while True:
            choice = input(
                f"Il file {filename} esiste già. Vuoi usare i dati esistenti (E) o scaricare nuovi dati (N)? ").lower()
            if choice in ['e', 'n']:
                break
            print("Scelta non valida. Per favore, inserisci 'E' per usare i dati esistenti o 'N' per scaricare nuovi dati.")

        if choice == 'e':
            print(f"Caricamento dei dati dal file {filename}...")
            return pd.read_csv(filename)

    print("Scaricamento di nuovi dati...")
    all_data = []
    for ticker in tickers:
        try:
            data = get_financial_data(ticker)
            all_data.append(data)
        except Exception as e:
            print(f"Errore nell'ottenere i dati per {ticker}: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv(filename, index=False)
    print(f"I nuovi dati sono stati salvati in {filename}")
    return df


def get_financial_data(ticker):
    # Scarica i dati per il ticker specificato
    stock = yf.Ticker(ticker)

    # Ottieni i dati del bilancio e del conto economico
    balance_sheet = stock.balance_sheet
    income_statement = stock.income_stmt

    # Ottieni i dati finanziari chiave e le previsioni degli analisti
    info = stock.info

    # Estrai i dati rilevanti
    total_assets = balance_sheet.loc['Total Assets'].values[0]
    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].values[0]
    equity = balance_sheet.loc['Total Equity Gross Minority Interest'].values[0]

    ebit = income_statement.loc['EBIT'].values[0]
    net_income = income_statement.loc['Net Income'].values[0]

    # Calcola i debiti finanziari (una stima semplificata)
    financial_debt = total_liabilities - \
        (balance_sheet.loc['Accounts Payable'].values[0]
         if 'Accounts Payable' in balance_sheet.index else 0)

    # Calcola ROA_adj
    cash_and_equivalents = balance_sheet.loc['Cash And Cash Equivalents'].values[0]
    roa_adj = net_income / (total_assets - cash_and_equivalents)

    # Calcola EbitPriceRatio
    market_cap = info.get('marketCap', None)
    ebit_price_ratio = ebit / market_cap if market_cap else None

    # Crea un dizionario con i dati
    data = {
        'Ticker': ticker,
        'Total Assets': total_assets,
        'Equity': equity,
        'EBIT': ebit,
        'Net Income': net_income,
        'Financial Debt': financial_debt,
        'ROE': info.get('returnOnEquity', None),
        'ROA': info.get('returnOnAssets', None),
        'ROA_adj': roa_adj,
        'EbitPriceRatio': ebit_price_ratio,
        'EPS': info.get('trailingEps', None),
        'P/E Ratio': info.get('trailingPE', None),
        'Dividend Yield': info.get('dividendYield', None),
        'Market Cap': market_cap,
        'Beta': info.get('beta', None),
        'Price to Book': info.get('priceToBook', None),
        'Debt to Equity': info.get('debtToEquity', None),
        'Free Cash Flow': info.get('freeCashflow', None),
        'Revenue Growth': info.get('revenueGrowth', None),
        'Gross Margins': info.get('grossMargins', None),
        'Operating Margins': info.get('operatingMargins', None),
        'Profit Margins': info.get('profitMargins', None),

        # Previsioni di consensus
        'Forward P/E': info.get('forwardPE', None),
        'Forward EPS': info.get('forwardEps', None),
        'EPS Estimate Current Year': info.get('epsCurrentYear', None),
        'EPS Estimate Next Year': info.get('epsNextYear', None),
        'EPS Estimate Next Quarter': info.get('epsNextQuarter', None),
        'Revenue Estimate Current Year': info.get('revenueEstimate', None),
        'Revenue Estimate Next Year': info.get('revenueEstimateNextYear', None),
        'Growth Estimate Current Year': info.get('earningsGrowth', None),
        'Growth Estimate Next Year': info.get('earningsQuarterlyGrowth', None),
        'Long-term Growth Rate': info.get('longTermGrowthRate', None),
        'Number of Analysts': info.get('numberOfAnalystOpinions', None),
        'Recommendation Mean': info.get('recommendationMean', None),
    }

    return data


def create_scatter_plot(df, x_indicator, y_indicator):
    plt.figure(figsize=(12, 8))
    plt.scatter(df[x_indicator], df[y_indicator], alpha=0.5)

    for i, ticker in enumerate(df['Ticker']):
        plt.annotate(ticker, (df[x_indicator].iloc[i],
                     df[y_indicator].iloc[i]))

    plt.xlabel(x_indicator)
    plt.ylabel(y_indicator)
    plt.title(f'{x_indicator} vs {y_indicator}')

    '''
    # Aggiunge una linea di regressione
    z = np.polyfit(df[x_indicator], df[y_indicator], 1)
    p = np.poly1d(z)
    plt.plot(df[x_indicator], p(df[x_indicator]), "r--", alpha=0.8)

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    '''

    # Salva il grafico come immagine
    filename = f'{x_indicator.lower().replace(" ", "_")}_vs_{y_indicator.lower().replace(" ", "_")}.png'
    plt.savefig(filename)
    print(f"Il grafico è stato salvato come '{filename}'")

    plt.show()


# Carica o scarica i dati
df = load_or_download_data(tickers)

# Ora puoi lavorare con il DataFrame 'df' che contiene i dati finanziari
print(df.head())

'''
# Esempio di alcune analisi che potresti voler fare:
print("\nStatistiche descrittive:")
print(df.describe())

print("\nMedia degli indicatori principali:")
print(df[['ROA_adj', 'EbitPriceRatio', 'P/E Ratio', 'Debt to Equity']].mean())

print("\nAziende con il miglior ROA_adj:")
print(df.sort_values('ROA_adj', ascending=False)[['Ticker', 'ROA_adj']].head())

print("\nAziende con il miglior EbitPriceRatio:")
print(df.sort_values('EbitPriceRatio', ascending=False)
      [['Ticker', 'EbitPriceRatio']].head())
'''


# Funzione per chiedere all'utente di scegliere un indicatore
def choose_indicator(prompt):
    print("\nIndicatori disponibili:")
    for i, col in enumerate(df.columns[1:], 1):  # Esclude 'Ticker'
        print(f"{i}. {col}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(df.columns) - 1:
                return df.columns[choice]
            else:
                print("Scelta non valida. Riprova.")
        except ValueError:
            print("Per favore, inserisci un numero.")


# Chiedi all'utente di scegliere gli indicatori per lo scatter plot
x_indicator = choose_indicator(
    "Scegli il numero dell'indicatore per l'asse X: ")
y_indicator = choose_indicator(
    "Scegli il numero dell'indicatore per l'asse Y: ")

# Crea e mostra lo scatter plot
create_scatter_plot(df, x_indicator, y_indicator)

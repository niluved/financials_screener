import yfinance as yf
import pandas as pd


def get_financial_data(ticker, start_date, end_date):
    # Scarica i dati per il ticker specificato
    stock = yf.Ticker(ticker)

    # Ottieni i dati del bilancio e del conto economico
    balance_sheet = stock.balance_sheet
    income_statement = stock.income_stmt

    # Estrai i dati rilevanti
    total_assets = balance_sheet.loc['Total Assets'].values[0]
    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].values[0]
    equity = balance_sheet.loc['Total Equity Gross Minority Interest'].values[0]

    ebit = income_statement.loc['EBIT'].values[0]
    net_income = income_statement.loc['Net Income'].values[0]

    # Dati aggiuntivi per i nuovi indici
    intangible_assets = balance_sheet.loc['Intangible Assets'].values[
        0] if 'Intangible Assets' in balance_sheet.index else 0
    cash = balance_sheet.loc['Cash And Cash Equivalents'].values[0]
    accounts_payable = balance_sheet.loc['Accounts Payable'].values[
        0] if 'Accounts Payable' in balance_sheet.index else 0

    # Calcola i debiti finanziari (una stima semplificata)
    financial_debt = total_liabilities - accounts_payable

    # Ottieni la capitalizzazione di mercato
    market_cap = stock.info['marketCap']

    # Calcola ROA
    roa_denominator = total_assets - intangible_assets - cash - accounts_payable
    roa = ebit / roa_denominator if roa_denominator != 0 else None

    # Calcola EbitPriceRatio
    ebit_price_ratio_denominator = market_cap + financial_debt
    ebit_price_ratio = ebit / \
        ebit_price_ratio_denominator if ebit_price_ratio_denominator != 0 else None

    # Crea un dizionario con i dati
    data = {
        'Ticker': ticker,
        'Total Assets': total_assets,
        'Equity': equity,
        'EBIT': ebit,
        'Net Income': net_income,
        'Financial Debt': financial_debt,
        'ROA': roa,
        'EbitPriceRatio': ebit_price_ratio
    }

    return data


# Lista dei ticker che vuoi analizzare
tickers = ['AMZN']  # Esempio con alcune grandi aziende tech

# Periodo di tempo per i dati
start_date = '2022-01-01'
end_date = '2023-12-31'

# Crea una lista per contenere i dati di tutti i ticker
all_data = []

# Itera attraverso i ticker e ottieni i dati
for ticker in tickers:
    try:
        data = get_financial_data(ticker, start_date, end_date)
        all_data.append(data)
    except Exception as e:
        print(f"Errore nell'ottenere i dati per {ticker}: {e}")

# Crea un DataFrame con tutti i dati
df = pd.DataFrame(all_data)

# Salva il DataFrame in un file CSV
df.to_csv('financial_data.csv', index=False)

print("I dati finanziari sono stati salvati in 'financial_data.csv'")

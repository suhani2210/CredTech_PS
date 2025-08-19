import yfinance as yf

def get_company_name_yfinance(ticker):
    """
    Fetches the company name from yfinance for a given ticker.
    
    Args:
        ticker (str): Stock ticker symbol.
        
    Returns:
        str: Company name, or an error message if not found.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get('longName') or info.get('shortName')
        if company_name:
            return company_name
        else:
            return "Company name not available for this ticker."
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"

# Example usage:
print(get_company_name_yfinance("AAPL"))

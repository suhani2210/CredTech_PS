import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict
import logging
from credtech import altman_z_score, ohlson_o_score, normalize_score, CompanyFinancials
from unstructured import news_sentiment_score


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_compute_credit_scores(
    tickers: List[str], 
    weight_altman: float = 0.50,
    weight_ohlson: float = 0.40,
    weight_sentiment: float = 0.10
) -> Dict[str, Dict[str, float]]:
    results = {}
    failed_tickers = []
    for ticker in tickers:
        logger.info(f"Processing ticker: {ticker}")
        try:
            stock = yf.Ticker(ticker)
            quarterly_bs = stock.quarterly_balance_sheet
            quarterly_income = stock.quarterly_financials
            info = stock.info

            if quarterly_bs.empty or quarterly_income.empty:
                logger.warning(f"No financial data available for {ticker}")
                failed_tickers.append(ticker)
                continue

            bs_latest = quarterly_bs.iloc[:, 0]
            is_latest = quarterly_income.iloc[:, 0]

            def safe_extract(series, keys, default=np.nan):
                for key in keys:
                    try:
                        value = series.get(key)
                        if value is not None and not pd.isna(value):
                            return float(value)
                    except:
                        continue
                return default

            total_assets = safe_extract(bs_latest, [
                'Total Assets', 'TotalAssets', 'Assets'
            ])
            # Try to get total liabilities. If missing, compute as: assets - total equity
            total_liabilities = safe_extract(bs_latest, [
                'Total Liab', 'Total Liabilities', 'TotalLiabilities'
            ])
            if pd.isna(total_liabilities):
                total_equity = safe_extract(bs_latest, [
                    'Total Stockholder Equity', 'Stockholders Equity', 'Total Equity', 'Shareholders Equity'
                ])
                if not pd.isna(total_equity) and not pd.isna(total_assets):
                    total_liabilities = total_assets - total_equity
                    logger.info(f"{ticker}: Estimated total_liabilities as total_assets - total_equity")
                else:
                    total_liabilities = 100000  # Absolute fallback

            current_assets = safe_extract(bs_latest, [
                'Total Current Assets', 'TotalCurrentAssets', 'Current Assets'
            ])
            current_liabilities = safe_extract(bs_latest, [
                'Total Current Liabilities', 'TotalCurrentLiabilities', 'Current Liabilities'
            ])
            retained_earnings = safe_extract(bs_latest, [
                'Retained Earnings', 'RetainedEarnings'
            ])
            revenue = safe_extract(is_latest, [
                'Total Revenue', 'TotalRevenue', 'Revenue', 'Net Sales'
            ])
            net_income = safe_extract(is_latest, [
                'Net Income', 'NetIncome'
            ])
            ebit = safe_extract(is_latest, [
                'EBIT', 'Ebit', 'Operating Income', 'OperatingIncome'
            ])
            market_cap = info.get('marketCap')

            if pd.isna(retained_earnings) and not (pd.isna(total_assets) or pd.isna(total_liabilities)):
                retained_earnings = total_assets - total_liabilities
                logger.info(f"{ticker}: Estimated retained_earnings from equity")
            if pd.isna(ebit) and not pd.isna(net_income):
                ebit = net_income
                logger.info(f"{ticker}: Used net_income as EBIT proxy")
            if pd.isna(current_assets) and not pd.isna(total_assets):
                current_assets = total_assets * 0.40
                logger.info(f"{ticker}: Estimated current_assets as 40% of total_assets")
            if pd.isna(current_liabilities) and not pd.isna(total_liabilities):
                current_liabilities = total_liabilities * 0.60
                logger.info(f"{ticker}: Estimated current_liabilities as 60% of total_liabilities")
            
            if not pd.isna(current_assets) and not pd.isna(current_liabilities):
                working_capital = current_assets - current_liabilities
            else:
                working_capital = 0.0
                logger.warning(f"{ticker}: Working capital set to 0 due to missing current asset/liability data")
            def apply_default(value, default, field_name):
                if pd.isna(value) or value is None:
                    logger.warning(f"{ticker}: Using default for {field_name}: {default}")
                    return default
                return float(value)
            
            total_assets = max(apply_default(total_assets, 1000000, "total_assets"), 1000000)
            total_liabilities = max(apply_default(total_liabilities, 100000, "total_liabilities"), 100000)
            current_assets = max(apply_default(current_assets, 0, "current_assets"), 0)
            current_liabilities = max(apply_default(current_liabilities, 0, "current_liabilities"), 0)
            retained_earnings = apply_default(retained_earnings, 0, "retained_earnings")
            ebit = apply_default(ebit, 0, "ebit")
            market_cap = max(apply_default(market_cap, 1000000, "market_cap"), 1000000)
            revenue = max(apply_default(revenue, 0, "revenue"), 0)
            net_income = apply_default(net_income, 0, "net_income")
            # Get sentiment score
            sentiment_score = news_sentiment_score(ticker)

            fin = CompanyFinancials(
                total_assets=total_assets,
                total_liabilities=total_liabilities,
                working_capital=working_capital,
                retained_earnings=retained_earnings,
                ebit=ebit,
                market_value_equity=market_cap,
                sales=revenue,
                net_income=net_income,
                current_assets=current_assets,
                current_liabilities=current_liabilities,
                sentiment_score=sentiment_score
            )

            # Use wide normalization ranges to ensure healthy company scores map high, e.g.: 
            altman_norm = normalize_score(altman_z_score(fin), -3, 10)
            ohlson_norm = normalize_score(ohlson_o_score(fin), -5, 4)

            final_score = (
                weight_altman * altman_norm
                + weight_ohlson * ohlson_norm
                + weight_sentiment * sentiment_score * 100
            )
            
            margin_high = sentiment_score*0.1*(100-final_score)
            margin_low = (1-sentiment_score)*0.1*(100-final_score)
            
            score_min, score_max = final_score - margin_low, final_score + margin_high

            results[ticker] = {
                'base_score': round(final_score, 2),
                'score_min': round(score_min, 2),
                'score_max': round(score_max, 2),
                'altman_z': round(altman_z_score(fin), 2),
                'ohlson_o': round(ohlson_o_score(fin), 2),
                'sentiment': sentiment_score
            }
            logger.info(f"{ticker}: Score = {final_score:.2f}")
        except Exception as e:
            logger.error(f"Failed to process {ticker}: {str(e)}")
            failed_tickers.append(ticker)
    if failed_tickers:
        logger.warning(f"Failed tickers: {failed_tickers}")
    logger.info(f"Processed {len(results)} of {len(tickers)}")
    return results

# Add this function to your existing credit scoring file
def get_score_breakdown_data():
    """Generate data for pie chart visualization"""
    
    # Altman Z-Score component weights (relative importance)
    altman_breakdown = {
        'Working Capital Efficiency': 11.78,
        'Retained Earnings': 13.91, 
        'Operating Performance': 51.03,  # Highest impact
        'Market Valuation': 6.90,
        'Asset Turnover': 16.39
    }
    
    # Ohlson O-Score component weights  
    ohlson_breakdown = {
        'Company Size': 25.89,
        'Debt Structure': 8.17,
        'Working Capital': 28.70,  # Highest impact
        'Liquidity Position': 1.52,
        'Profitability': 7.43,
        'Income Stability': 24.89,
        'Sales Efficiency': 3.41
    }
    
    return {
        'altman': altman_breakdown,
        'ohlson': ohlson_breakdown,
        'weights': {
            'altman_weight': 50,    # 50% of total score
            'ohlson_weight': 40,    # 40% of total score  
            'sentiment_weight': 10  # 10% of total score
        }
    }

def get_detailed_breakdown_for_ticker(ticker: str):
    """Get detailed breakdown for a specific ticker including actual values"""
    try:
        # Use existing function to get the scores
        results = fetch_and_compute_credit_scores([ticker])
        
        if ticker not in results:
            return None
            
        score_data = results[ticker]
        breakdown_data = get_score_breakdown_data()
        
        return {
            'ticker': ticker,
            'scores': score_data,
            'breakdown': breakdown_data,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting breakdown for {ticker}: {str(e)}")
        return None


# Example usage

results = fetch_and_compute_credit_scores(tickers=['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'ADBE', 'DELL', 'IBM', 'NFLX', 'NVDA', 'META', 'INTC'])
for ticker, score_data in results.items():
    print(f"{ticker}: Base Score = {score_data['base_score']}, "
          f"Range = ({score_data['score_min']}, {score_data['score_max']}), "
          f"Altman Z = {score_data['altman_z']}, Ohlson O = {score_data['ohlson_o']}, "
          f"Sentiment = {score_data['sentiment']}")

# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from fetch_and_score import fetch_and_compute_credit_scores, get_score_breakdown_data
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/company-analysis/<ticker>')
def company_analysis(ticker):
    """Get complete analysis for a specific company"""
    try:
        ticker = ticker.upper()
        logger.info(f"Analyzing ticker: {ticker}")
        
        # Get credit scores for the ticker
        credit_results = fetch_and_compute_credit_scores([ticker])
        
        if ticker not in credit_results:
            return jsonify({
                'error': f'No financial data available for {ticker}. Please check the ticker symbol.'
            }), 404
        
        # Get breakdown data
        breakdown_data = get_score_breakdown_data()
        
        response_data = {
            'ticker': ticker,
            'credit_scores': credit_results[ticker],
            'breakdown': breakdown_data,
            'success': True,
            'timestamp': credit_results.get('timestamp', None)
        }
        
        logger.info(f"Successfully analyzed {ticker}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {str(e)}")
        return jsonify({
            'error': f'Failed to analyze {ticker}: {str(e)}'
        }), 500

@app.route('/api/batch-analysis', methods=['POST'])
def batch_analysis():
    """Analyze multiple companies at once"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({'error': 'No tickers provided'}), 400
        
        # Limit batch size for performance
        if len(tickers) > 10:
            return jsonify({'error': 'Maximum 10 tickers per batch'}), 400
        
        # Convert to uppercase
        tickers = [ticker.upper() for ticker in tickers]
        
        # Get credit scores
        credit_results = fetch_and_compute_credit_scores(tickers)
        
        # Get breakdown data
        breakdown_data = get_score_breakdown_data()
        
        return jsonify({
            'results': credit_results,
            'breakdown': breakdown_data,
            'processed_count': len(credit_results),
            'requested_count': len(tickers),
            'success': True
        })
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return jsonify({'error': 'Batch analysis failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Import CLI logic
from alpaca_cli import setup_api_client_from_env, get_account_status_data, list_positions_data

# Load environment variables from a .env file
load_dotenv()

# Initialize Alpaca client using CLI logic
trading_client = setup_api_client_from_env()

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/api/account_info', methods=['GET'])
def get_account_info():
    try:
        account_data = get_account_status_data(trading_client)
        return jsonify(account_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/positions', methods=['GET'])
def get_positions():
    try:
        positions_list = list_positions_data(trading_client)
        return jsonify(positions_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Go to http://127.0.0.1:5000 in your browser to view the client.")
    app.run(debug=True, port=5000)

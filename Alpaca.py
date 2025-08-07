# Alpaca.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from alpaca_cli import setup_api_client, get_account_status_data, list_positions_data

# --- Flask App Setup ---
app = Flask(__name__, static_folder='.')
CORS(app) # Enable CORS for development

# Set up the API client once when the server starts
api = setup_api_client()

# --- Routes ---

@app.route('/')
def serve_index():
    """Serves the index.html file from the same directory."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/account_info', methods=['GET'])
def get_account_info():
    """
    Fetches account info using the refactored function and returns it as JSON.
    """
    data = get_account_status_data(api)
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data), 200

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """
    Fetches all positions using the refactored function and returns them as JSON.
    """
    data = list_positions_data(api)
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data), 200

@app.route('/api/screen_stocks', methods=['GET'])
def get_screen_stocks():
    """
    A placeholder for a stock screening endpoint.
    """
    # This is a placeholder; you would add your stock screening logic here.
    return jsonify({"stocks": []}), 200

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Go to http://127.0.0.1:5000 in your browser to view the client.")
    app.run(debug=True, port=5000)